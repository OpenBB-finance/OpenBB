from dataclasses import dataclass, make_dataclass
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from fastapi import Query
from openbb_provider.map import build_provider_mapping
from pydantic import BaseConfig, BaseModel, Extra, Field, create_model


@dataclass
class DataclassField:
    name: str
    type_: Any
    default: Any


@dataclass
class ExtraParams:
    pass


@dataclass
class StandardParams:
    pass


@dataclass
class ProviderChoices:
    provider: Literal  # type: ignore


class StandardData(BaseModel):
    pass


class ExtraData(BaseModel):
    pass


class ProviderInterface:
    """Provider interface class. Provides access to 'openbb_provider' package information.

    Attributes
    ----------
    map : Dict[str, Dict[str, Dict[str, Any]]]
        Dictionary of provider information.
    model_providers : Dict[str, ProviderChoices]
        Dictionary of provider choices by model.
    params : Dict[str, Dict[str, Union[StandardParams, ExtraParams]]]
        Dictionary of params by model.
    merged_data : Dict[str, BaseModel]
        Dictionary of data by model.
    providers_literal : type
        Literal of provider names.
    provider_choices : type
        Dataclass with literal of provider names.
    models : List[str]
        List of model names.
    """

    def __init__(self) -> None:
        self.__map = build_provider_mapping()
        self.__model_providers_map = self.__generate_model_providers_dc()
        self.__params = self.__generate_params_dc()
        self.__data = self.__generate_data_dc()
        self.__merged_data = self.__merge_data_dc(self.__data)

    @property
    def map(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        return self.__map

    @property
    def model_providers(self) -> Dict[str, ProviderChoices]:
        return self.__model_providers_map

    @property
    def params(self) -> Dict[str, Dict[str, Union[StandardParams, ExtraParams]]]:
        return self.__params

    @property
    def data(self) -> Dict[str, Dict[str, Union[StandardData, ExtraData]]]:
        return self.__data

    @property
    def merged_data(self) -> Dict[str, BaseModel]:
        return self.__merged_data

    @property
    def providers_literal(self) -> type:
        providers = []
        for _, provider in self.map.items():
            providers.extend(list(provider.keys()))
        providers = list(set(providers))
        if "openbb" in providers:
            providers.remove("openbb")

        return Literal[tuple(providers)]  # type: ignore

    @property
    def provider_choices(self) -> type:
        return make_dataclass(
            cls_name="ProviderChoices",
            fields=[("provider", self.providers_literal)],
            bases=(ProviderChoices,),
        )

    @property
    def models(self) -> List[str]:
        return list(self.__map.keys())

    @staticmethod
    def __merge_fields(
        current: DataclassField, incoming: DataclassField, query: bool = False
    ) -> DataclassField:
        current_name = current.name
        current_type = current.type_
        incoming_type = incoming.type_

        if query:
            merged_default = Query(
                default=current.default.default,
                description=f"{current.default.description}, {incoming.default.description}",
            )
        else:
            merged_default = current.default

        merged_type = (
            Union[current_type, incoming_type]
            if current_type != incoming_type
            else current_type
        )

        return DataclassField(
            name=current_name,
            type_=merged_type,
            default=merged_default,
        )

    @staticmethod
    def __create_field(
        name: str,
        field: Dict[str, Any],
        description: Optional[str] = None,
        query: bool = False,
    ) -> DataclassField:
        new_name = name.replace(".", "_")
        type_ = field["type"]

        default = ... if field["required"] else field["default"]
        if query:
            default = Query(default=default, description=description)
        elif description:
            default = Field(default=default, description=description)

        return DataclassField(new_name, type_, default)

    @classmethod
    def __extract_params(
        cls,
        providers: Any,
    ) -> Tuple[Dict[str, Tuple[str, Any, Any]], Dict[str, Tuple[str, Any, Any]]]:
        standard: Dict[str, Tuple[str, Any, Any]] = {}
        extra: Dict[str, Tuple[str, Any, Any]] = {}

        for provider_name, model_details in providers.items():
            if provider_name == "openbb":
                for name, field in model_details["QueryParams"]["fields"].items():
                    incoming = cls.__create_field(name, field, query=True)

                    standard[incoming.name] = (
                        incoming.name,
                        incoming.type_,
                        incoming.default,
                    )
            else:
                for name, field in model_details["QueryParams"]["fields"].items():
                    if name not in providers["openbb"]["QueryParams"]["fields"]:
                        incoming = cls.__create_field(
                            name, field, provider_name, query=True
                        )

                        if incoming.name in extra:
                            current = DataclassField(*extra[incoming.name])
                            updated = cls.__merge_fields(current, incoming, query=True)
                        else:
                            updated = incoming

                        if not updated.default.description.startswith(
                            "Available for providers:"
                        ):
                            updated.default.description = (
                                "Available for providers: "
                                + updated.default.description
                            )

                        extra[updated.name] = (
                            updated.name,
                            updated.type_,
                            updated.default,
                        )

        return standard, extra

    @classmethod
    def __extract_data(
        cls,
        providers: Any,
    ) -> Tuple[Dict[str, Tuple[str, Any, Any]], Dict[str, Tuple[str, Any, Any]]]:
        standard: Dict[str, Tuple[str, Any, Any]] = {}
        extra: Dict[str, Tuple[str, Any, Any]] = {}

        for provider_name, model_details in providers.items():
            if provider_name == "openbb":
                for name, field in model_details["Data"]["fields"].items():
                    incoming = cls.__create_field(name, field, provider_name)

                    standard[incoming.name] = (
                        incoming.name,
                        incoming.type_,
                        incoming.default,
                    )
            else:
                for name, field in model_details["Data"]["fields"].items():
                    if name not in providers["openbb"]["Data"]["fields"]:
                        incoming = cls.__create_field(name, field, provider_name)

                        if incoming.name in extra:
                            current = DataclassField(*extra[incoming.name])
                            updated = cls.__merge_fields(current, incoming)
                        else:
                            updated = incoming

                        extra[updated.name] = (
                            updated.name,
                            updated.type_,
                            updated.default,
                        )

        return standard, extra

    def __generate_params_dc(
        self,
    ) -> Dict[str, Dict[str, Union[StandardParams, ExtraParams]]]:
        """Generate dataclasses for params.

        This creates a dictionary of dataclasses that can be used as extra params.

        Example:

        @dataclass
        class StockNews(StandardParams):
            symbols: str = Query(...)
            page: int = Query(default=1)

        @dataclass
        class StockNews(ExtraParams):
            pageSize: int = Query(default=15, description="benzinga")
            displayOutput: int = Query(default="headline", description="benzinga")
            ...
            sort: str = Query(default=None, description="benzinga, polygon")
        """

        result: Dict = {}

        for model_name, providers in self.__map.items():
            standard, extra = self.__extract_params(providers)

            result[model_name] = {
                "standard": make_dataclass(  # type: ignore
                    cls_name=model_name,
                    fields=list(standard.values()),
                    bases=(StandardParams,),
                ),
                "extra": make_dataclass(  # type: ignore
                    cls_name=model_name,
                    fields=list(extra.values()),
                    bases=(ExtraParams,),
                ),
            }
        return result

    def __generate_model_providers_dc(self) -> Dict[str, ProviderChoices]:
        """Generate dataclasses for provider choices by model.

        This creates a dictionary that maps model names to dataclasses that can be used
        as provider choices.

        Example:

        @dataclass
        class StockNews(ProviderChoices):
            provider: Literal["benzinga", "polygon"]
        """

        result: Dict = {}

        for model_name, providers in self.__map.items():
            choices = list(providers.keys())
            if "openbb" in choices:
                choices.remove("openbb")

            result[model_name] = make_dataclass(  # type: ignore
                cls_name=model_name,
                fields=[("provider", Literal[tuple(choices)])],  # type: ignore
                bases=(ProviderChoices,),
            )

        return result

    def __generate_data_dc(
        self,
    ) -> Dict[str, Dict[str, Union[StandardData, ExtraData]]]:
        """Generate dataclasses for data.

        This creates a dictionary of dataclasses that can be used as data.

        Example:

        class StockEODData(StandardData):
            date: date
            open: PositiveFloat
            high: PositiveFloat
            low: PositiveFloat
            close: PositiveFloat
            adj_close: Optional[PositiveFloat]
            volume: PositiveFloat
        """
        result: Dict = {}

        for model_name, providers in self.__map.items():
            standard, extra = self.__extract_data(providers)
            result[model_name] = {
                "standard": make_dataclass(  # type: ignore
                    cls_name=model_name,
                    fields=list(standard.values()),
                    bases=(StandardData,),
                ),
                "extra": make_dataclass(  # type: ignore
                    cls_name=model_name,
                    fields=list(extra.values()),
                    bases=(ExtraData,),
                ),
            }

        return result

    def __merge_data_dc(
        self, data: Dict[str, Dict[str, Union[StandardData, ExtraData]]]
    ) -> Dict[str, BaseModel]:
        """Merge standard data with extra data into a single BaseModel"""
        result: Dict = {}
        for model_name, dataclasses in data.items():
            standard = dataclasses["standard"]
            extra = dataclasses["extra"]

            fields = standard.__fields__.copy()
            fields.update(extra.__fields__)

            fields_dict: Dict[str, Tuple[Any, Any]] = {}
            for name, field in fields.items():
                fields_dict[name] = (
                    field.type_,
                    Field(
                        default=field.default, description=field.field_info.description
                    ),
                )

            class Config(BaseConfig):
                extra = Extra.allow

            result[model_name] = create_model(  # type: ignore
                model_name,
                __config__=Config,
                **fields_dict,  # type: ignore
            )

        return result


__provider_interface = ProviderInterface()


def get_provider_interface() -> ProviderInterface:
    return __provider_interface
