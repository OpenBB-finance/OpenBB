import pandas as pd


class Filing_data:
    """Holder class for company filings information"""

    filings = pd.DataFrame()
    total_count = 0
    start_index = 0
    end_index = 0

    def __init__(self, filings, start_index, end_index, total_count):
        self.filings = filings
        self.start_index = start_index
        self.end_index = end_index
        self.total_count = total_count

    def dataAvailable(self) -> bool:
        return len(self.filings) > 0
