"""Pydantic models for Quantitative Analysis."""
from pydantic import BaseModel


class TestModel(BaseModel):
    """Base model for QA tests."""

    statistic: float
    p_value: float


class NormalityModel(BaseModel):
    """Normality model."""

    kurtosis: TestModel
    skewness: TestModel
    jarque_bera: TestModel
    shapiro_wilk: TestModel
    kolmogorov_smirnov: TestModel


class ADFTestModel(TestModel):
    """Augmented Dickey-Fuller test model."""

    nlags: int
    nobs: int
    icbest: float


class KPSSTestModel(TestModel):
    """Kwiatkowski–Phillips–Schmidt–Shin test model."""

    nlags: int


class UnitRootModel(BaseModel):
    """Unit root model."""

    adf: ADFTestModel
    kpss: KPSSTestModel


class OmegaModel(BaseModel):
    """Omega model."""

    threshold: float
    omega: float


class SummaryModel(BaseModel):
    """Summary model."""

    count: int
    mean: float
    std: float
    var: float
    min: float
    max: float
    p_25: float
    p_50: float
    p_75: float


class CAPMModel(BaseModel):
    """CAPM model."""

    market_risk: float
    systematic_risk: float
    idiosyncratic_risk: float
