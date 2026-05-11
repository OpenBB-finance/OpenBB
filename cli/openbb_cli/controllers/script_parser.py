"""Routine functions for OpenBB Platform CLI."""

import re
from datetime import datetime, timedelta
from re import Match

from dateutil.relativedelta import relativedelta

from openbb_cli.session import Session

session = Session()


MONTHS_VALUE = {
    "JANUARY": 1,
    "FEBRUARY": 2,
    "MARCH": 3,
    "APRIL": 4,
    "MAY": 5,
    "JUNE": 6,
    "JULY": 7,
    "AUGUST": 8,
    "SEPTEMBER": 9,
    "OCTOBER": 10,
    "NOVEMBER": 11,
    "DECEMBER": 12,
}

WEEKDAY_VALUE = {
    "MONDAY": 0,
    "TUESDAY": 1,
    "WEDNESDAY": 2,
    "THURSDAY": 3,
    "FRIDAY": 4,
    "SATURDAY": 5,
    "SUNDAY": 6,
}


def is_reset(command: str) -> bool:
    """Test whether a command is a reset command.

    Parameters
    ----------
    command : str
        The command to test

    Returns
    -------
    answer : bool
        Whether the command is a reset command
    """
    if "reset" in command:
        return True
    return command in ("r", "r\n")


def match_and_return_openbb_keyword_date(keyword: str) -> str:  # noqa: PLR0911
    """Return OpenBB keyword into date.

    Parameters
    ----------
    keyword : str
        String with potential OpenBB keyword (e.g. 1MONTHAGO,LASTFRIDAY,3YEARSFROMNOW,NEXTTUESDAY)

    Returns
    -------
        str: Date with format YYYY-MM-DD
    """
    now = datetime.now()
    for i, regex in enumerate([r"^\$(\d+)([A-Z]+)AGO$", r"^\$(\d+)([A-Z]+)FROMNOW$"]):
        match = re.match(regex, keyword)
        if match:
            integer_value = int(match.group(1))
            time_unit = match.group(2)
            clean_time = time_unit.upper()
            if "DAYS" in clean_time or "MONTHS" in clean_time or "YEARS" in clean_time:
                kwargs = {time_unit.lower(): integer_value}
                if i == 0:
                    return (now - relativedelta(**kwargs)).strftime("%Y-%m-%d")  # ty: ignore[invalid-argument-type]
                return (now + relativedelta(**kwargs)).strftime("%Y-%m-%d")  # ty: ignore[invalid-argument-type]

    match = re.search(r"\$LAST(\w+)", keyword)
    if match:
        time_unit = match.group(1)
        if time_unit in list(MONTHS_VALUE.keys()):
            the_year = now.year
            if now.month <= MONTHS_VALUE[time_unit]:
                the_year = now.year - 1
            return datetime(the_year, MONTHS_VALUE[time_unit], 1).strftime("%Y-%m-%d")

        if time_unit in list(WEEKDAY_VALUE.keys()):
            if datetime.weekday(now) > WEEKDAY_VALUE[time_unit]:
                return (
                    now
                    - timedelta(datetime.weekday(now))
                    + timedelta(WEEKDAY_VALUE[time_unit])
                ).strftime("%Y-%m-%d")
            return (
                now
                - timedelta(7)
                - timedelta(datetime.weekday(now))
                + timedelta(WEEKDAY_VALUE[time_unit])
            ).strftime("%Y-%m-%d")

    match = re.search(r"\$NEXT(\w+)", keyword)
    if match:
        time_unit = match.group(1)
        if time_unit in list(MONTHS_VALUE.keys()):
            if now.month < MONTHS_VALUE[time_unit]:
                return datetime(now.year, MONTHS_VALUE[time_unit], 1).strftime(
                    "%Y-%m-%d"
                )

            return datetime(now.year + 1, MONTHS_VALUE[time_unit], 1).strftime(
                "%Y-%m-%d"
            )

        if time_unit in list(WEEKDAY_VALUE.keys()):
            if datetime.weekday(now) < WEEKDAY_VALUE[time_unit]:
                return (
                    now
                    - timedelta(datetime.weekday(now))
                    + timedelta(WEEKDAY_VALUE[time_unit])
                ).strftime("%Y-%m-%d")
            return (
                now
                + timedelta(7)
                - timedelta(datetime.weekday(now))
                + timedelta(WEEKDAY_VALUE[time_unit])
            ).strftime("%Y-%m-%d")

    return ""


def parse_openbb_script(  # noqa: PLR0911,PLR0912
    raw_lines: list[str],
    script_inputs: list[str] | None = None,
) -> tuple[str, str]:
    """Parse .openbb script.

    Parameters
    ----------
    raw_lines : List[str]
        Lines from .openbb script
    script_inputs: str, optional
        Inputs to the script that come externally

    Returns
    -------
    str
        Error that occurred - if empty means no error
    str
        Processed string from .openbb script that can be run by the OpenBB Platform CLI
    """
    ROUTINE_VARS: dict[str, str | list[str]] = dict()
    if script_inputs:
        ROUTINE_VARS["$ARGV"] = script_inputs

    raw_lines = [
        x.strip()
        for x in raw_lines
        if (not is_reset(x)) and ("#" not in x) and x.strip()
    ]

    lines_without_declarations = list()
    for line in raw_lines:
        if "$" in line and "=" in line:
            match = re.search(r"\$(\w+)\s*=\s*([\w\d,-.\s]+)", line)
            if match:
                VAR_NAME = match.group(1)
                VAR_VALUES = match.group(2)
                ROUTINE_VARS["$" + VAR_NAME] = (
                    VAR_VALUES if "," not in VAR_VALUES else VAR_VALUES.split(",")
                )

                numdollars = len(re.findall(r"\$", line))
                if numdollars > 1:
                    session.console.print(
                        f"The variable {VAR_NAME} should not be declared as "
                        f"{'$' * numdollars}{VAR_NAME}. Instead it will be "
                        f"converted into ${VAR_NAME}."
                    )

            else:
                lines_without_declarations.append(line)
        else:
            lines_without_declarations.append(line)

    lines_with_vars_replaced = list()
    foreach_loop_found = False
    for line in lines_without_declarations:
        templine = line

        if re.match(r"^\s*end\s*$", line, re.IGNORECASE):
            if not foreach_loop_found:
                return (
                    "[red]The script has a foreach loop that terminates before it gets started. "
                    "Add the keyword 'foreach' to explicitly start loop[/red]",
                    "",
                )
            foreach_loop_found = False

        else:
            if re.search(r"foreach", line, re.IGNORECASE):
                foreach_loop_found = True

            pattern = r"(?<!\$)(\$(\w+)(\[[^\]]*\])?)(?=(?:[^\]]*\]*))"

            matches: list[Match[str]] | None = re.findall(pattern, line)

            if matches:
                for match in matches:
                    if match:
                        VAR_NAME = "$" + match[1]
                        VAR_SLICE = match[2][1:-1] if match[2] else ""

                        if VAR_SLICE.isdigit():
                            if VAR_SLICE == "0":
                                if VAR_NAME in ROUTINE_VARS:
                                    values = ROUTINE_VARS[VAR_NAME]
                                    if isinstance(values, list):
                                        templine = templine.replace(
                                            match[0],
                                            values[int(VAR_SLICE)],
                                        )
                                    else:
                                        templine = templine.replace(match[0], values)
                                else:
                                    return (
                                        f"[red]Variable {VAR_NAME} not given for current routine script.[/red]",
                                        "",
                                    )

                            elif VAR_NAME in ROUTINE_VARS:
                                variable = ROUTINE_VARS[VAR_NAME]
                                length_variable = (
                                    len(variable) if isinstance(variable, list) else 1
                                )

                                if length_variable <= int(VAR_SLICE):
                                    return (
                                        f"[red]Variable {VAR_NAME} only has "
                                        f"{length_variable} elements and there "
                                        f"was an attempt to access it with index {VAR_SLICE}.[/red]",
                                        "",
                                    )
                                templine = templine.replace(
                                    match[0],
                                    variable[int(VAR_SLICE)],
                                )
                            else:
                                return (
                                    f"[red]Variable {VAR_NAME} not given for current routine script.[/red]",
                                    "",
                                )

                        elif (
                            ":" in VAR_SLICE
                            and len(VAR_SLICE.split(":")) == 2
                            and (
                                VAR_SLICE.split(":")[0].isdigit()
                                or VAR_SLICE.split(":")[1].isdigit()
                            )
                        ):
                            parts = VAR_SLICE.split(":")
                            start = (
                                int(parts[0])
                                if parts[0] and parts[0].lstrip("-").isdigit()
                                else None
                            )
                            stop = (
                                int(parts[1])
                                if len(parts) > 1
                                and parts[1]
                                and parts[1].lstrip("-").isdigit()
                                else None
                            )
                            vars_to_loop = ROUTINE_VARS[VAR_NAME][slice(start, stop)]

                            if vars_to_loop:
                                templine = templine.replace(
                                    match[0],
                                    ",".join(vars_to_loop),
                                )
                            else:
                                return (
                                    f"[red]The foreach loop cannot run with input: {match[0]}.[/red]",
                                    "",
                                )

                        else:
                            if VAR_SLICE:
                                if VAR_SLICE.startswith("-"):
                                    if not VAR_SLICE[1:].isdigit():
                                        return (
                                            f"[red]Index '{VAR_SLICE}' is not a value[/red]",
                                            "",
                                        )
                                    if int(VAR_SLICE) < 0:
                                        return (
                                            f"[red]Negative index on {VAR_NAME} is not allowed[/red]",
                                            "",
                                        )
                                if not VAR_SLICE.isdigit():
                                    return (
                                        f"[red]Index '{VAR_SLICE}' is not a value[/red]",
                                        "",
                                    )

                            if VAR_NAME in ROUTINE_VARS:
                                value = ROUTINE_VARS[VAR_NAME]

                                if isinstance(value, list):
                                    templine = templine.replace(
                                        match[0],
                                        ",".join(value),
                                    )
                                else:
                                    templine = templine.replace(match[0], value)

                            else:
                                potential_date_match = (
                                    match_and_return_openbb_keyword_date(VAR_NAME)
                                )
                                if potential_date_match:
                                    templine = templine.replace(
                                        match[0], potential_date_match
                                    )
                                else:
                                    return (
                                        f"[red]Variable {VAR_NAME} not given for current routine script.[/red]",
                                        "",
                                    )

        lines_with_vars_replaced.append(templine)

    if foreach_loop_found:
        return (
            "[red]The script has a foreach loop that doesn't terminate. "
            "Add the keyword 'end' to explicitly terminate loop[/red]",
            "",
        )

    within_foreach = False
    foreach_lines_loop: list[str] = list()

    parsed_script = ""
    final_lines = list()
    varname = "VAR"
    varused_inside = False
    for line in lines_with_vars_replaced:
        match = re.search(
            r"foreach \$\$([A-Za-z\_]+) in ([A-Za-z0-9,-.]+)", line, re.IGNORECASE
        )
        if match:
            varname = match.group(1)
            foreach_loop = match.group(2).split(",")
            within_foreach = True

        elif within_foreach:
            if re.match(r"^\s*end\s*$", line, re.IGNORECASE):
                for var in foreach_loop:
                    for foreach_line_loop in foreach_lines_loop:
                        if f"$${varname}" in foreach_line_loop:
                            final_lines.append(
                                foreach_line_loop.replace(f"$${varname}", var).strip()
                            )
                            varused_inside = True
                        elif "$$" in foreach_line_loop:
                            return (
                                "[red]The script has a foreach loop that iterates through "
                                f"{','.join(foreach_loop)} with variable $${varname} "
                                "but another var name is being utilized instead[/red]",
                                "",
                            )
                        else:
                            final_lines.append(foreach_line_loop.strip())

                if not varused_inside:
                    session.console.print(
                        f"The variable {varname} was used in foreach header but it wasn't used inside the loop."
                    )
                    varused_inside = False

                within_foreach = False
                foreach_lines_loop = list()

            else:
                foreach_lines_loop.append(line)

        else:
            final_lines.append(line)

    if final_lines:
        parsed_script = f"{'/'.join([line.rstrip() for line in final_lines])}".replace(
            "//", "/home/"
        )
        if parsed_script[0] == "/":
            if parsed_script.startswith("//home"):  # pragma: no cover
                parsed_script = parsed_script[6:]
        else:
            parsed_script = "/" + parsed_script

        if parsed_script.endswith("/home/"):
            parsed_script = parsed_script[:-1]

    return "", parsed_script
