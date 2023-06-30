from enum import Enum

from pydantic import BaseModel


class ExportFormat(str, Enum):
    csv = "csv"
    feather = "feather"
    hdf = "hdf"
    html = "html"
    jpeg = "jpeg"
    json = "json"
    parquet = "parquet"
    pdf = "pdf"
    plotly = "plotly"
    png = "png"
    svg = "svg"
    txt = "txt"
    xlsx = "xlsx"
    xls = "xls"
    xml = "xml"


class Export(BaseModel):
    content: str
    export_format: ExportFormat

    class Config:
        validate_assignment = True
