"""Template Provider Helpers"""

from typing import Any, Dict, List, Optional, Union

from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request


async def get_congress_data(
    url: str,
    api_key: Optional[str] = None,
    **kwargs: Any
) -> Union[Dict, List[Dict]]:
    """Get data from Congress.gov API endpoint.
    
    Parameters
    ----------
    url : str
        The API endpoint URL
    api_key : str, optional
        Congress API key
    **kwargs
        Additional arguments for the request
        
    Returns
    -------
    Union[Dict, List[Dict]]
        The response data
        
    Raises
    ------
    EmptyDataError
        If no data is returned
    """
    params = kwargs.get('params', {})
    if api_key:
        params['api_key'] = api_key
        kwargs['params'] = params
    
    response = await amake_request(url, **kwargs)
    
    if not response:
        raise EmptyDataError("No data returned from Congress API")
        
    return response


def build_congress_url(
    base_path: str,
    congress: Optional[int] = None,
    bill_type: Optional[str] = None,
    bill_number: Optional[str] = None,
    endpoint: Optional[str] = None
) -> str:
    """Build a Congress.gov API URL.
    
    Parameters
    ----------
    base_path : str
        Base API path (e.g., 'bill', 'summaries')
    congress : int, optional
        Congress session number
    bill_type : str, optional
        Type of bill (hr, s, etc.)
    bill_number : str, optional
        Bill number
    endpoint : str, optional
        Additional endpoint (e.g., 'summaries', 'text')
        
    Returns
    -------
    str
        Complete API URL
    """
    base_url = "https://api.congress.gov/v3"
    url_parts = [base_url, base_path]
    
    if congress:
        url_parts.append(str(congress))
    if bill_type:
        url_parts.append(bill_type)
    if bill_number:
        url_parts.append(bill_number)
    if endpoint:
        url_parts.append(endpoint)
        
    return "/".join(url_parts)
