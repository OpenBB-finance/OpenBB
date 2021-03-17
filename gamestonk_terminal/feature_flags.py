import os

USE_COLOR = os.getenv("GTFF_USE_COLOR").lower() not in ["false", "0"] or True
USE_FLAIR = os.getenv("GTFF_USE_FLAIR") or "stars"
USE_ION = os.getenv("GTFF_USE_ION").lower() not in ["false", "0"] or True
USE_PROMPT_TOOLKIT = (
    os.getenv("GTFF_USE_PROMPT_TOOLKIT").lower() not in ["false", "0"] or False
)

# Enable Prediction features
ENABLE_PREDICT = os.getenv("GTFF_ENABLE_PREDICT").lower() not in ["false", "0"] or False

# Enable plot autoscaling
USE_PLOT_AUTOSCALING = (
    os.getenv("GTFF_USE_PLOT_AUTOSCALING").lower() not in ["false", "0"] or False
)
