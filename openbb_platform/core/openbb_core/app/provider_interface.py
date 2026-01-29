"""提供者接口。"""

from collections.abc import Callable
from dataclasses import dataclass, make_dataclass
from difflib import SequenceMatcher
from typing import (
    Annotated,
    Any,
    Literal,
    Optional,
    Union,
    get_args,
    get_origin,
)

from fastapi import Body, Query
from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.obbject import OBBject
from openbb_core.provider.query_executor import QueryExecutor
from openbb_core.provider.registry_map import MapType, RegistryMap
from openbb_core.provider.utils.helpers import to_snake_case
from pydantic import (
    BaseModel,
    ConfigDict,
    Discriminator,
    Field,
    SerializeAsAny,
    Tag,
    create_model,
)
from pydantic.fields import FieldInfo

TupleFieldType = tuple[str, type | None, Any | None]


@dataclass
class DataclassField:
    """数据类字段。"""

    name: str
    annotation: type | None
    default: Any | None


@dataclass
class StandardParams:
    """标准参数数据类。"""


@dataclass
class ExtraParams:
    """额外参数数据类。"""


class StandardData(BaseModel):
    """标准数据模型。"""


class ExtraData(BaseModel):
    """额外数据模型。"""


@dataclass
class ProviderChoices:
    """提供者选择数据类。"""

    provider: Literal  # type: ignore


class ProviderInterface(metaclass=SingletonMeta):
    """提供者接口类。

    Properties
    ----------
    map : MapType
        提供者信息字典。
    credentials: List[str]
        凭据列表。
    model_providers : Dict[str, ProviderChoices]
        按模型划分的提供者选择字典。
    params : Dict[str, Dict[str, Union[StandardParams, ExtraParams]]]
        按模型划分的参数字典。
    return_schema : Dict[str, Type[BaseModel]]
        按模型划分的返回数据架构字典。
    available_providers : List[str]
        可用提供者列表。
    provider_choices : ProviderChoices
        包含提供者名称字面量的数据类。
    models : List[str]
        模型名称列表。

    Methods
    -------
    create_executor : QueryExecutor
        创建查询执行器
    """

    def __init__(
        self,
        registry_map: RegistryMap | None = None,
        query_executor: QueryExecutor | None = None,
    ) -> None:
        """初始化提供者接口。"""
        self._registry_map = registry_map or RegistryMap()
        self._query_executor = query_executor or QueryExecutor

        self._map = self._registry_map.standard_extra
        # TODO: 尝试在一次迭代中尝试这 4 种方法
        self._model_providers_map = self._generate_model_providers_dc(self._map)
        self._params = self._generate_params_dc(self._map)
        self._data = self._generate_data_dc(self._map)
        self._return_schema = self._generate_return_schema(self._data)
        self._return_annotations = self._generate_return_annotations(
            self._registry_map.original_models
        )

        self._available_providers = self._registry_map.available_providers
        self._provider_choices = self._get_provider_choices(self._available_providers)

    @property
    def map(self) -> MapType:
        """提供者信息字典。"""
        return self._map

    @property
    def credentials(self) -> dict[str, list[str]]:
        """将提供者映射到凭列表。"""
        return self._registry_map.credentials

    @property
    def model_providers(self) -> dict[str, ProviderChoices]:
        """按模型划分的提供者选择字典。"""
        return self._model_providers_map

    @property
    def params(self) -> dict[str, dict[str, StandardParams | ExtraParams]]:
        """按模型划分的参数字典。"""
        return self._params

    @property
    def data(self) -> dict[str, dict[str, StandardData | ExtraData]]:
        """按模型划分的数据字典。"""
        return self._data

    @property
    def return_schema(self) -> dict[str, type[BaseModel]]:
        """按模型合并后的数据字典。"""
        return self._return_schema

    @property
    def available_providers(self) -> list[str]:
        """可用提供者列表。"""
        return self._available_providers

    @property
    def provider_choices(self) -> type:
        """包含提供者名称字面量的数据类。"""
        return self._provider_choices

    @property
    def models(self) -> list[str]:
        """模型名称列表。"""
        return self._registry_map.models

    @property
    def return_annotations(self) -> dict[str, type[OBBject]]:
        """返回映射。"""
        return self._return_annotations

    def create_executor(self) -> QueryExecutor:
        """获取查询执行器。"""
        return self._query_executor(self._registry_map.registry)  # type: ignore[operator]

    @staticmethod
    def _merge_fields(
        current: DataclassField, incoming: DataclassField, query: bool = False
    ) -> DataclassField:
        """合并 2 个数据类字段。"""
        curr_name = current.name
        curr_type: type | None = current.annotation
        curr_desc = getattr(current.default, "description", "")
        curr_json_schema_extra = getattr(current.default, "json_schema_extra", {})

        inc_type: type | None = incoming.annotation
        inc_desc = getattr(incoming.default, "description", "")
        inc_json_schema_extra = getattr(incoming.default, "json_schema_extra", {})

        def split_desc(desc: str) -> str:
            """拆分字段描述，移除提供者标签和多项文本。"""
            item = desc.split(" (provider: ")
            detail = item[0] if item else ""
            # 同时移除 "Multiple comma separated items allowed." 用于比较
            detail = detail.replace(" Multiple comma separated items allowed.", "")
            detail = detail.replace("Multiple comma separated items allowed.", "")
            return detail.strip()

        def merge_json_schema_extra(curr: dict, inc: dict) -> dict:
            """合并 json schema extra。"""
            for key in curr.keys() & inc.keys():
                # 如果两个字典中的值都是列表，则合并这些键
                curr_value = curr[key]
                inc_value = inc[key]
                if isinstance(curr_value, list) and isinstance(inc_value, list):
                    curr[key] = list(set(curr.get(key, []) + inc.get(key, [])))
                    inc.pop(key)

            # 将 inc 中剩余的任何键添加到 curr 中
            curr.update(inc)
            return curr

        json_schema_extra: dict = merge_json_schema_extra(
            curr=curr_json_schema_extra or {}, inc=inc_json_schema_extra or {}
        )

        curr_detail = split_desc(curr_desc)
        inc_detail = split_desc(inc_desc)

        curr_title = getattr(current.default, "title", "") or ""
        inc_title = getattr(incoming.default, "title", "") or ""
        # 过滤掉空标题并连接
        provider_list = [t for t in [curr_title, inc_title] if t]
        providers = ",".join(provider_list)
        formatted_prov = ", ".join(provider_list)

        if SequenceMatcher(None, curr_detail, inc_detail).ratio() > 0.8:
            new_desc = f"{curr_detail} (provider: {formatted_prov})"
        else:
            new_desc = f"{curr_desc};\n    {inc_desc}"

        QF: Callable = Query if query else FieldInfo  # type: ignore[assignment]
        merged_default = QF(
            default=getattr(current.default, "default", None),
            title=providers,
            description=new_desc,
            json_schema_extra=json_schema_extra,
        )

        merged_type: type | None = (
            Union[curr_type, inc_type] if curr_type != inc_type else curr_type  # type: ignore[assignment]  # noqa
        )

        return DataclassField(curr_name, merged_type, merged_default)

    @staticmethod
    def _create_field(
        name: str,
        field: FieldInfo,
        provider_name: str | None = None,
        query: bool = False,
        force_optional: bool = False,
    ) -> DataclassField:
        new_name = name.replace(".", "_")
        annotation = field.annotation

        additional_description = ""
        choices: dict = {}
        if extra := field.json_schema_extra:
            providers: list = []
            for p, v in extra.items():  # type: ignore
                if isinstance(v, dict) and v.get("multiple_items_allowed"):
                    providers.append(p)
                    choices[p] = {"multiple_items_allowed": True, "choices": v.get("choices")}  # type: ignore
                elif isinstance(v, list) and "multiple_items_allowed" in v:
                    # 为了向后兼容，这之前是一个列表
                    providers.append(p)
                    choices[p] = {"multiple_items_allowed": True, "choices": None}  # type: ignore
                elif isinstance(v, dict) and v.get("choices"):
                    choices[p] = {
                        "multiple_items_allowed": False,
                        "choices": v.get("choices"),
                    }

                if isinstance(v, dict) and v.get("x-widget_config"):
                    if p not in choices:
                        choices[p] = {"x-widget_config": v.get("x-widget_config")}
                    else:
                        choices[p]["x-widget_config"] = v.get("x-widget_config")

            if providers:
                if provider_name:
                    additional_description += " 允许使用逗号分隔的多个项目。"
                else:
                    additional_description += (
                        " 允许提供者使用逗号分隔的多个项目: "
                        + ", ".join(providers)  # type: ignore[arg-type]
                        + "."
                    )
        provider_field = (
            f"(provider: {provider_name})" if provider_name != "openbb" else ""
        )
        description = (
            f"{field.description}{additional_description} {provider_field}"
            if provider_name and field.description
            else f"{field.description}{additional_description}"
        )

        if field.is_required():
            if force_optional:
                annotation = Optional[annotation]  # type: ignore  # noqa
                default = None
            else:
                default = ...
        else:
            default = field.default

        if (
            hasattr(annotation, "__name__")
            and annotation.__name__ in ["Dict", "dict", "Data"]  # type: ignore
            or field.kw_only is True
        ):
            return DataclassField(
                new_name,
                annotation,
                Body(
                    default=default,
                    title=provider_name,
                    description=description,
                    alias=field.alias or None,
                    json_schema_extra=choices,
                ),
            )

        if query:
            # 如果我们希望字段描述显示在 swagger 中，我们需要使用 query
            # 这是 fastapi 的限制
            return DataclassField(
                new_name,
                annotation,
                Query(
                    default=default,
                    title=provider_name,
                    description=description,
                    alias=field.alias or None,
                    json_schema_extra=choices,
                ),
            )
        if provider_name:
            return DataclassField(
                new_name,
                annotation,
                Field(
                    default=default or None,
                    title=provider_name,
                    description=description,
                    json_schema_extra=choices,
                ),
            )

        return DataclassField(new_name, annotation, default)

    @classmethod
    def _extract_params(
        cls,
        providers: Any,
    ) -> tuple[dict[str, TupleFieldType], dict[str, TupleFieldType]]:
        """从映射中提取参数。"""
        standard: dict[str, TupleFieldType] = {}
        extra: dict[str, TupleFieldType] = {}
        standard_fields = (
            providers.get("openbb", {}).get("QueryParams", {}).get("fields", {})
        )

        for provider_name, model_details in providers.items():
            if provider_name == "openbb":
                for name, field in model_details["QueryParams"]["fields"].items():
                    incoming = cls._create_field(name, field, query=True)

                    standard[incoming.name] = (
                        incoming.name,
                        incoming.annotation,
                        incoming.default,
                    )
            else:
                for name, field in model_details["QueryParams"]["fields"].items():
                    s_name = to_snake_case(name)

                    if name in standard_fields:
                        # 提供者重新定义了标准字段 - 合并描述
                        # 在合并之前检查描述是否不同
                        standard_desc = standard_fields[name].description or ""
                        provider_desc = field.description or ""

                        if provider_desc and provider_desc != standard_desc:
                            # 创建一个带有特定于提供者描述的字段
                            incoming = cls._create_field(
                                s_name,
                                field,
                                provider_name,
                                query=True,
                                force_optional=False,
                            )
                            # 合并到标准字段中
                            if s_name in standard:
                                current = DataclassField(*standard[s_name])
                                updated = cls._merge_fields(
                                    current, incoming, query=True
                                )
                                standard[s_name] = (
                                    updated.name,
                                    updated.annotation,
                                    updated.default,
                                )
                    else:
                        # 额外字段不在标准中 - 添加到额外参数
                        incoming = cls._create_field(
                            s_name,
                            field,
                            provider_name,
                            query=True,
                            force_optional=True,
                        )

                        if incoming.name in extra:
                            current = DataclassField(*extra[incoming.name])
                            updated = cls._merge_fields(current, incoming, query=True)
                        else:
                            updated = incoming

                        extra[updated.name] = (
                            updated.name,
                            updated.annotation,
                            updated.default,
                        )

        return standard, extra

    @classmethod
    def _extract_data(
        cls,
        providers: Any,
    ) -> tuple[dict[str, TupleFieldType], dict[str, TupleFieldType]]:
        standard: dict[str, TupleFieldType] = {}
        extra: dict[str, TupleFieldType] = {}

        for provider_name, model_details in providers.items():
            if provider_name == "openbb":
                for name, field in model_details["Data"]["fields"].items():
                    if (
                        name == "provider"
                        and field.description == "数据的提供者。"
                    ):  # noqa
                        continue
                    incoming = cls._create_field(name, field, "openbb")

                    standard[incoming.name] = (
                        incoming.name,
                        incoming.annotation,
                        incoming.default,
                    )
            else:
                for name, field in model_details["Data"]["fields"].items():
                    if name not in providers["openbb"]["Data"]["fields"]:
                        if (
                            name == "provider"
                            and field.description == "数据的提供者。"
                        ):  # noqa
                            continue
                        incoming = cls._create_field(
                            to_snake_case(name),
                            field,
                            provider_name,
                            force_optional=True,
                        )

                        if incoming.name in extra:
                            current = DataclassField(*extra[incoming.name])
                            updated = cls._merge_fields(current, incoming)
                        else:
                            updated = incoming

                        extra[updated.name] = (
                            updated.name,
                            updated.annotation,
                            updated.default,
                        )

                ),
            }
        return result

    def _generate_params_dc(
        self, map_: MapType
    ) -> dict[str, dict[str, StandardParams | ExtraParams]]:
        """为参数生成数据类。

        这将创建一个数据类字典，可以作为 FastAPI 依赖项注入。"""

        # 这将创建一个数据类字典，可以作为 FastAPI 依赖项注入。

        Example
        -------
        @dataclass
        class CompanyNews(StandardParams):
            symbols: str = Query(...)
            page: int = Query(default=1)

        @dataclass
        class CompanyNews(ExtraParams):
            pageSize: int = Query(default=15, title="benzinga")
            displayOutput: int = Query(default="headline", title="benzinga")
            ...
            sort: str = Query(default=None, title="benzinga,polygon")
        """
        result: dict = {}

        for model_name, providers in map_.items():
            standard: dict
            extra: dict
            standard, extra = self._extract_params(providers)

            result[model_name] = {
                "standard": make_dataclass(
                    cls_name=model_name,
                    fields=list(standard.values()),  # type: ignore[arg-type]
                    bases=(StandardParams,),
                ),
                "extra": make_dataclass(
                    cls_name=model_name,
                    fields=list(extra.values()),  # type: ignore[arg-type]
                    bases=(ExtraParams,),
                ),
            }
        return result

    def _generate_model_providers_dc(self
, map_: MapType) -> dict[str, ProviderChoices]:
        """按模型生成提供者选择的数据类。

        这将创建一个字典，将模型名称映射到可以作为 FastAPI 依赖项注入的数据类。"""

        # 这将创建一个将模型名称映射到可以作为 FastAPI 依赖项注入的数据类的字典。

        Example
        -------
        @dataclass
        class CompanyNews(ProviderChoices):
            provider: Literal["benzinga", "polygon"]
        """
        result: dict = {}

        for model_name, providers in map_.items():
            choices = sorted(list(providers.keys()))
            if "openbb" in choices:
                choices.remove("openbb")

            result[model_name] = make_dataclass(  # type: ignore
                cls_name=model_name,
                fields=[
                    (
                        "provider",
                        Literal[tuple(choices)],  # type: ignore
                        ... if len(choices) > 1 else choices[0],
                    )
                ],
                bases=(ProviderChoices,),
            )

        return result

    def _generate_data_dc(
        self, map_: MapType
    ) -> dict[str, dict[str, StandardData | ExtraData]]:
        """为数据生成数据类。

        这将创建一个数据类字典。"""

        # 这创建了一个数据类字典。

        Example
        -------
        class EquityHistoricalData(StandardData):
            date: date
            open: PositiveFloat
            high: PositiveFloat
            low: PositiveFloat
            close: PositiveFloat
            adj_close: Optional[PositiveFloat]
            volume: PositiveFloat
        """
        result: dict = {}

        for model_name, providers in map_.items():
            standard: dict
            extra: dict
            standard, extra = self._extract_data(providers)
            result[model_name] = {
                "standard": make_dataclass(
                    cls_name=model_name,
                    fields=list(standard.values()),  # type: ignore[arg-type]
                    bases=(StandardData,),
                ),
                "extra": make_dataclass(
                    cls_name=model_name,
                    fields=list(extra.values()),  # type: ignore[arg-type]
                    bases=(ExtraData,),
                ),
            }

        return result

    def _generate_return_schema(
        self,
        data: dict[str, dict[str, StandardData | ExtraData]],
    ) -> dict[str, type[BaseModel]]:
        """将标准数据与额外数据合并到单个 BaseModel 中，以便作为 FastAPI 依赖项注入。"""
        result: dict = {}
        for model_name, dataclasses in data.items():
            standard = dataclasses["standard"]
            extra = dataclasses["extra"]

            fields = standard.model_fields.copy()
            fields.update(extra.model_fields)

            fields_dict: dict[str, tuple[Any, Any]] = {}

            for name, field in fields.items():
                fields_dict[name] = (
                    field.annotation,
                    Field(
                        default=field.default,
                        title=field.title,
                        description=field.description,
                        alias=field.alias,
                        json_schema_extra=field.json_schema_extra,
                    ),
                )

            model_config = ConfigDict(extra="allow", populate_by_name=True)

            result[model_name] = create_model(  # type: ignore
                model_name,
                __config__=model_config,
                **fields_dict,  # type: ignore
            )

        return result

    def _get_provider_choices(self, available_providers: list[str]) -> type:
        return make_dataclass(
            cls_name="ProviderChoices",
            fields=[("provider", Literal[tuple(available_providers)])],  # type: ignore
            bases=(ProviderChoices,),
        )

    def _get_annotated_union(self, models: dict[str, Any]) -> Any:
        """获取带注释的联合。"""

        def get_provider(v: type[BaseModel]):
            """区分使用哪个 BaseModel 的可调用对象。"""
            return getattr(v, "_provider", None)

        args = set()
        for provider, model in models.items():
            data = model["data"]
            # 我们设置提供者以便在鉴别器函数中使用它
            setattr(data, "_provider", provider)
            if get_origin(data) is Annotated:
                metadata = data.__metadata__ + (Tag(provider),)
                annotated_args = (get_args(data)[0],) + metadata
                args.add(Annotated[annotated_args])
            else:
                args.add(Annotated[data, Tag(provider)])
        meta = Discriminator(get_provider) if len(args) > 1 else None
        return SerializeAsAny[Annotated[Union[tuple(args)], meta]]  # type: ignore  # noqa

    def _generate_return_annotations(
        self, original_models: dict[str, dict[str, Any]]
    ) -> dict[str, type[OBBject]]:
        """为 FastAPI 生成返回注释。"""

        Example
        -------
        class Data(BaseModel):
            ...

        class EquityData(Data):
            price: float

        class YFEquityData(EquityData):
            yf_field: str

        class AVEquityData(EquityData):
            av_field: str

        class OBBject(BaseModel):
            results: List[
                SerializeAsAny[
                    Annotated[
                        Union[
                            Annotated[YFEquityData, Tag("yf")],
                            Annotated[AVEquityData, Tag("av")],
                        ],
                        Discriminator(get_provider),
                    ]
                ]
            ]
        """
        annotations = {}
        for name, models in original_models.items():
            outer = {model["results_type"] for model in models.values()}
            inner = self._get_annotated_union(models)
            full = Union[tuple((o[inner] if o else inner) for o in outer)]  # type: ignore  # noqa
            annotations[name] = create_model(
                f"OBBject_{name}",
                __base__=OBBject[full],  # type: ignore
                __doc__=f"带有 {name} 类型结果的 OBBject",
            )
        return annotations
