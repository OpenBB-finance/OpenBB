from dataclasses import dataclass, make_dataclass
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from fastapi import Query
from openbb_provider.provider.provider_map import build_provider_mapping
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
    def __init__(self) -> None:
        self.__mapping = build_provider_mapping()
        self.__params = self.generate_params()
        self.__provider_choices = self.generate_provider_choices()
        self.__data = self.generate_data()
        self.__merged_data = self.generate_merged_data()

    @property
    def mapping(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        return self.__mapping

    @property
    def params(self) -> Dict[str, Dict[str, Union[StandardParams, ExtraParams]]]:
        return self.__params

    @property
    def provider_choices(self) -> Dict[str, ProviderChoices]:
        return self.__provider_choices

    @property
    def data(self) -> Dict[str, Dict[str, Union[StandardData, ExtraData]]]:
        return self.__data

    @property
    def merged_data(self) -> Dict[str, StandardData]:
        return self.__merged_data

    @property
    def providers(self) -> Literal:  # type: ignore
        providers = []
        for _, provider in self.mapping.items():
            providers.extend(list(provider.keys()))
        providers = list(set(providers))
        if "openbb" in providers:
            providers.remove("openbb")

        return Literal[tuple(providers)]  # type: ignore

    @property
    def queries(self) -> List[str]:
        return list(self.mapping.keys())

    @staticmethod
    def merge_fields(
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
    def create_field(
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

    def generate_params(
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

        # TODO: Break this function into smaller functions

        result: Dict = {}

        for query_name, providers in self.__mapping.items():
            standard_fields_dict: Dict[str, Tuple[str, Any, Any]] = {}
            extra_fields_dict: Dict[str, Tuple[str, Any, Any]] = {}
            for provider_name, query_details in providers.items():
                if provider_name == "openbb":
                    for name, field in query_details["QueryParams"]["fields"].items():
                        incoming = self.create_field(name, field, query=True)

                        standard_fields_dict[incoming.name] = (
                            incoming.name,
                            incoming.type_,
                            incoming.default,
                        )
                else:
                    for name, field in query_details["QueryParams"]["fields"].items():
                        if name not in providers["openbb"]["QueryParams"]["fields"]:
                            incoming = self.create_field(
                                name, field, provider_name, query=True
                            )

                            if incoming.name in extra_fields_dict:
                                current = DataclassField(
                                    *extra_fields_dict[incoming.name]
                                )
                                updated = self.merge_fields(current, incoming)
                            else:
                                updated = incoming

                            if not updated.default.description.startswith(
                                "Available for providers:"
                            ):
                                updated.default.description = (
                                    "Available for providers: "
                                    + updated.default.description
                                )

                            extra_fields_dict[updated.name] = (
                                updated.name,
                                updated.type_,
                                updated.default,
                            )

            result[query_name] = {
                "standard": make_dataclass(  # type: ignore
                    cls_name=query_name,
                    fields=list(standard_fields_dict.values()),
                    bases=(StandardParams,),
                ),
                "extra": make_dataclass(  # type: ignore
                    cls_name=query_name,
                    fields=list(extra_fields_dict.values()),
                    bases=(ExtraParams,),
                ),
            }

        return result

    def generate_provider_choices(self) -> Dict[str, ProviderChoices]:
        """Generate dataclasses for provider choices.

        This creates a dictionary of dataclasses that can be used as provider choices.

        Example:

        @dataclass
        class StockNews(ProviderChoices):
            provider: Literal["benzinga", "polygon", "openbb"]
        """

        result: Dict = {}

        for query_name, providers in self.__mapping.items():
            choices = list(providers.keys())
            if "openbb" in choices:
                choices.remove("openbb")

            result[query_name] = make_dataclass(  # type: ignore
                cls_name=query_name,
                fields=[("provider", Literal[tuple(choices)])],  # type: ignore
                bases=(ProviderChoices,),
            )

        return result

    def generate_merged_data(self) -> Dict[str, StandardData]:
        result: Dict = {}
        for query_name, dataclasses in self.__data.items():
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

            result[query_name] = create_model(  # type: ignore
                query_name,
                __config__=Config,
                **fields_dict,  # type: ignore
            )

        return result

    def generate_data(self) -> Dict[str, Dict[str, Union[StandardData, ExtraData]]]:
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

        for query_name, providers in self.__mapping.items():
            standard_fields_dict: Dict[str, Tuple[str, Any, Any]] = {}
            extra_fields_dict: Dict[str, Tuple[str, Any, Any]] = {}
            for provider_name, query_details in providers.items():
                if provider_name == "openbb":
                    for name, field in query_details["Data"]["fields"].items():
                        incoming = self.create_field(name, field, provider_name)

                        standard_fields_dict[incoming.name] = (
                            incoming.name,
                            incoming.type_,
                            incoming.default,
                        )
                else:
                    for name, field in query_details["Data"]["fields"].items():
                        if name not in providers["openbb"]["Data"]["fields"]:
                            incoming = self.create_field(name, field, provider_name)

                            if incoming.name in extra_fields_dict:
                                current = DataclassField(
                                    *extra_fields_dict[incoming.name]
                                )
                                updated = self.merge_fields(current, incoming)
                            else:
                                updated = incoming

                            extra_fields_dict[updated.name] = (
                                updated.name,
                                updated.type_,
                                updated.default,
                            )

            result[query_name] = {
                "standard": make_dataclass(  # type: ignore
                    cls_name=query_name,
                    fields=list(standard_fields_dict.values()),
                    bases=(StandardData,),
                ),
                "extra": make_dataclass(  # type: ignore
                    cls_name=query_name,
                    fields=list(extra_fields_dict.values()),
                    bases=(ExtraData,),
                ),
            }

        return result


__provider_interface = ProviderInterface()


def get_provider_interface() -> ProviderInterface:
    return __provider_interface
