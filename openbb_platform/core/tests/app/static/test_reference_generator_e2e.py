"""Drive the reference_generator + full builder paths via fake_router.

The existing `built_package_dir` fixture patches out `_save_reference_file`
which means `ReferenceGenerator.get_paths`/`get_routers` (~660 lines) never
runs. This file repeats the build *without* that patch so reference_generator
gets exercised.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from openbb_core.app.router import Router, RouterLoader
from openbb_core.app.static.package_builder import PackageBuilder
from openbb_core.app.static.package_builder.reference_generator import (
    ReferenceGenerator,
)
from openbb_core.provider.abstract.data import Data

pytestmark = pytest.mark.requires_pandas


class _TransformResult(Data):
    """Result row."""

    symbol: str = ""
    value: float = 0.0


@pytest.fixture
def install_router(monkeypatch, isolated_provider_interface):
    """Override conftest version to support both class- and instance-style calls."""

    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.docstring_generator."
        "DocstringGenerator.provider_interface",
        isolated_provider_interface,
    )
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.reference_generator."
        "ReferenceGenerator.pi",
        isolated_provider_interface,
    )

    def _install(child: Router, prefix: str = "/test") -> Router:
        parent = Router()
        parent.include_router(router=child, prefix=prefix)
        RouterLoader.from_extensions.cache_clear()  # type: ignore[attr-defined]
        monkeypatch.setattr(
            "openbb_core.app.router.RouterLoader.from_extensions",
            staticmethod(lambda: parent),
        )
        return parent

    return _install


@pytest.fixture
def built_package_with_reference(
    tmp_path: Path, fake_router: Router
) -> tuple[Path, dict]:
    """Run the FULL `PackageBuilder.build()` including `_save_reference_file`."""
    builder = PackageBuilder(directory=tmp_path, lint=False, verbose=False)
    captured: dict = {}

    real_save = builder._save_reference_file

    def spy(ext_map=None):
        captured["ext_map"] = ext_map
        return real_save(ext_map)

    with patch.object(builder, "_save_reference_file", side_effect=spy):
        builder.build()

    ref_path = tmp_path / "assets" / "reference.json"
    assert ref_path.exists(), f"reference.json not written to {ref_path}"

    import json

    captured["reference"] = json.loads(ref_path.read_text())
    return tmp_path, captured


def test_reference_file_written_with_paths_and_routers(built_package_with_reference):
    _, captured = built_package_with_reference
    ref = captured["reference"]
    assert "paths" in ref
    assert "routers" in ref
    assert "openbb" in ref


def test_reference_file_paths_exposes_fake_route(built_package_with_reference):
    _, captured = built_package_with_reference
    paths = captured["reference"]["paths"]
    assert paths, "Expected at least one path in reference.json"
    assert any("/test/" in p for p in paths), f"missing /test/* path; got {list(paths)}"


def test_reference_file_routers_keyed_by_path(built_package_with_reference):
    _, captured = built_package_with_reference
    routers = captured["reference"]["routers"]
    assert isinstance(routers, dict)


def test_reference_get_paths_directly(fake_router):
    """Drive ReferenceGenerator.get_paths against the real route_map."""
    from openbb_core.app.static.package_builder.path_handler import PathHandler

    route_map = PathHandler.build_route_map()
    paths = ReferenceGenerator.get_paths(route_map)
    assert isinstance(paths, dict)
    assert paths
    # Each path entry should expose a 'deprecated' boolean and 'description' string
    first = next(iter(paths.values()))
    assert isinstance(first, dict)


def test_reference_get_routers_directly(fake_router):
    from openbb_core.app.static.package_builder.path_handler import PathHandler

    route_map = PathHandler.build_route_map()
    routers = ReferenceGenerator.get_routers(route_map)
    assert isinstance(routers, dict)


@pytest.fixture
def router_with_data_processing(
    isolated_provider_interface, fake_model_name, install_router
):
    """Add a non-model (POST data-processing) command alongside a model command."""
    from typing import Annotated

    from openbb_core.app.model.command_context import CommandContext
    from openbb_core.app.model.field import OpenBBField
    from openbb_core.app.model.obbject import OBBject
    from openbb_core.app.provider_interface import (
        ExtraParams,
        ProviderChoices,
        StandardParams,
    )

    child = Router()

    async def model_cmd(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:  # type: ignore[empty-body]
        """Model command."""

    child.command(model=fake_model_name)(model_cmd)

    @child.command(methods=["POST"])
    async def transform(
        symbol: Annotated[str, OpenBBField(description="The symbol.")],
        days: int = 7,
    ) -> OBBject[list[_TransformResult]]:
        """Process some data.

        Parameters
        ----------
        symbol : str
            The symbol.
        days : int
            The days.

        Returns
        -------
        OBBject[list[_TransformResult]]
            Processed data.
        """

    return install_router(child, prefix="/test")


def test_reference_data_processing_endpoint(tmp_path, router_with_data_processing):
    builder = PackageBuilder(directory=tmp_path, lint=False, verbose=False)
    builder.build()
    import json

    ref = json.loads((tmp_path / "assets" / "reference.json").read_text())
    paths = ref["paths"]
    assert any("/test/transform" in p for p in paths)
    transform = next(p for k, p in paths.items() if "transform" in k)
    assert "parameters" in transform
    # data-processing path also produced parameters from formatted_params
    assert transform["parameters"].get("standard") is not None
