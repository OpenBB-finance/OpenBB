from typing import List


class Metadata:
    @property
    def dir_list(self) -> List[str]:
        return self.__dir_list

    @property
    def doc_string(self) -> str:
        return self.__doc_string

    def __init__(
        self,
        dir_list: List[str],
        doc_string: str = "",
    ) -> None:
        self.__dir_list = dir_list
        self.__doc_string = doc_string
