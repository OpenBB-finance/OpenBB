"""Convert OpenAPI JSON-schema fragments into Pydantic class source code.

The converter is the foundation of the spec-to-extension pipeline: every
``QueryParams`` / ``Data`` class in the generated extension is produced by
``generate_class``. Schemas come from the spec's already-dereferenced response
/ request body (cycle markers as ``{"$ref": ref}`` are tolerated and collapse
to ``dict[str, Any]``).

Output is plain Python source text — easy to inspect, easy to format with
``ruff format``, no AST acrobatics.
"""

from __future__ import annotations

import keyword
import re
from dataclasses import dataclass, field
from typing import Any

# JSON-schema primitive type → Python type annotation
_PRIMITIVE_TYPES: dict[str, str] = {
    "string": "str",
    "integer": "int",
    "number": "float",
    "boolean": "bool",
}

# String formats that map to richer Python types. The annotations use the
# fully-qualified ``datetime.<X>`` form so a field literally named ``date``
# (very common in time-series schemas) doesn't shadow the type binding.
_STRING_FORMATS: dict[str, str] = {
    "date": "datetime.date",
    "date-time": "datetime.datetime",
}

_PYTHON_RESERVED_FIELD_NAMES = frozenset(
    {"model_config", "model_fields", "model_dump", "model_validate"}
)


@dataclass
class GeneratedClass:
    """One emitted Pydantic class plus any nested classes it depends on.

    ``nested`` holds peer classes that must be defined *before* this class so
    forward references resolve at import time. The codegen pipeline flattens
    a class tree by walking ``nested`` depth-first and emitting each entry's
    ``source`` in order, then the parent's ``source`` last.
    """

    name: str
    source: str
    nested: list[GeneratedClass] = field(default_factory=list)
    imports: set[str] = field(default_factory=set)

    def flatten(self) -> list[GeneratedClass]:
        """Return ``[nested..., self]`` in topological order, deduped by name."""
        seen: set[str] = set()
        out: list[GeneratedClass] = []
        for child in self.nested:
            for grandchild in child.flatten():
                if grandchild.name not in seen:
                    seen.add(grandchild.name)
                    out.append(grandchild)
        if self.name not in seen:
            out.append(self)
        return out

    def collect_imports(self) -> set[str]:
        """Union of ``imports`` across this class and every descendant."""
        out = set(self.imports)
        for child in self.nested:
            out.update(child.collect_imports())
        return out


def safe_field_name(name: str) -> tuple[str, bool]:
    """Normalize a JSON property name to a valid Python identifier.

    Returns ``(safe_name, needs_alias)``. When ``needs_alias`` is ``True``
    the caller must emit ``alias="<original>"`` on the ``Field(...)`` so
    the on-the-wire name still round-trips. Triggers on names that aren't
    valid identifiers, collide with Python keywords, or shadow Pydantic's
    reserved attribute names.

    Leading underscores get stripped because Pydantic v2 refuses to
    declare them as model fields ("Fields must not use names with leading
    underscores"). Names that would otherwise start with a digit get an
    ``f_`` prefix instead of ``_`` so the result stays acceptable to
    Pydantic — Socrata's ``$select`` becomes ``select`` (alias ``$select``),
    not ``_select``.
    """
    cleaned = re.sub(r"[^0-9a-zA-Z_]", "_", name).lstrip("_")
    if not cleaned:
        cleaned = "field"
    if cleaned[0].isdigit():
        cleaned = f"f_{cleaned}"
    if keyword.iskeyword(cleaned) or cleaned in _PYTHON_RESERVED_FIELD_NAMES:
        cleaned = f"{cleaned}_"
    return (cleaned, cleaned != name)


def class_name_from(*parts: str) -> str:
    """Join + camel-case a set of name parts into a Python class identifier.

    ``("equity", "price.quote", "Data")`` → ``"EquityPriceQuoteData"``. Non-
    alphanumeric characters split words; the first letter is upper-cased.
    Empty / falsy parts are dropped.
    """
    words: list[str] = []
    for part in parts:
        if not part:
            continue
        for word in re.split(r"[^0-9a-zA-Z]+", part):
            if word:
                words.append(word[:1].upper() + word[1:])
    name = "".join(words) or "Anonymous"
    if name[0].isdigit():
        name = f"_{name}"
    return name


def schema_to_type(  # noqa: PLR0911 — dispatch over schema variants, one return per case
    schema: Any,
    *,
    parent_class_name: str,
    field_name: str,
    nested_classes: list[GeneratedClass],
    imports: set[str],
) -> str:
    """Resolve a JSON schema to a Python type annotation string.

    Side effects: pushes any required nested class onto ``nested_classes``
    and any required ``from typing import X`` onto ``imports``. Returns the
    annotation text the caller writes after ``field_name:``.
    """
    if not isinstance(schema, dict):
        # An unparsable fragment (e.g. a stale cycle marker) collapses to ``Any``.
        imports.add("from typing import Any")
        return "Any"

    if "$ref" in schema:
        # Cycle stub left behind by ``deref_schema`` — we lost the type info.
        imports.add("from typing import Any")
        return "dict[str, Any]"

    any_of = schema.get("anyOf") or schema.get("oneOf")
    if any_of:
        return _resolve_union(
            any_of,
            parent_class_name=parent_class_name,
            field_name=field_name,
            nested_classes=nested_classes,
            imports=imports,
        )

    enum = schema.get("enum")
    if enum:
        return _enum_primitive(enum, schema.get("type"), imports)

    if "const" in schema:
        return _enum_primitive([schema["const"]], schema.get("type"), imports)

    schema_type = schema.get("type")
    if schema_type == "array":
        inner = schema_to_type(
            schema.get("items") or {},
            parent_class_name=parent_class_name,
            field_name=field_name + "_item",
            nested_classes=nested_classes,
            imports=imports,
        )
        return f"list[{inner}]"

    if schema_type == "object" or "properties" in schema:
        return _resolve_object(
            schema,
            parent_class_name=parent_class_name,
            field_name=field_name,
            nested_classes=nested_classes,
            imports=imports,
        )

    if schema_type in _PRIMITIVE_TYPES:
        py_type = _PRIMITIVE_TYPES[schema_type]
        if py_type == "str":
            fmt = schema.get("format")
            if fmt in _STRING_FORMATS:
                qualified = _STRING_FORMATS[fmt]
                # Qualified import (``import datetime``) avoids shadowing
                # field names like ``date`` / ``datetime``.
                imports.add("import datetime")
                return qualified
        return py_type

    # Unknown / missing type: keep the field permissive.
    imports.add("from typing import Any")
    return "Any"


def _enum_primitive(
    values: list[Any],
    declared_type: Any,  # noqa: ARG001 — kept for caller compatibility
    imports: set[str],
) -> str:
    """Map an ``enum`` / ``const`` to a ``Literal[...]`` annotation.

    Pydantic enforces ``Literal`` membership at construction time so
    invalid choices raise instead of silently flowing through to the
    upstream API. ``None`` is included as a valid Literal member so the
    field can be omitted ("all values, no filter") without losing the
    rejection of typo'd values like ``"Imprt"``.

    openbb-core's docstring renderer used to collapse
    ``Literal[...] | None`` to the bogus ``Optional[None]``; that's
    been fixed (Literal args render as the primitive type of their
    members), so the docstring shows ``str | None`` while the runtime
    type still rejects unknown values.
    """
    if not values:
        imports.add("from typing import Any")
        return "Any"
    rendered_members = ", ".join(repr(v) for v in values)
    imports.add("from typing import Literal")
    # The ``| None`` suffix gets appended by ``generate_class`` for
    # non-required fields (with ``default=None``) — so callers omit the
    # filter to get all values, or pass a Literal member to constrain.
    return f"Literal[{rendered_members}]"


def _resolve_union(
    variants: list[Any],
    *,
    parent_class_name: str,
    field_name: str,
    nested_classes: list[GeneratedClass],
    imports: set[str],
) -> str:
    """Resolve an ``anyOf`` / ``oneOf`` list into a Python annotation.

    ``[X, {type: null}]`` collapses to ``Optional[X]`` for readability. Real
    multi-type unions become ``Union[A, B, ...]``. Empty unions degrade to
    ``Any``.
    """
    non_null = [
        v for v in variants if not (isinstance(v, dict) and v.get("type") == "null")
    ]
    is_optional = len(non_null) != len(variants)

    if not non_null:
        imports.add("from typing import Any")
        return "Any"

    rendered: list[str] = []
    for variant in non_null:
        rendered.append(
            schema_to_type(
                variant,
                parent_class_name=parent_class_name,
                field_name=field_name,
                nested_classes=nested_classes,
                imports=imports,
            )
        )
    # Drop duplicates while preserving order so ``str | str`` doesn't show up.
    seen: set[str] = set()
    unique: list[str] = []
    for r in rendered:
        if r not in seen:
            seen.add(r)
            unique.append(r)

    inner = unique[0] if len(unique) == 1 else " | ".join(unique)

    if is_optional:
        return f"{inner} | None"
    return inner


def _resolve_object(
    schema: dict[str, Any],
    *,
    parent_class_name: str,
    field_name: str,
    nested_classes: list[GeneratedClass],
    imports: set[str],
) -> str:
    """Either generate a nested class or fall back to ``dict[str, Any]``.

    A schema with concrete ``properties`` becomes a nested ``BaseModel``
    subclass. ``additionalProperties: true`` with no properties collapses
    to ``dict[str, Any]`` because the shape is open.
    """
    properties = schema.get("properties") or {}
    if not properties:
        # ``additionalProperties: {"type": "number"}`` → ``dict[str, float]`` —
        # preserves the typed-value information instead of collapsing to ``Any``.
        ap = schema.get("additionalProperties")
        if isinstance(ap, dict):
            value_type = schema_to_type(
                ap,
                parent_class_name=parent_class_name,
                field_name=field_name + "_value",
                nested_classes=nested_classes,
                imports=imports,
            )
            return f"dict[str, {value_type}]"
        imports.add("from typing import Any")
        return "dict[str, Any]"

    nested_name = schema.get("title") or class_name_from(parent_class_name, field_name)
    nested_name = class_name_from(nested_name)
    nested = generate_class(
        schema,
        class_name=nested_name,
        docstring=schema.get("description"),
    )
    nested_classes.append(nested)
    return nested_name


def render_field_default(default: Any) -> str:
    """Render a JSON default value as a Python literal for ``Field(default=...)``."""
    if isinstance(default, bool):
        return "True" if default else "False"
    if isinstance(default, (int, float)):
        return repr(default)
    if isinstance(default, str):
        return repr(default)
    if default is None:
        return "None"
    if isinstance(default, (list, tuple, dict)):
        return repr(default)
    return repr(default)


_LINE_LENGTH_BUDGET = 88


def _build_field_call(
    *,
    description: str | None,
    default: Any,
    has_default: bool,
    required: bool,
    alias: str | None,
    leading_width: int = 0,
) -> str:
    """Compose the ``Field(...)`` text used after ``field_name: type =``.

    Parameters
    ----------
    description : str, optional
        The field description (becomes the ``description`` kwarg).
    default : Any
        The literal default value, or ``None`` when ``has_default`` is False.
    has_default : bool
        Whether the schema specified an explicit default.
    required : bool
        Whether the field is required (no default emitted in that case).
    alias : str, optional
        On-the-wire JSON name when it differs from the Python identifier.
    leading_width : int
        Number of characters consumed before the ``Field(...)`` call on
        the line — used to decide whether to wrap across multiple lines
        so the result fits within ``_LINE_LENGTH_BUDGET``.

    Returns
    -------
    str
        The full ``Field(...)`` source. Empty string when no metadata
        applies — caller drops the ``=`` in that case.
    """
    args: list[str] = []
    if has_default and not required:
        args.append(f"default={render_field_default(default)}")
    elif not required:
        args.append("default=None")
    if alias is not None:
        args.append(f"alias={alias!r}")
    if description is not None:
        args.append(f"description={_python_string_literal(description)}")
    if not args:
        return ""
    single_line = "Field(" + ", ".join(args) + ")"
    if leading_width + len(single_line) <= _LINE_LENGTH_BUDGET:
        return single_line
    # Wrap across lines so each argument lands within the line-length budget.
    inner = ",\n        ".join(args)
    return f"Field(\n        {inner},\n    )"


def _resolve_field_description(
    prop: dict[str, Any],
    field_name: str | None = None,  # noqa: ARG001 — kept for caller call site
) -> str:
    """Pick the description text for a Pydantic Field.

    Priority: ``description`` > ``title`` > ``Example: <example value>``.
    When the schema has an ``enum``, the allowed choices are appended (or
    used as the body when there's no other text) so the information is
    preserved after we stop emitting ``Literal[...]`` annotations.

    Falls back to the empty string when the spec has nothing to say —
    openbb-core's DocstringGenerator renders ``field.description`` directly,
    so passing ``None`` produces the literal text ``"None"`` under the field.
    An empty string renders as nothing.
    """
    text = prop.get("description") or prop.get("title")
    parts: list[str] = []
    if text:
        parts.append(text.rstrip(". ") + ".")
    elif prop.get("example") is not None:
        parts.append(f"Example: {prop['example']}.")
    enum = prop.get("enum") or (
        [prop["const"]]
        if isinstance(prop.get("const"), (str, int, float, bool))
        else None
    )
    if enum:
        rendered = ", ".join(str(v) for v in enum)
        parts.append(f"Choices: {rendered}.")
    return " ".join(parts).rstrip()


def _nested_object_breakout(prop: dict[str, Any]) -> str:
    """Render an inline breakout of a nested object's fields.

    openbb-core's docstring renderer prints ``field.description`` directly
    under each field but does NOT recursively expand nested-class types —
    so ``num_dealers : NumDealers | None`` shows up as a bare class
    reference with no hint at the inner shape. By embedding a one-line
    summary of the inner fields into the description, the rendered
    docstring becomes self-contained: every nested model's contents are
    visible without the user having to chase down the class definition.

    Returns the empty string for primitives, arrays-of-primitives, unions,
    and ``$ref`` cycle stubs — anywhere there's no flat property list to
    summarize.
    """
    target = prop
    if isinstance(prop.get("items"), dict):
        target = prop["items"]
    # ``oneOf`` envelopes a single typed variant — descend so item schemas
    # like ``{oneOf: [{properties: {...}}]}`` still produce a breakout.
    for combinator in ("oneOf", "anyOf"):
        variants = target.get(combinator)
        if isinstance(variants, list):
            for variant in variants:
                if isinstance(variant, dict) and isinstance(
                    variant.get("properties"), dict
                ):
                    target = variant
                    break
    properties = target.get("properties")
    if not isinstance(properties, dict) or not properties:
        return ""
    summaries: list[str] = []
    for inner_name, inner_sch in properties.items():
        if not isinstance(inner_sch, dict):
            summaries.append(inner_name)
            continue
        inner_type = _quick_schema_type(inner_sch)
        summaries.append(f"{inner_name} ({inner_type})")
    label = (
        "Inner item fields" if isinstance(prop.get("items"), dict) else "Inner fields"
    )
    return f"{label}: {', '.join(summaries)}."


def _quick_schema_type(schema: dict[str, Any]) -> str:
    """Best-effort shorthand type label for breakout text.

    Doesn't replicate ``schema_to_type`` (no nested-class generation, no
    import tracking) — just produces a short human-readable label that's
    accurate enough to help a reader skim a Numpy-style docstring.
    """
    if isinstance(schema.get("enum"), list):
        return "str"
    schema_type = schema.get("type")
    if schema_type == "array":
        items = schema.get("items")
        inner = "Any"
        if isinstance(items, dict):
            inner = _quick_schema_type(items)
        return f"list[{inner}]"
    if schema_type == "object" or "properties" in schema:
        title = schema.get("title")
        return title or "object"
    if schema_type in _PRIMITIVE_TYPES:
        if schema_type == "string":
            fmt = schema.get("format")
            if fmt == "date":
                return "date"
            if fmt == "date-time":
                return "datetime"
        return _PRIMITIVE_TYPES[schema_type]
    return "Any"


def _python_string_literal(text: str) -> str:
    """Render a docstring-safe string literal that survives multi-line text.

    Parameters
    ----------
    text : str
        The raw string to embed in generated source.

    Returns
    -------
    str
        A quoted Python literal — triple-quoted when ``text`` contains a
        newline or both ``'`` and ``"``, single-quoted via ``repr`` otherwise.
    """
    if "\n" in text or "'" in text and '"' in text:
        escaped = text.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
        return f'"""{escaped}"""'
    return repr(text)


def _annotation_for_docstring(annotation: str) -> tuple[str, bool]:
    """Strip ``| None`` from a type annotation for Numpy-style ``:`` lines.

    Parameters
    ----------
    annotation : str
        The Python type annotation (e.g. ``"str | None"``, ``"list[int]"``).

    Returns
    -------
    tuple of (str, bool)
        The bare type without ``| None`` suffix, and a flag indicating
        whether the annotation was optional. The flag drives the
        ``", optional"`` suffix in the docstring's Parameters block.
    """
    suffix = " | None"
    if annotation.endswith(suffix):
        return (annotation[: -len(suffix)].strip(), True)
    return (annotation, False)


def _render_numpy_parameters(
    fields: list[tuple[str, str, str | None, bool, Any, bool]],
) -> str:
    r"""Build a Numpy-style ``Parameters`` block for a class / function docstring.

    Parameters
    ----------
    fields : list of tuple
        Each tuple is
        ``(name, annotation, description, has_default, default, optional)``
        — ``name`` is the (possibly aliased) Python identifier,
        ``annotation`` is the rendered type, ``description`` is the prose
        from the schema (or ``None``), ``has_default`` flags presence of
        an explicit default, ``default`` is the literal value, and
        ``optional`` is ``True`` for fields whose annotation included
        ``| None`` (i.e. required-ness was relaxed).

    Returns
    -------
    str
        The full block — ``"Parameters\\n----------\\n…"`` — with no
        leading or trailing newlines. Empty string when ``fields`` is empty.
    """
    if not fields:
        return ""
    lines = ["Parameters", "----------"]
    for name, annotation, description, has_default, default, optional in fields:
        bare, _ = _annotation_for_docstring(annotation)
        type_label = f"{bare}, optional" if optional else bare
        lines.append(f"{name} : {type_label}")
        body = description or ""
        if has_default and default is not None:
            suffix = f"(default: {render_field_default(default)})"
            body = f"{body} {suffix}".strip() if body else suffix
        if body:
            for piece in body.split("\n"):
                lines.append(f"    {piece}")
    return "\n".join(lines)


def _render_class_docstring(
    summary: str,
    fields: list[tuple[str, str, str | None, bool, Any, bool]],
) -> str:
    """Render a Numpy-style class docstring and indent every line by four spaces.

    Parameters
    ----------
    summary : str
        The summary sentence shown immediately after the opening quotes.
    fields : list of tuple
        Tuples consumed by ``_render_numpy_parameters`` (see its docstring).

    Returns
    -------
    str
        The full triple-double-quoted block, ready to be concatenated into a class
        body. Always uses triple-double quotes so the generated source
        round-trips cleanly through ``ruff format`` and tools that lint
        for D-rules.
    """
    summary_clean = summary.strip()
    if not summary_clean.endswith("."):
        summary_clean += "."
    lines = [f'    """{summary_clean}']
    params_block = _render_numpy_parameters(fields)
    if params_block:
        lines.append("")
        for line in params_block.split("\n"):
            lines.append(f"    {line}" if line else "")
    lines.append('    """')
    return "\n".join(lines)


def render_function_docstring(
    summary: str,
    *,
    parameters: list[tuple[str, str, str | None]] | None = None,
    returns: tuple[str, str | None] | None = None,
    indent: str = "    ",
) -> str:
    """Render a Numpy-style function / method docstring.

    Parameters
    ----------
    summary : str
        The one-line summary sentence (a trailing ``.`` is added if missing).
    parameters : list of (name, type, description) tuples, optional
        Each tuple becomes one entry under the ``Parameters`` section. Use
        ``None`` for ``description`` to emit a placeholder dot.
    returns : tuple of (type, description), optional
        When supplied, emits a ``Returns`` section with the given type and
        description.
    indent : str
        The indentation prefix for every line of the rendered block.

    Returns
    -------
    str
        The full triple-double-quoted block, indented by ``indent`` and ready to be
        concatenated into a function body.
    """
    summary_clean = summary.strip()
    if not summary_clean.endswith("."):
        summary_clean += "."
    lines = [f'{indent}"""{summary_clean}']
    if parameters:
        lines.append("")
        lines.append(f"{indent}Parameters")
        lines.append(f"{indent}----------")
        for name, type_label, description in parameters:
            lines.append(f"{indent}{name} : {type_label}")
            if description:
                for piece in description.split("\n"):
                    lines.append(f"{indent}    {piece}")
    if returns is not None:
        return_type, return_desc = returns
        lines.append("")
        lines.append(f"{indent}Returns")
        lines.append(f"{indent}-------")
        lines.append(f"{indent}{return_type}")
        if return_desc:
            for piece in return_desc.split("\n"):
                lines.append(f"{indent}    {piece}")
    lines.append(f'{indent}"""')
    return "\n".join(lines)


def generate_class(
    schema: dict[str, Any],
    *,
    class_name: str,
    base_class: str = "BaseModel",
    docstring: str | None = None,
) -> GeneratedClass:
    """Build a Pydantic class definition from an OpenAPI ``object`` schema.

    Each top-level property becomes one ``name: type = Field(...)`` line.
    Nested object schemas spawn additional ``GeneratedClass`` entries on the
    return value's ``nested`` list — the caller emits those before this
    class so forward references resolve at import time.

    Required-ness comes from the schema's ``required`` array. Defaults from
    each property's ``default``. Descriptions from ``description`` /
    ``title``. Field-name conflicts (Python keywords, dotted names, leading
    digits) are normalized and round-tripped via ``alias``.
    """
    properties: dict[str, Any] = schema.get("properties") or {}
    required_set: set[str] = set(schema.get("required") or [])
    nested_classes: list[GeneratedClass] = []
    imports: set[str] = {"from pydantic import BaseModel, Field"}
    body_lines: list[str] = []
    doc_fields: list[tuple[str, str, str | None, bool, Any, bool]] = []

    for raw_name, prop_schema in properties.items():
        safe_name, needs_alias = safe_field_name(raw_name)
        annotation = schema_to_type(
            prop_schema if isinstance(prop_schema, dict) else {},
            parent_class_name=class_name,
            field_name=safe_name,
            nested_classes=nested_classes,
            imports=imports,
        )
        is_required = raw_name in required_set
        prop = prop_schema if isinstance(prop_schema, dict) else {}
        has_default = "default" in prop
        if not is_required and "None" not in annotation:
            annotation = f"{annotation} | None"
        description = _resolve_field_description(prop, field_name=raw_name)
        breakout = _nested_object_breakout(prop)
        if breakout:
            description = (
                f"{description} {breakout}".strip() if description else breakout
            )
        prefix = f"    {safe_name}: {annotation} = "
        field_call = _build_field_call(
            description=description,
            default=prop.get("default"),
            has_default=has_default,
            required=is_required,
            alias=raw_name if needs_alias else None,
            leading_width=len(prefix),
        )
        line = f"    {safe_name}: {annotation}"
        if field_call:
            line += f" = {field_call}"
        body_lines.append(line)

        doc_fields.append(
            (
                safe_name,
                annotation,
                description,
                has_default,
                prop.get("default"),
                not is_required,
            )
        )

    if not body_lines:
        body_lines.append("    pass")

    summary = docstring or class_name
    doc_block = _render_class_docstring(summary, doc_fields)

    source = (
        f"class {class_name}({base_class}):\n"
        f"{doc_block}\n\n" + "\n".join(body_lines) + "\n"
    )

    return GeneratedClass(
        name=class_name,
        source=source,
        nested=nested_classes,
        imports=imports,
    )


def consolidate_imports(imports: set[str]) -> list[str]:
    """Merge multiple ``from X import A`` / ``from X import B`` into one line.

    Parameters
    ----------
    imports : set of str
        Raw import statements (e.g. ``"from typing import Any"``).

    Returns
    -------
    list of str
        Sorted list with same-module ``from`` imports collapsed.
        ``import X`` lines pass through unchanged. The output preserves
        the `import X` / `from X import a, b, c` ordering ``ruff format``
        produces.
    """
    from_imports: dict[str, set[str]] = {}
    bare_imports: set[str] = set()
    for raw_line in imports:
        line = raw_line.strip()
        if line.startswith("from ") and " import " in line:
            module, _, names = line[len("from ") :].partition(" import ")
            for raw_name in names.split(","):
                name = raw_name.strip()
                if name:
                    from_imports.setdefault(module.strip(), set()).add(name)
        else:
            bare_imports.add(line)
    out: list[str] = sorted(bare_imports)
    for module in sorted(from_imports):
        names = ", ".join(sorted(from_imports[module]))
        out.append(f"from {module} import {names}")
    return out


def render_module(
    cls: GeneratedClass,
    *,
    module_docstring: str | None = None,
) -> str:
    """Render a ``cls`` and its nested classes as a single importable module.

    Imports are deduplicated, consolidated by module so ``Any`` and
    ``Literal`` from ``typing`` land on one line, sorted, and split into
    stdlib / third-party blocks separated by a blank line — matching the
    style ``ruff format`` would normalize to.
    """
    classes = cls.flatten()
    imports = consolidate_imports(cls.collect_imports())

    stdlib: list[str] = []
    third_party: list[str] = []
    for imp in imports:
        if (
            imp.startswith("from typing")
            or imp.startswith("from datetime")
            or imp.startswith("import typing")
            or imp.startswith("import datetime")
        ):
            stdlib.append(imp)
        else:
            third_party.append(imp)

    parts: list[str] = []
    if module_docstring:
        summary = module_docstring.strip()
        if not summary.endswith("."):
            summary += "."
        # Always triple-quote module docstrings: ruff's D-rules expect that
        # form and ``ruff format`` will rewrite single quotes to triple anyway.
        parts.append(f'"""{summary}"""')
        parts.append("")
    if stdlib:
        parts.extend(stdlib)
        parts.append("")
    if third_party:
        parts.extend(third_party)
        parts.append("")
    parts.append("")
    parts.extend(c.source for c in classes)
    return "\n".join(parts).rstrip() + "\n"
