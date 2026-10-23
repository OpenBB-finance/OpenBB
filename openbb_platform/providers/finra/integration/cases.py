"""The FINRA commands and parameters both consumption surfaces are exercised with."""

COMMANDS = [
    ("equity.search", "EQUITY_INSTALLED", {"query": "apple"}),
    ("equity.search", "EQUITY_INSTALLED", {"query": "SPY", "security_type": "etf"}),
    ("equity.profile", "EQUITY_INSTALLED", {"symbol": "AAPL,SPY,VFIAX,BRK-B"}),
    ("equity.darkpool.otc", "EQUITY_INSTALLED", {"symbol": "AAPL"}),
    ("equity.darkpool.otc", "EQUITY_INSTALLED", {"tier": "T2", "is_ats": False}),
    ("equity.shorts.short_interest", "EQUITY_INSTALLED", {"symbol": "AAPL,BRK.B"}),
    (
        "fixedincome.bond_prices",
        "FIXEDINCOME_INSTALLED",
        {"cusip": "037833EH9,912810UG1"},
    ),
    ("fixedincome.bond_prices", "FIXEDINCOME_INSTALLED", {"issuer_name": "apple inc"}),
    (
        "fixedincome.bond_prices",
        "FIXEDINCOME_INSTALLED",
        {"bond_type": "TBA", "issuer_name": "ginnie", "limit": 10},
    ),
    ("fixedincome.bond_historical", None, {"cusip": "037833EH9"}),
    ("fixedincome.bonds", None, {"bond_type": "TS"}),
    ("fixedincome.bonds", None, {"bond_type": "ABS"}),
    ("equity.securities", None, {}),
    ("equity.securities", None, {"security_type": "closed_end_fund"}),
]

STANDARD_PATHS = {
    "fixedincome.bond_prices": "fixedincome.corporate.bond_prices",
}


def path(command: str, owner: str | None) -> list[str]:
    """Return where a command is served: the shared namespace or FINRA's own."""
    import openbb_finra

    if owner and getattr(openbb_finra, owner):
        return STANDARD_PATHS.get(command, command).split(".")

    return ["finra", *command.split(".")]


def case_id(case: tuple) -> str:
    """Name a parametrized case by its command and parameters."""
    command, _owner, params = case
    written = ",".join(f"{key}={value}" for key, value in params.items())

    return f"{command}[{written}]"
