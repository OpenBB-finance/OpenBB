from typing import Dict, Generic, List, Optional, TypeVar

import pandas as pd
from pydantic import Field
from pydantic.generics import GenericModel

from openbb_sdk_core.app.model.abstract.error import Error
from openbb_sdk_core.app.model.abstract.tagged import Tagged
from openbb_sdk_core.app.model.abstract.warning import Warning_
from openbb_sdk_core.app.provider_interface import get_provider_interface

T = TypeVar("T")
PROVIDERS = get_provider_interface().providers


class CommandOutput(GenericModel, Generic[T], Tagged):
    results: Optional[T] = Field(
        default=None,
        description="Serializable results.",
    )
    provider: Optional[PROVIDERS] = Field(  # type: ignore
        default=None,
        description="Provider name.",
    )
    warnings: Optional[List[Warning_]] = None
    error: Optional[Error] = None

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + "\n\n"
            + "\n".join([f"{k}: {v}" for k, v in self.dict().items()])
        )

    def to_dataframe(self) -> pd.DataFrame:
        """Converts results field to pandas dataframe.

        Returns
        -------
        pd.DataFrame
            Pandas dataframe.
        """
        if self.results is None:
            raise ValueError("Results not found.")

        try:
            df = pd.DataFrame(self.dict()["results"])
            if "date" in df.columns:
                df = df.set_index("date")
        except ValueError:
            df = pd.DataFrame(self.dict()["results"], index=["values"]).T

        return df

    def to_dict(self) -> Dict[str, List]:
        """Converts results field to list of values.

        Returns
        -------
        Dict[str, List]
            Dictionary of lists.
        """
        df = self.to_dataframe()
        results = {}
        for field in df.columns:
            results[field] = df[field].tolist()

        return results
