### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import typing
from typing import Literal, Optional

from pydantic import validate_arguments

from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_stocks_dd(Container):
    @filter_call
    @validate_arguments
    def sec(
        self,
        symbol: str,
        type: Optional[str] = None,
        page: Optional[int] = 0,
        limit: Optional[int] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """SEC Filings.

        Available providers: fmp,

        Standard
        ========
        Parameter
        ---------
        symbol : str
            The symbol of the company.
        type : str
            The type of the SEC filing form. (full list: https://www.sec.gov/forms)
        page : int
            The page of the results.
        limit : int
            The limit of the results.


        Returns
        -------
        symbol : str
            The symbol of the stock.
        filling_date : date
            The filling date of the SEC filing.
        accepted_date : date
            The accepted date of the SEC filing.
        cik : str
            The CIK of the SEC filing.
        type : str
            The type of the SEC filing.
        link : str
            The link of the SEC filing.
        final_link : str
            The final link of the SEC filing.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/sec-filings-api/

        Parameter
        ---------
            The type of the SEC filing form. (full list: https://www.sec.gov/forms)

        Returns
        -------
        Documentation not available.
        """
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "type": type,
                "page": page,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/dd/sec",
            **inputs,
        ).output

        return filter_output(o)
