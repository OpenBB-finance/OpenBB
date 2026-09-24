"""Daily Treasury Statement Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator

from openbb_government_us.utils.serializers import OmitNoneMixin

api_prefix = SystemService().system_settings.api_settings.prefix

ENDPOINT = "v1/accounting/dts"
ALL_SUB_TABLES = "all"
ALL_BASES = "all"
OPTIONS_LOOKBACK_DAYS = 30

DtsTable = Literal[
    "operating_cash_balance",
    "deposits_withdrawals_operating_cash",
    "public_debt_transactions",
    "adjustment_public_debt_transactions_cash_basis",
    "debt_subject_to_limit",
    "federal_tax_deposits",
    "short_term_cash_investments",
    "income_tax_refunds_issued",
    "inter_agency_tax_transfers",
]

COMMON_FIELDS = {
    "record_date": "date",
    "table_nbr": "table_number",
    "table_nm": "table_name",
    "src_line_nbr": "line_number",
}

FIELD_MAP: dict[str, dict[str, str]] = {
    "operating_cash_balance": {
        **COMMON_FIELDS,
        "sub_table_name": "sub_table_name",
        "account_type": "account_type",
        "close_today_bal": "close_today_balance",
        "open_today_bal": "open_today_balance",
        "open_month_bal": "open_month_balance",
        "open_fiscal_year_bal": "open_fiscal_year_balance",
    },
    "deposits_withdrawals_operating_cash": {
        **COMMON_FIELDS,
        "account_type": "account_type",
        "transaction_type": "transaction_type",
        "transaction_catg": "category",
        "transaction_catg_desc": "category_description",
        "transaction_today_amt": "today_amount",
        "transaction_mtd_amt": "month_to_date_amount",
        "transaction_fytd_amt": "fiscal_year_to_date_amount",
    },
    "public_debt_transactions": {
        **COMMON_FIELDS,
        "transaction_type": "transaction_type",
        "security_market": "security_market",
        "security_type": "security_type",
        "security_type_desc": "security_type_description",
        "transaction_today_amt": "today_amount",
        "transaction_mtd_amt": "month_to_date_amount",
        "transaction_fytd_amt": "fiscal_year_to_date_amount",
    },
    "adjustment_public_debt_transactions_cash_basis": {
        **COMMON_FIELDS,
        "sub_table_name": "sub_table_name",
        "transaction_type": "transaction_type",
        "adj_type": "category",
        "adj_type_desc": "category_description",
        "adj_today_amt": "today_amount",
        "adj_mtd_amt": "month_to_date_amount",
        "adj_fytd_amt": "fiscal_year_to_date_amount",
    },
    "debt_subject_to_limit": {
        **COMMON_FIELDS,
        "sub_table_name": "sub_table_name",
        "debt_catg": "category",
        "debt_catg_desc": "category_description",
        "close_today_bal": "close_today_balance",
        "open_today_bal": "open_today_balance",
        "open_month_bal": "open_month_balance",
        "open_fiscal_year_bal": "open_fiscal_year_balance",
    },
    "federal_tax_deposits": {
        **COMMON_FIELDS,
        "sub_table_name": "sub_table_name",
        "tax_deposit_type": "category",
        "tax_deposit_type_desc": "category_description",
        "tax_deposit_today_amt": "today_amount",
        "tax_deposit_mtd_amt": "month_to_date_amount",
        "tax_deposit_fytd_amt": "fiscal_year_to_date_amount",
    },
    "short_term_cash_investments": {
        **COMMON_FIELDS,
        "sub_table_name": "sub_table_name",
        "transaction_type": "transaction_type",
        "transaction_type_desc": "category_description",
        "depositary_type_a_amt": "depositary_type_a_amount",
        "depositary_type_b_amt": "depositary_type_b_amount",
        "depositary_type_c_amt": "depositary_type_c_amount",
        "total_amt": "total_amount",
    },
    "income_tax_refunds_issued": {
        **COMMON_FIELDS,
        "sub_table_name": "sub_table_name",
        "tax_refund_type": "category",
        "tax_refund_type_desc": "category_description",
        "tax_refund_today_amt": "today_amount",
        "tax_refund_mtd_amt": "month_to_date_amount",
        "tax_refund_fytd_amt": "fiscal_year_to_date_amount",
    },
    "inter_agency_tax_transfers": {
        **COMMON_FIELDS,
        "sub_table_name": "sub_table_name",
        "classification": "category",
        "today_amt": "today_amount",
        "mtd_amt": "month_to_date_amount",
        "fytd_amt": "fiscal_year_to_date_amount",
    },
}

AMOUNT_FIELDS = {
    "today_amount",
    "month_to_date_amount",
    "fiscal_year_to_date_amount",
    "close_today_balance",
    "open_today_balance",
    "open_month_balance",
    "open_fiscal_year_balance",
    "depositary_type_a_amount",
    "depositary_type_b_amount",
    "depositary_type_c_amount",
    "total_amount",
}

PIVOT_DIMS: dict[str, tuple[str, ...]] = {
    "operating_cash_balance": ("sub_table_name", "account_type"),
    "deposits_withdrawals_operating_cash": (
        "account_type",
        "transaction_type",
        "category",
        "category_description",
    ),
    "public_debt_transactions": (
        "transaction_type",
        "security_market",
        "security_type",
        "security_type_description",
    ),
    "adjustment_public_debt_transactions_cash_basis": (
        "sub_table_name",
        "transaction_type",
        "category",
        "category_description",
    ),
    "debt_subject_to_limit": ("sub_table_name", "category", "category_description"),
    "federal_tax_deposits": ("sub_table_name", "category", "category_description"),
    "short_term_cash_investments": (
        "sub_table_name",
        "transaction_type",
        "category_description",
    ),
    "income_tax_refunds_issued": ("sub_table_name", "category", "category_description"),
    "inter_agency_tax_transfers": ("sub_table_name", "category"),
}

SUB_TABLE_FIELD: dict[str, str] = {
    "operating_cash_balance": "sub_table_name",
    "deposits_withdrawals_operating_cash": "transaction_type",
    "public_debt_transactions": "transaction_type",
    "adjustment_public_debt_transactions_cash_basis": "transaction_type",
    "debt_subject_to_limit": "sub_table_name",
    "federal_tax_deposits": "sub_table_name",
    "short_term_cash_investments": "sub_table_name",
    "income_tax_refunds_issued": "sub_table_name",
    "inter_agency_tax_transfers": "sub_table_name",
}

DEFAULT_AMOUNT_BASIS: dict[str, str] = {
    "deposits_withdrawals_operating_cash": "Today",
    "public_debt_transactions": "Today",
}

DEFAULT_SUB_TABLE: dict[str, str] = {
    "deposits_withdrawals_operating_cash": "Deposits",
    "public_debt_transactions": "Issues",
}

LAST_RECORD_DATE: dict[str, str] = {
    "federal_tax_deposits": "2023-02-13",
    "short_term_cash_investments": "2023-02-13",
}

VALUE_LABELS: dict[str, str] = {
    "today_amount": "Today",
    "month_to_date_amount": "Month to Date",
    "fiscal_year_to_date_amount": "Fiscal Year to Date",
    "close_today_balance": "Close Today",
    "open_today_balance": "Open Today",
    "open_month_balance": "Open Month",
    "open_fiscal_year_balance": "Open Fiscal Year",
    "depositary_type_a_amount": "Depositary Type A",
    "depositary_type_b_amount": "Depositary Type B",
    "depositary_type_c_amount": "Depositary Type C",
    "total_amount": "Total",
}


def map_records(table: str, data: list[dict]) -> list[dict[str, Any]]:
    """Map source rows of one DTS table onto the model's field names.

    Parameters
    ----------
    table : str
        Key of FIELD_MAP.
    data : list[dict]
        Rows as published by the FiscalData API.

    Returns
    -------
    list[dict]
        The mapped long-format records, with amounts reported in millions
        expanded to dollars.
    """
    mapping = FIELD_MAP[table]
    records: list[dict[str, Any]] = []

    for row in data:
        record: dict[str, Any] = {}

        for source, target in mapping.items():
            if source not in row:
                continue

            value = row[source]

            if target in AMOUNT_FIELDS and value is not None:
                value = float(value) * 1_000_000

            record[target] = value

        records.append(record)

    return records


def amount_bases(table: str) -> list[str]:
    """List the amount bases a table publishes, in published order."""
    return [target for target in FIELD_MAP[table].values() if target in AMOUNT_FIELDS]


def resolve_amount_basis(table: str, amount_basis: str | None) -> list[str]:
    """Return the amount fields to spread across the line-item columns.

    Parameters
    ----------
    table : str
        Key of FIELD_MAP.
    amount_basis : str | None
        The requested basis label, 'all' for every basis, or None to take the
        table's first published basis so every line item keeps a column.

    Returns
    -------
    list[str]
        The amount fields to serve.

    Raises
    ------
    OpenBBError
        If the requested basis is not one the table publishes.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    published = amount_bases(table)

    if not amount_basis:
        default = DEFAULT_AMOUNT_BASIS.get(table)

        if not default:
            return published

        return [
            field for field in published if VALUE_LABELS[field] == default
        ] or published

    if amount_basis == ALL_BASES:
        return published

    matched = [field for field in published if VALUE_LABELS[field] == amount_basis]

    if not matched:
        raise OpenBBError(
            f"Invalid amount_basis: '{amount_basis}'. The {table} table"
            " publishes: "
            + ", ".join(VALUE_LABELS[field] for field in published)
            + f", or '{ALL_BASES}'."
        )

    return matched


def resolve_sub_table(table: str, sub_table: str | None) -> str:
    """Return the sub-table selection in effect for a table.

    Parameters
    ----------
    table : str
        Key of FIELD_MAP.
    sub_table : str | None
        The requested sub-table, or None to take the table's default.

    Returns
    -------
    str
        The requested sub-table, the table's default, or ALL_SUB_TABLES.
    """
    if sub_table:
        return sub_table

    return DEFAULT_SUB_TABLE.get(table, ALL_SUB_TABLES)


def filter_sub_table(table: str, records: list[dict], sub_table: str) -> list[dict]:
    """Keep only the records belonging to one sub-table.

    Parameters
    ----------
    table : str
        Key of FIELD_MAP.
    records : list[dict]
        The mapped long-format records.
    sub_table : str
        The sub-table value to keep, or ALL_SUB_TABLES to keep everything.

    Returns
    -------
    list[dict]
        The records of the requested sub-table.

    Raises
    ------
    EmptyDataError
        If no record carries the requested sub-table.
    """
    from openbb_core.provider.utils.errors import EmptyDataError

    if sub_table == ALL_SUB_TABLES:
        return records

    field = SUB_TABLE_FIELD[table]
    kept = [record for record in records if record.get(field) == sub_table]

    if not kept:
        available = sorted({str(record.get(field)) for record in records})
        raise EmptyDataError(
            f"No '{sub_table}' sub-table in {table}. Available -> "
            + ", ".join(available)
        )

    return kept


async def sub_table_options(table: str) -> list[dict[str, str]]:
    """List the sub-tables of one DTS table as widget options.

    Parameters
    ----------
    table : str
        Key of FIELD_MAP.

    Returns
    -------
    list[dict[str, str]]
        Widget options, the table's default selection first, ending with the
        entry that serves every sub-table at once.
    """
    from openbb_government_us.treasury.utils.fiscal_data import (
        build_filters,
        default_start_date,
        get_fiscal_data,
    )

    if table not in FIELD_MAP:
        return []

    anchor = LAST_RECORD_DATE.get(table)
    end_date = dateType.fromisoformat(anchor) if anchor else None
    filters = build_filters(
        [
            (
                "record_date",
                "gte",
                default_start_date(None, end_date, OPTIONS_LOOKBACK_DAYS),
            ),
            ("record_date", "lte", end_date),
        ]
    )
    data = await get_fiscal_data(
        f"{ENDPOINT}/{table}", filters=filters, sort="record_date"
    )
    field = SUB_TABLE_FIELD[table]
    values: list[str] = []

    for record in map_records(table, data):
        value = record.get(field)

        if value and value not in values:
            values.append(str(value))

    options = [{"label": value, "value": value} for value in values]

    options.append({"label": "All Sub-Tables", "value": ALL_SUB_TABLES})
    default = resolve_sub_table(table, None)
    options.sort(key=lambda option: option["value"] != default)

    return options


class DailyTreasuryStatementQueryParams(QueryParams):
    """Daily Treasury Statement Query Parameters.

    Source: https://fiscaldata.treasury.gov/datasets/daily-treasury-statement/
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "multiSelect": False,
                "multiple": False,
                "style": {"popupWidth": 420},
            },
        },
        "sub_table": {
            "x-widget_config": {
                "label": "Sub-Table",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/ustreasury/dts_sub_tables",
                "optionsParams": {"table": "$table"},
                "style": {"popupWidth": 420},
            },
        },
        "amount_basis": {
            "x-widget_config": {
                "label": "Amount Basis",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/ustreasury/dts_amount_bases",
                "optionsParams": {"table": "$table"},
                "style": {"popupWidth": 320},
            },
        },
    }

    table: DtsTable = Field(
        default="operating_cash_balance",
        description="The DTS table to query."
        + " federal_tax_deposits and short_term_cash_investments are"
        + " discontinued, frozen at 2023-02-13;"
        + " inter_agency_tax_transfers begins 2023-02-14.",
    )
    sub_table: str | None = Field(
        default=None,
        description="The sub-table of the selected table to spread into columns,"
        + " as published, e.g. 'Deposits' or 'Issues'. Use 'all' to combine every"
        + " sub-table. When None, deposits_withdrawals_operating_cash defaults to"
        + " 'Deposits' and public_debt_transactions to 'Issues', because those"
        + " tables are too wide to read whole; every other table defaults to"
        + " 'all'.",
    )
    amount_basis: str | None = Field(
        default=None,
        description="Which reported amount to spread across the line-item"
        + " columns, as published, e.g. 'Today', 'Month to Date', or 'Fiscal"
        + " Year to Date'. Selecting one basis keeps a column per line item."
        + " When None, the two tables that publish enough line items to be"
        + " unreadable across every basis default to 'Today' and the rest serve"
        + " every basis they publish. Use 'all' to force every basis.",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Data begins 2005-10-03. When None, defaults to the trailing 30 days"
        + " rather than the full history; set it explicitly to reach further"
        + " back.",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )

    @field_validator("sub_table", mode="before", check_fields=False)
    @classmethod
    def _strip_sub_table(cls, v):
        """Strip the sub-table selection to None when empty."""
        if not isinstance(v, str):
            return v

        return v.strip() or None


class DailyTreasuryStatementData(OmitNoneMixin, Data):
    """Daily Treasury Statement Data.

    One row per statement date, newest first, with each published line item
    of the requested table and sub-table spread into its own column. A column
    is labelled by its line item and suffixed with the amount it reports, e.g.
    'Treasury General Account (TGA) Closing Balance (Open Today)'. Dollar
    amounts reported by the source in millions are expanded to dollars.
    """

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
    )


class DailyTreasuryStatementFetcher(
    Fetcher[
        DailyTreasuryStatementQueryParams,
        list[DailyTreasuryStatementData],
    ]
):
    """Fetch the Daily Treasury Statement from the FiscalData API."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DailyTreasuryStatementQueryParams:
        """Transform the query params."""
        return DailyTreasuryStatementQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DailyTreasuryStatementQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the FiscalData API."""
        from openbb_government_us.treasury.utils.fiscal_data import (
            build_filters,
            default_start_date,
            get_fiscal_data,
        )

        anchor = LAST_RECORD_DATE.get(query.table)
        end_date = query.end_date or (
            dateType.fromisoformat(anchor) if anchor else None
        )
        start_date = default_start_date(query.start_date, end_date, 30)
        filters = build_filters(
            [
                ("record_date", "gte", start_date),
                ("record_date", "lte", end_date),
            ]
        )

        return await get_fiscal_data(
            f"{ENDPOINT}/{query.table}", filters=filters, sort="record_date"
        )

    @staticmethod
    def transform_data(
        query: DailyTreasuryStatementQueryParams, data: list[dict], **kwargs: Any
    ) -> list[DailyTreasuryStatementData]:
        """Transform the data."""
        sub_table = resolve_sub_table(query.table, query.sub_table)
        records = filter_sub_table(
            query.table, map_records(query.table, data), sub_table
        )

        return DailyTreasuryStatementFetcher._pivot(
            query.table, records, query.amount_basis, sub_table
        )

    @staticmethod
    def _pivot(
        table: str,
        records: list[dict],
        amount_basis: str | None = None,
        sub_table: str = ALL_SUB_TABLES,
    ) -> list[DailyTreasuryStatementData]:
        """Pivot the long statement rows into one row per statement date.

        Parameters
        ----------
        table : str
            Key of FIELD_MAP.
        records : list[dict]
            The mapped long-format records.
        amount_basis : str | None
            Cap on the number of served columns, counting the date column.
            When the line items overflow it, the largest by reported value are
            kept and a warning names how many were left out. None or 0 serves
            every line item.
        sub_table : str
            The sub-table the records were narrowed to, left out of the column
            labels because every column shares it.

        Returns
        -------
        list[DailyTreasuryStatementData]
            One row per statement date, newest first, with each line item
            spread into its own value column.
        """
        candidates = (
            tuple(
                dimension
                for dimension in PIVOT_DIMS[table]
                if dimension != SUB_TABLE_FIELD[table]
            )
            if sub_table != ALL_SUB_TABLES
            else PIVOT_DIMS[table]
        ) or PIVOT_DIMS[table]
        varying = tuple(
            dimension
            for dimension in candidates
            if len(
                {record.get(dimension) for record in records if record.get(dimension)}
            )
            > 1
        )
        dimensions = varying or candidates
        values = resolve_amount_basis(table, amount_basis)
        multi_basis = len(values) > 1
        pivoted: dict[Any, dict[str, Any]] = {}
        columns: list[str] = []

        for record in records:
            date = record.get("date")

            if date is None:
                continue

            row = pivoted.setdefault(date, {"date": date})
            parts: list[str] = []

            for dimension in dimensions:
                value = record.get(dimension)

                if value in (None, "") or (parts and str(value) == parts[-1]):
                    continue

                parts.append(str(value))

            label = " - ".join(parts)

            if not label:
                continue

            for value in values:
                amount = record.get(value)

                if amount is None:
                    continue

                column = f"{label} ({VALUE_LABELS[value]})" if multi_basis else label

                if column not in columns:
                    columns.append(column)

                row[column] = amount

        ordered = sorted(pivoted.values(), key=lambda row: row["date"], reverse=True)

        return [
            DailyTreasuryStatementData.model_validate(
                {
                    "date": row["date"],
                    **{column: row.get(column) for column in columns},
                }
            )
            for row in ordered
        ]
