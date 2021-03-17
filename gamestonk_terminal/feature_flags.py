import os

# env vars are strings not booleans
# check for "false" or "0"
# any other value is true (including empty string)

USE_COLOR = os.getenv("GTFF_USE_COLOR", "true").lower() not in ["false", "0"]
USE_FLAIR = os.getenv("GTFF_USE_FLAIR", "stars")
USE_ION = os.getenv("GTFF_USE_ION", "true").lower() not in ["false", "0"]
USE_PROMPT_TOOLKIT = os.getenv("GTFF_USE_PROMPT_TOOLKIT", "false").lower() not in [
    "false",
    "0",
]


# Enable Prediction features
ENABLE_PREDICT = os.getenv("GTFF_ENABLE_PREDICT", "false").lower() not in ["false", "0"]

# Enable plot autoscaling
USE_PLOT_AUTOSCALING = os.getenv("GTFF_USE_PLOT_AUTOSCALING", "false").lower() not in [
    "false",
    "0",
]
