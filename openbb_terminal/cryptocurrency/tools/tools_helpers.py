def change_variation(change: float) -> float:
    """Helper to convert change variation

    Parameters
    ----------
    change: float
        percentage change

    Returns
    -------
    float:
        converted value
    """
    return (100 + change) / 100


def calculate_hold_value(changeA: float, changeB: float, proportion: float) -> float:
    """Calculates hold value of two different coins

    Parameters
    ----------
    changeA: float
        price change of crypto A in percentage
    changeB: float
        price change of crypto B in percentage
    proportion: float
        percentage of first token in pool

    Returns
    -------
    float:
        hold value
    """
    return (change_variation(changeA) * proportion) / 100 + (
        (change_variation(changeB) * (100 - proportion)) / 100
    )


def calculate_pool_value(changeA, changeB, proportion):
    """Calculates pool value of two different coins

    Parameters
    ----------
    changeA: float
        price change of crypto A in percentage
    changeB: float
        price change of crypto B in percentage
    proportion: float
        percentage of first token in pool

    Returns
    -------
    float:
        pool value
    """
    return pow(change_variation(changeA), proportion / 100) * pow(
        change_variation(changeB), (100 - proportion) / 100
    )
