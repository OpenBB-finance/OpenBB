from pydantic import BaseModel


class TestModel(BaseModel):
    statistic: float
    p_value: float


class NormalityModel(BaseModel):
    kurtosis: TestModel
    skewness: TestModel
    jarque_bera: TestModel
    shapiro_wilk: TestModel
    kolmogorov_smirnov: TestModel


class ADFTestModel(TestModel):
    nlags: int
    nobs: int
    icbest: float


class KPSSTestModel(TestModel):
    nlags: int


class UnitRootModel(BaseModel):
    adf: ADFTestModel
    kpss: KPSSTestModel


class OmegaModel(BaseModel):
    threshold: float
    omega: float


class SummaryModel(BaseModel):
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
    market_risk: float
    systematic_risk: float
    idiosyncratic_risk: float
