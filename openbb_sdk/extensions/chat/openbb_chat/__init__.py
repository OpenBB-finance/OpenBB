from openbb_core.app.model.obbject import OBBject
from pandasai import SmartDataframe
from pandasai.llm import OpenAI


def chat(self: OBBject, query, **kwargs) -> str:
    """Chat with a dataframable OBBject

    Parameters
    ----------
    self
    query
    llm

    Returns
    -------

    """

    # TODO: add other model compatibilities.

    try:
        df = self.to_df()
    except Exception as e:
        print(str(e))
        return self

    return SmartDataframe(
        df,
        config={"llm": OpenAI("I NEED HELP FIGURING OUT HOW TO DEAL WITH API KEY")},
    ).chat(query)


OBBject.chat = chat
