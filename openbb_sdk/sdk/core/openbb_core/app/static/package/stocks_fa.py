### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
import typing
from typing import List, Literal, Optional, Union

import openbb_provider
from pydantic import validate_arguments

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_stocks_fa(Container):
    @filter_call
    @validate_arguments
    def analysis(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Analyse SEC filings with the help of machine learning."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/analysis",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def balance(
        self,
        symbol: Optional[str] = None,
        period: Literal["annual", "quarter"] = "annual",
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Balance Sheet."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "period": period,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/balance",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def cal(
        self,
        start_date: Union[datetime.date, None, str] = None,
        end_date: Union[datetime.date, None, str] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Show Dividend Calendar for a given start and end dates."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/cal",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def cash(
        self,
        symbol: Optional[str] = None,
        period: Literal["annual", "quarter"] = "annual",
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Cash Flow Statement."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "period": period,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/cash",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def comp(
        self,
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Executive Compensation."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/comp",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def comsplit(
        self,
        start_date: Union[datetime.date, str],
        end_date: Union[datetime.date, str],
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Stock Split Calendar."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/comsplit",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def customer(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """List of customers of the company."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/customer",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def dcfc(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Determine the (historical) discounted cash flow."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/dcfc",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def divs(
        self,
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Historical Dividends."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/divs",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def dupont(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Detailed breakdown for Return on Equity (RoE)."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/dupont",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def earning(
        self,
        symbol: str,
        limit: Optional[int] = 50,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Earnings Calendar."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/earning",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def emp(
        self,
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Number of Employees."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/emp",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def enterprise(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Enterprise value."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/enterprise",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def epsfc(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Earnings Estimate by Analysts - EPS."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/epsfc",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def est(
        self,
        symbol: str,
        period: Literal["quarterly", "annually"] = "annually",
        limit: int = 30,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Analyst Estimates."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "period": period,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/est",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def fama_coe(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Fama French 3 Factor Model - Coefficient of Earnings."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/fama_coe",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def fama_raw(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Fama French 3 Factor Model - Raw Data."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/fama_raw",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def fraud(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Key fraud ratios including M-score, Z-score and McKee."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/fraud",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def growth(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Growth of financial statement items and ratios."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/growth",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def historical_5(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/historical_5",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def income(
        self,
        symbol: Optional[str] = None,
        period: Literal["annual", "quarter"] = "annual",
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Income Statement."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "period": period,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/income",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def ins(
        self,
        transactionType: List[
            openbb_provider.models.stock_insider_trading.TransactionTypes
        ] = [],
        symbol: Optional[str] = None,
        reportingCik: Optional[int] = None,
        companyCik: Optional[int] = None,
        page: int = 0,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Stock Insider Trading."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "transactionType": transactionType,
                "symbol": symbol,
                "reportingCik": reportingCik,
                "companyCik": companyCik,
                "page": page,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/ins",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def key(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/key",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def metrics(
        self,
        symbol: str,
        period: Literal["quarter", "annual"] = "annual",
        limit: Optional[int] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Key Metrics."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "period": period,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/metrics",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def mgmt(
        self,
        symbol: str,
        key_executive_name: Optional[str] = None,
        key_executive_title: Optional[str] = None,
        key_executive_title_since: Optional[datetime.datetime] = None,
        key_executive_year_born: Optional[datetime.datetime] = None,
        key_executive_gender: Optional[str] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Key Executives."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "key_executive_name": key_executive_name,
                "key_executive_title": key_executive_title,
                "key_executive_title_since": key_executive_title_since,
                "key_executive_year_born": key_executive_year_born,
                "key_executive_gender": key_executive_gender,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/mgmt",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def mktcap(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Obtain the market capitalization or enterprise value."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/mktcap",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def news(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/news",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def overview(
        self,
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Company Overview."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/overview",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def own(
        self,
        symbol: str,
        date: Optional[datetime.date] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Institutional Ownership."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "date": date,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/own",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def pt(
        self,
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Price Target Consensus."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/pt",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def pta(
        self,
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Price Target."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/pta",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def rating(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Analyst prices and ratings over time of the company."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/rating",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def ratios(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Extensive set of ratios over time."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/ratios",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def revfc(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Earning Estimate by Analysts - Revenue."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/revfc",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def revgeo(
        self,
        symbol: str,
        period: Literal["quarterly", "annually"] = "quarterly",
        structure: Literal["hierarchical", "flat"] = "flat",
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Revenue Geographic."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "period": period,
                "structure": structure,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/revgeo",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def revseg(
        self,
        symbol: str,
        period: Literal["quarterly", "annually"] = "quarterly",
        structure: Literal["hierarchical", "flat"] = "flat",
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Revenue Business Line."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "period": period,
                "structure": structure,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/revseg",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def rot(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Number of analyst ratings over time on a monthly basis."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/rot",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def score(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Value investing scores for any time period."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/score",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def sec(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/sec",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def shares(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/shares",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def shrs(
        self,
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Share Statistics."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/shrs",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def split(
        self,
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Historical Stock Splits."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/split",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def supplier(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """List of suppliers of the company."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/supplier",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def transcript(
        self,
        symbol: str,
        year: int,
        quarter: Literal[1, 2, 3, 4] = 1,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Earnings Call Transcript."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "year": year,
                "quarter": quarter,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/transcript",
            **inputs,
        ).output

        return filter_output(o)
