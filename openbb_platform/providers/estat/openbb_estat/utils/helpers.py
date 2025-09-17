"""e-Stat API Helper Functions."""

from typing import Dict, Any, Optional


def handle_estat_error(status_code: int, error_msg: str) -> str:
    """Handle e-Stat API error codes.

    Error codes from e-Stat API:
    - 0: Success
    - 100-199: Client errors
    - 200-299: Parameter errors
    - 300-399: Data not found errors
    - 400+: Server errors
    """
    error_messages = {
        100: "Invalid Application ID",
        101: "Application ID not registered",
        102: "Rate limit exceeded",
        200: "Invalid parameter format",
        201: "Missing required parameter",
        300: "Statistical data not found",
        301: "No data available for specified conditions",
        400: "Server error",
        500: "Maintenance in progress",
    }

    if status_code in error_messages:
        return f"{error_messages[status_code]}: {error_msg}"
    elif 100 <= status_code < 200:
        return f"Authentication error ({status_code}): {error_msg}"
    elif 200 <= status_code < 300:
        return f"Parameter error ({status_code}): {error_msg}"
    elif 300 <= status_code < 400:
        return f"Data not found ({status_code}): {error_msg}"
    else:
        return f"API error ({status_code}): {error_msg}"


def validate_stats_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean e-Stat API parameters.

    Args:
        params: Raw parameters dictionary

    Returns:
        Cleaned parameters dictionary
    """
    # Remove None values
    cleaned = {k: v for k, v in params.items() if v is not None}

    # Validate search_kind
    if "searchKind" in cleaned and cleaned["searchKind"] not in ["1", "2"]:
        cleaned["searchKind"] = "1"

    # Validate flags
    for flag_key in ["metaGetFlg", "cntGetFlg", "explanationGetFlg", "annotationGetFlg"]:
        if flag_key in cleaned and cleaned[flag_key] not in ["Y", "N"]:
            cleaned[flag_key] = "Y"

    return cleaned


def format_estat_date(date_str: str) -> Optional[str]:
    """Format date string from e-Stat format.

    e-Stat uses formats like:
    - YYYY: Annual data (e.g., "2020")
    - YYYYMM: Monthly data (e.g., "202012")
    - YYYYQ#: Quarterly data (e.g., "2020Q1")
    - YYYY######: Special format (e.g., "2020000000")

    Returns ISO format date string or None if invalid.
    """
    if not date_str:
        return None

    try:
        # Special format with trailing zeros (e.g., "2020000000")
        if len(date_str) == 10 and date_str.endswith("000000"):
            return f"{date_str[:4]}-01-01"

        # Remove trailing zeros for other special formats
        if len(date_str) > 6:
            # Check if positions 4-6 are valid month digits
            if date_str[4:6].isdigit() and 1 <= int(date_str[4:6]) <= 12:
                date_str = date_str[:6]
            else:
                date_str = date_str[:4]

        if len(date_str) == 4:  # Year only
            if date_str.isdigit():
                return f"{date_str}-01-01"
            else:
                return None
        elif len(date_str) == 6:  # Year and month
            month = date_str[4:6]
            if 1 <= int(month) <= 12:
                return f"{date_str[:4]}-{month}-01"
            else:
                return f"{date_str[:4]}-01-01"
        elif "Q" in date_str:  # Quarterly
            year = date_str[:4]
            quarter = int(date_str[-1])
            month = (quarter - 1) * 3 + 1
            return f"{year}-{month:02d}-01"
        else:
            return None
    except (ValueError, IndexError):
        return None