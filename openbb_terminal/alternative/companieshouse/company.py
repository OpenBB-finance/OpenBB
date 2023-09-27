class Company:
    """Holder class for company information"""

    name = ""
    address = ""
    lastAccounts = ""

    def __init__(self, name="", address: str = "", lastAccounts: str = ""):
        self.name = name
        self.address = address
        self.lastAccounts = lastAccounts

    def dataAvailable(self) -> bool:
        return len(self.name) > 0
