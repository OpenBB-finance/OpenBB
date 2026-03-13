"""FMP Earnings Call Transcript Model."""

# pylint: disable=unused-argument
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.earnings_call_transcript import (
    EarningsCallTranscriptData,
    EarningsCallTranscriptQueryParams,
)
from pydantic import ConfigDict


class FMPEarningsCallTranscriptQueryParams(EarningsCallTranscriptQueryParams):
    """FMP Earnings Call Transcript Query.

    Source: https://site.financialmodelingprep.com/developer/docs/earning-call-transcript-api/
    """


class FMPEarningsCallTranscriptData(EarningsCallTranscriptData):
    """FMP Earnings Call Transcript Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Earnings Call Transcript",
                "$.description": "Earnings calls by symbol, year, and quarter.",
                "$.type": "markdown",
                "$.gridData": {
                    "h": 20,
                    "w": 40,
                },
                "$.data": {
                    "dataKey": "results.content",
                },
                "$.params": [
                    {
                        "paramName": "year",
                        "label": "Fiscal Year",
                        "type": "number",
                        "description": "Fiscal year of the earnings call transcript."
                        + " When not provided, or not available, the most recent will be used.",
                    },
                    {
                        "paramName": "quarter",
                        "label": "Fiscal Quarter",
                        "description": "Fiscal quarter of the earnings call transcript."
                        + " When not provided, the latest quarter available will be used.",
                    },
                ],
                "$.refetchInterval": False,
            }
        }
    )

    __alias_dict__ = {
        "quarter": "period",
    }


class FMPEarningsCallTranscriptFetcher(
    Fetcher[
        FMPEarningsCallTranscriptQueryParams,
        FMPEarningsCallTranscriptData,
    ]
):
    """FMP Earnings Call Transcript Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPEarningsCallTranscriptQueryParams:
        """Transform the query params."""
        return FMPEarningsCallTranscriptQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEarningsCallTranscriptQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import warnings  # noqa
        from openbb_fmp.utils.helpers import (
            get_available_transcript_symbols,
            get_data_one,
            get_transcript_dates_for_symbol,
        )
        from pandas import DataFrame

        api_key = credentials.get("fmp_api_key") if credentials else ""

        available_symbols = get_available_transcript_symbols(api_key=api_key)
        avail_df = DataFrame(available_symbols)

        if query.symbol.upper() not in avail_df["symbol"].values:
            raise OpenBBError(
                ValueError(
                    f"Symbol {query.symbol} not found in available transcripts."
                    + f"\n Available symbols include: {', '.join(sorted(avail_df['symbol'].unique().tolist()))}"
                )
            )
        symbol_transcripts = get_transcript_dates_for_symbol(
            query.symbol.upper(), api_key=api_key
        )

        df_dates = DataFrame(symbol_transcripts).sort_values(by="date", ascending=False)
        year = df_dates.iloc[0].fiscalYear

        if query.year and query.year not in df_dates.fiscalYear.values:
            warnings.warn(
                f"Year {query.year} not found in available transcripts for {query.symbol}."
                + f" Using latest year {year} instead."
            )

        year = query.year if query.year in df_dates.fiscalYear.values else year

        quarter = query.quarter if query.quarter else df_dates.iloc[0].quarter

        if (
            query.quarter
            and query.quarter
            not in df_dates.query("fiscalYear == @year").quarter.values
        ):
            warnings.warn(
                f"Quarter {query.quarter} not found in available transcripts for {query.symbol} in {year}."
                + f" Using latest quarter q{df_dates.query('fiscalYear == @year').iloc[0].quarter} instead."
            )

        url = (
            "https://financialmodelingprep.com/stable/earning-call-transcript?symbol="
            + f"{query.symbol.upper()}&year={year}&quarter={quarter}&apikey={api_key}"
        )

        try:
            return await get_data_one(url, **kwargs)
        except ValueError as e:
            raise OpenBBError(
                f"No transcript found for {query.symbol} in {year} Q{quarter}"
                f". \n Latest available transcript is {df_dates.iloc[0].fiscalYear} Q{df_dates.iloc[0].quarter}."
            ) from e

    @staticmethod
    def transform_data(
        query: FMPEarningsCallTranscriptQueryParams, data: dict, **kwargs: Any
    ) -> FMPEarningsCallTranscriptData:
        """Return the transformed data."""
        if not data:
            raise OpenBBError(
                ValueError(
                    f"No data found for {query.symbol} for year {query.year} and period {query.quarter}."
                )
            )
        transcript = data.get("content", "")

        output_lines: list = []
        intro_lines = f"""
## {data.get("symbol")} - {data.get("year")} {data.get("period")} Earnings Call Transcript - {data.get("date")}
\n\n
"""
        output_lines.append(intro_lines + "\n\n")
        for line in transcript.splitlines():
            section_title = line.split(":", 1)[0] if ":" in line else ""
            section_line = line.split(":", 1)[1] if ":" in line else ""
            if section_title and section_line:
                output_lines.append(f"### **{section_title.strip()}**:" + "\n\n")
                output_lines.append(section_line.strip() + "\n\n")
            else:
                output_lines.append(line)

        data["content"] = "\n".join(output_lines)

        return FMPEarningsCallTranscriptData.model_validate(data)
