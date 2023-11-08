import re
from datetime import datetime, timedelta
from typing import Dict, List, Match, Optional, Tuple, Union

from dateutil.relativedelta import relativedelta

from openbb_terminal.rich_config import console

# pylint: disable=too-many-statements,eval-used,consider-iterating-dictionary
# pylint: disable=too-many-branches,too-many-return-statements

# Necessary for OpenBB keywords
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
    """Test whether a command is a reset command

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
    if command == "r":
        return True
    if command == "r\n":
        return True
    return False


def match_and_return_openbb_keyword_date(keyword: str) -> str:  # noqa: PLR0911
    """Return OpenBB keyword into date

    Parameters
    ----------
    keyword : str
        String with potential OpenBB keyword (e.g. 1MONTHAGO,LASTFRIDAY,3YEARSFROMNOW,NEXTTUESDAY)

    Returns
    ----------
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
                    return (now - relativedelta(**kwargs)).strftime("%Y-%m-%d")  # type: ignore
                return (now + relativedelta(**kwargs)).strftime("%Y-%m-%d")  # type: ignore

    match = re.search(r"\$LAST(\w+)", keyword)
    if match:
        time_unit = match.group(1)
        # Check if it corresponds to a month
        if time_unit in list(MONTHS_VALUE.keys()):
            the_year = now.year
            # Calculate the year and month for last month date
            if now.month <= MONTHS_VALUE[time_unit]:
                # If the current month is greater than the last date month, it means it is this year
                the_year = now.year - 1
            return datetime(the_year, MONTHS_VALUE[time_unit], 1).strftime("%Y-%m-%d")

        # Check if it corresponds to a week day
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
        # Check if it corresponds to a month
        if time_unit in list(MONTHS_VALUE.keys()):
            # Calculate the year and month for next month date
            if now.month < MONTHS_VALUE[time_unit]:
                # If the current month is greater than the last date month, it means it is this year
                return datetime(now.year, MONTHS_VALUE[time_unit], 1).strftime(
                    "%Y-%m-%d"
                )

            return datetime(now.year + 1, MONTHS_VALUE[time_unit], 1).strftime(
                "%Y-%m-%d"
            )

        # Check if it corresponds to a week day
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
    raw_lines: List[str],
    script_inputs: Optional[List[str]] = None,
) -> Tuple[str, str]:
    """
    Parse .openbb script

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
        Processed string from .openbb script that can be run by the OpenBB Terminal
    """
    ROUTINE_VARS: Dict[str, Union[str, List[str]]] = dict()
    if script_inputs:
        ROUTINE_VARS["$ARGV"] = script_inputs

    ## PRE PROCESSING
    # Remove reset commands, comments, empty lines and trailing/leading whitespaces
    raw_lines = [
        x.strip()
        for x in raw_lines
        if (not is_reset(x)) and ("#" not in x) and x.strip()
    ]

    ## LOOK FOR NEW VARIABLES BEING DECLARED FROM USERS
    lines_without_declarations = list()
    for line in raw_lines:
        # Check if this line has a variable attribution
        # This currently allows user to override ARGV parameter
        if "$" in line and "=" in line:
            match = re.search(r"\$(\w+)\s*=\s*([\w\d,-.\s]+)", line)
            if match:
                VAR_NAME = match.group(1)
                VAR_VALUES = match.group(2)
                ROUTINE_VARS["$" + VAR_NAME] = (
                    VAR_VALUES if "," not in VAR_VALUES else VAR_VALUES.split(",")
                )

                # Just throw a warning when user uses wrong convention
                numdollars = len(re.findall(r"\$", line))
                if numdollars > 1:
                    console.print(
                        f"The variable {VAR_NAME} should not be declared as "
                        f"{'$' * numdollars}{VAR_NAME}. Instead it will be "
                        f"converted into ${VAR_NAME}."
                    )

            else:
                lines_without_declarations.append(line)
        else:
            lines_without_declarations.append(line)

    # At this stage our ROUTINE_VARS should be completed coming from external AND from internal
    # Now we want to replace the ROUTINE_VARS to where applicable throughout the .openbb script
    # Due to this implementation, a variable declared at the end will still be effective

    lines_with_vars_replaced = list()
    foreach_loop_found = False
    for line in lines_without_declarations:
        # Save temporary line to ensure that all vars get replaced by correct vars
        templine = line

        # Found 'end' keyword which means that a loop has terminated
        if re.match(r"^\s*end\s*$", line, re.IGNORECASE):
            # Check whether the foreach loop has started or not
            if not foreach_loop_found:
                return (
                    "[red]The script has a foreach loop that terminates before it gets started. "
                    "Add the keyword 'foreach' to explicitly start loop[/red]",
                    "",
                )
            foreach_loop_found = False

        else:
            # Found 'foreach' keyword which means there needs to be a matching 'end'
            if re.search(r"foreach", line, re.IGNORECASE):
                foreach_loop_found = True

            # Regular expression pattern to match variables starting with $
            pattern = r"(?<!\$)(\$(\w+)(\[[^\]]*\])?)(?=(?:[^\]]*\]*))"

            # Find all matches of the pattern in the line
            matches: Optional[List[Match[str]]] = re.findall(pattern, line)

            if matches:
                for match in matches:
                    if match:
                        VAR_NAME = "$" + match[1]
                        VAR_SLICE = match[2][1:-1] if match[2] else ""

                        # Within a list refers to a single element
                        if VAR_SLICE.isdigit():
                            # This is an edge case for when the user has a variable such as $DATE = 2022-01-01
                            # We want the user to be able to access it with $DATE or $DATE[0] and the latest
                            # in python will only take the first '2'
                            if VAR_SLICE == "0":
                                if VAR_NAME in ROUTINE_VARS:
                                    values = eval(  # noqa: S307
                                        f'ROUTINE_VARS["{VAR_NAME}"]'
                                    )
                                    if isinstance(values, list):
                                        templine = templine.replace(
                                            match[0],
                                            eval(f"values[{VAR_SLICE}]"),  # noqa: S307
                                        )
                                    else:
                                        templine = templine.replace(match[0], values)
                                else:
                                    return (
                                        f"[red]Variable {VAR_NAME} not given "
                                        "for current routine script.[/red]",
                                        "",
                                    )

                            # Only enters here when any other index from 0 is used
                            elif VAR_NAME in ROUTINE_VARS:
                                variable = eval(  # noqa: S307
                                    f'ROUTINE_VARS["{VAR_NAME}"]'
                                )
                                length_variable = (
                                    len(variable) if isinstance(variable, list) else 1
                                )

                                # We use <= because we are using 0 index based lists
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

                        # Involves slicing which is a bit more tricky to use eval on
                        elif (
                            ":" in VAR_SLICE
                            and len(VAR_SLICE.split(":")) == 2
                            and (
                                VAR_SLICE.split(":")[0].isdigit()
                                or VAR_SLICE.split(":")[1].isdigit()
                            )
                        ):
                            slicing_tuple = "slice("
                            slicing_tuple += (
                                VAR_SLICE.split(":")[0]
                                if VAR_SLICE.split(":")[0].isdigit()
                                else "None"
                            )
                            slicing_tuple += ","
                            slicing_tuple += (
                                VAR_SLICE.split(":")[1]
                                if VAR_SLICE.split(":")[1].isdigit()
                                else "None"
                            )
                            slicing_tuple += ")"

                            vars_to_loop = eval(  # noqa: S307
                                f'ROUTINE_VARS["{VAR_NAME}"][{slicing_tuple}]'
                            )

                            # Check whether the slicing was successful or not
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

                        # Just replace value without slicing or list
                        else:
                            if VAR_SLICE:
                                # Check if the string starts with a minus sign
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
                                value = eval(  # noqa: S307
                                    f'ROUTINE_VARS["{VAR_NAME}"]'
                                )

                                # If the value is a list, we want to replace it with the whole list
                                if isinstance(value, list):
                                    templine = templine.replace(
                                        match[0],
                                        ",".join(value),
                                    )
                                else:
                                    templine = templine.replace(match[0], value)

                            else:
                                # Check if this is an OpenBB keyword variable like
                                # 1MONTHAGO,LASTFRIDAY,3YEARSFROMNOW,NEXTTUESDAY
                                # and decode it into the right date if it exists
                                potential_date_match = (
                                    match_and_return_openbb_keyword_date(VAR_NAME)
                                )
                                if potential_date_match:
                                    templine = templine.replace(
                                        match[0], potential_date_match
                                    )
                                else:
                                    return (
                                        f"[red]Variable {VAR_NAME} not given for "
                                        "current routine script.[/red]",
                                        "",
                                    )

        lines_with_vars_replaced.append(templine)

    # If this flags ends in True it means that the script routine has a foreach loop that never terminates
    if foreach_loop_found:
        return (
            "[red]The script has a foreach loop that doesn't terminate. "
            "Add the keyword 'end' to explicitly terminate loop[/red]",
            "",
        )

    # Finally the only remaining thing to address are the foreach loops. For that we'll go through
    # those lines and unroll the arguments that will be iterated by.
    # Note that the fact that we checked before that the amount of foreach and end matches allow us
    # to be confident that the script has no clear issues.

    within_foreach = False
    foreach_lines_loop: List[str] = list()

    parsed_script = ""
    final_lines = list()
    varname = "VAR"
    varused_inside = False
    for line in lines_with_vars_replaced:
        # Found 'foreach' header associated with loop
        match = re.search(
            r"foreach \$\$([A-Za-z\_]+) in ([A-Za-z0-9,-.]+)", line, re.IGNORECASE
        )
        if match:
            varname = match.group(1)
            foreach_loop = match.group(2).split(",")
            within_foreach = True

        # We are inside a loop and this is a line that we will want to replicate,
        # so we need to temporarily store it until we reach the end
        elif within_foreach:
            # Found 'end' keyword which means that the foreach loop has reached the end
            if re.match(r"^\s*end\s*$", line, re.IGNORECASE):
                # Now we want to process what we were waiting for before

                # Iterate through main foreach header
                for var in foreach_loop:
                    # Iterate through all lines within foreach and end loop
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
                    console.print(
                        f"The variable {varname} was used in foreach header "
                        "but it wasn't used inside the loop."
                    )
                    varused_inside = False

                # Since this has been processed we reset the foreach loop lines
                within_foreach = False
                foreach_lines_loop = list()

            else:
                foreach_lines_loop.append(line)

        else:
            final_lines.append(line)

    # If the list is non null, then we want to convert this into a parsed string that is
    # recognized by the OpenBB Terminal
    if final_lines:
        parsed_script = f"{'/'.join([line.rstrip() for line in final_lines])}".replace(
            "//", "/home/"
        )
        if parsed_script[0] == "/":
            # If the user had added a / at the beginning, then it was converted to //home/
            # and we need to remove it
            if parsed_script.startswith("//home"):
                parsed_script = parsed_script[6:]
        else:
            # We want the script to start from the home menu, hence we add it if the user
            # didn't add it
            parsed_script = "/" + parsed_script

        # If the script finishes with // it means that we converted it to /home/
        # This means that we are expecting a command to follow, but since this is
        # the end of the script, we need to remove the trailing /
        if parsed_script.endswith("/home/"):
            parsed_script = parsed_script[:-1]

    return "", parsed_script
