from typing import List, Dict
from pydantic import BaseModel

class QueryResult(BaseModel):
    """Base model for SQL query results"""
    query: str
    data: Dict

class DistrictEventStats(BaseModel):
    """Statistics of events by district"""
    district_data: Dict[str, int]
    
class ElectricVehicleViolations(BaseModel):
    """Electric vehicle violations by community"""
    communities: List[str]
    
class GarbageExposureStats(BaseModel):
    """Garbage exposure statistics by community"""
    community_data: Dict[str, int]
    
class GarbageSourceStats(BaseModel):
    """Statistics on sources of garbage exposure events"""
    source_data: Dict[str, int]

class ChartData(BaseModel):
    """Chart data for visualization"""
    chart_type: str
    title: str
    chart_url: str
    description: str

class ReportSection(BaseModel):
    """A section of the final report"""
    title: str
    content: str
    chart_data: ChartData = None

class PingshanReport(BaseModel):
    """Complete Pingshan Hotline Report"""
    sections: List[ReportSection]