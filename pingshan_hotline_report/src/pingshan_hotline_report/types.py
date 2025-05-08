from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime


class ChartData(BaseModel):
    """Representation of chart data for visualization"""
    title: str
    chart_type: str  # bar, line, pie, etc.
    data: Dict[str, Any]
    chart_url: Optional[str] = None


class ReportSection(BaseModel):
    """A section of the monthly report"""
    title: str
    content: str
    charts: Optional[List[ChartData]] = None


class MonthlyReport(BaseModel):
    """Complete monthly report structure"""
    title: str
    month: str
    year: str
    summary: str
    sections: List[ReportSection]
    creation_date: datetime = datetime.now()