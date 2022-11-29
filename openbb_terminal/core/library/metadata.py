from typing import List


class Metadata:
    @property
    def dir_list(self) -> List[str]:
        return self.__dir_list

    @property
    def docstring(self) -> str:
        return self.__docstring

    def __init__(
        self,
        dir_list: List[str],
        docstring: str = "",
    ) -> None:
        self.__dir_list = dir_list
        self.__docstring = docstring
