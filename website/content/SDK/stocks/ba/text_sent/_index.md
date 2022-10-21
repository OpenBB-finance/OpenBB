## Get underlying data 
### stocks.ba.text_sent(post_data: List[str]) -> float

Find the sentiment of a post and related comments

    Parameters
    ----------
    post_data: list[str]
        A post and its comments in string form

    Returns
    -------
    float
        A number in the range [-1, 1] representing sentiment
