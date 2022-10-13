## Get underlying data 
### stocks.options.process_chains(response: requests.models.Response) -> pandas.core.frame.DataFrame

Function to take in the requests.get and return a DataFrame

    Parameters
    ----------
    response: requests.models.Response
        This is the response from tradier api.

    Returns
    -------
    opt_chain: pd.DataFrame
        Dataframe with all available options
