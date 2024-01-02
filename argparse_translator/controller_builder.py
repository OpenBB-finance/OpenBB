from openbb import obb
from .argparse_class_processor import ArgparseClassProcessor

equity_price_translations = ArgparseClassProcessor(target_class=obb.equity.price)
print("nice")
