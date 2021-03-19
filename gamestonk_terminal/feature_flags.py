from distutils.util import strtobool
import os

USE_COLOR = strtobool(os.getenv("GTFF_USE_COLOR", "True"))
USE_FLAIR = os.getenv("GTFF_USE_FLAIR") or "stars"
USE_ION = strtobool(os.getenv("GTFF_USE_ION", "True"))
USE_PROMPT_TOOLKIT = strtobool(os.getenv("GTFF_USE_PROMPT_TOOLKIT", "False"))

# Enable Prediction features
ENABLE_PREDICT = strtobool(os.getenv("GTFF_ENABLE_PREDICT", "False"))

# Enable plot autoscaling
USE_PLOT_AUTOSCALING = strtobool(os.getenv("GTFF_USE_PLOT_AUTOSCALING", "False"))
