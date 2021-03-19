import os


def convert_to_bool(ins: str) -> bool:
    return True if ins == "True" else False


USE_COLOR = (
    True
    if os.getenv("GTFF_USE_COLOR") is None
    else convert_to_bool(os.getenv("GTFF_USE_COLOR"))
)
USE_FLAIR = (
    "stars" if os.getenv("GTFF_USE_FLAIR") is None else os.getenv("GTFF_USE_FLAIR")
)
USE_ION = (
    True
    if os.getenv("GTFF_USE_ION") is None
    else convert_to_bool(os.getenv("GTFF_USE_ION"))
)
USE_PROMPT_TOOLKIT = (
    False
    if os.getenv("GTFF_USE_PROMPT_TOOLKIT") is None
    else convert_to_bool(os.getenv("GTFF_USE_PROMPT_TOOLKIT"))
)

# Enable Prediction features
ENABLE_PREDICT = (
    False
    if os.getenv("GTFF_ENABLE_PREDICT") is None
    else convert_to_bool(os.getenv("GTFF_ENABLE_PREDICT"))
)

# Enable plot autoscaling
USE_PLOT_AUTOSCALING = (
    False
    if os.getenv("GTFF_USE_PLOT_AUTOSCALING") is None
    else convert_to_bool(os.getenv("GTFF_USE_PLOT_AUTOSCALING"))
)
