class CompanyDocument:
    """Holder class for company document information"""

    category = ""
    date = ""
    description = ""
    paper_filed = ""
    pages = ""
    transaction_id = ""
    content = b""

    def __init__(
        self,
        category="",
        date: str = "",
        description: str = "",
        paper_filed: str = "",
        pages: str = "",
        transaction_id: str = "",
        content=b"",
    ):
        self.category = category
        self.date = date
        self.description = description
        self.paper_filed = paper_filed
        self.pages = pages
        self.transaction_id = transaction_id
        self.content = content

    def dataAvailable(self) -> bool:
        return len(self.content) > 0
