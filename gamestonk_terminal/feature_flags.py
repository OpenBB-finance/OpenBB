import os

USE_COLOR = os.getenv("GTFF_USE_COLOR") or True
USE_FLAIR = os.getenv("GTFF_USE_FLAIR") or "stars"
USE_ION = os.getenv("GTFF_USE_ION") or True
USE_PROMPT_TOOLKIT = os.getenv("GTFF_USE_PROMPT_TOOLKIT") or False

# Enable Prediction features
ENABLE_PREDICT = os.getenv("GTFF_ENABLE_PREDICT") or False