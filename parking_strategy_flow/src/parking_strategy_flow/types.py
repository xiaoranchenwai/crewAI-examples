from typing import List, Dict, Any
from pydantic import BaseModel


class ResearchData(BaseModel):
    market_analysis: str
    user_behavior: str 
    pricing_models: str
    case_studies: str


class PricingStrategy(BaseModel):
    pricing_strategy: str
    justification: str
    risk_control: str
    implementation: str
    case_references: str