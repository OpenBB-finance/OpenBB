"""Finviz Definitions."""

from typing import Literal

GROUPS = Literal[
    "sector",
    "industry",
    "country",
    "capitalization",
    "energy",
    "materials",
    "industrials",
    "consumer_cyclical",
    "consumer_defensive",
    "healthcare",
    "financial",
    "technology",
    "communication_services",
    "utilities",
    "real_estate",
]

GROUPS_DICT = {
    "sector": "Sector",
    "industry": "Industry",
    "country": "Country (U.S. listed stocks only)",
    "capitalization": "Capitalization",
    "energy": "Industry (Energy)",
    "materials": "Industry (Basic Materials)",
    "industrials": "Industry (Industrials)",
    "consumer_cyclical": "Industry (Consumer Cyclical)",
    "consumer_defensive": "Industry (Consumer Defensive)",
    "healthcare": "Industry (Healthcare)",
    "financial": "Industry (Financial)",
    "technology": "Industry (Technology)",
    "communication_services": "Industry (Communication Services)",
    "utilities": "Industry (Utilities)",
    "real_estate": "Industry (Real Estate)",
}

METRICS = Literal[
    "performance",
    "valuation",
    "overview",
]
