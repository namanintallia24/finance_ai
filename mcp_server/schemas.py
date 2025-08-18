from typing import List, Dict , Optional ,Union, Any
from pydantic import BaseModel

# For yearly purpose..
# Schema for compare_net_income tool
class CompareNetIncomeInput(BaseModel):
    company_names: List[str]
    year: str
    fields: Optional[List[str]] = None 

class Company_Info_Input(BaseModel):
    company_names: List[str]
    year: str
    fields: Optional[List[str]] = None 

class CashFlowInput(BaseModel):
    company_names: List[str]
    year: str
    fields: Optional[List[str]] = None 

class CashFlowOutput(BaseModel):
    comparison: Dict[str, Dict[str, Dict[str, Any]]]
    year: str


class CompareNetIncomeOutput(BaseModel):
    comparison: Dict[str, Dict[str, Dict[str, Any]]]
    year: str

class Company_Info_Output(BaseModel):
    comparison: Dict[str, Dict[str, Dict[str, Any]]]
    year: str


class SummarizeBalanceSheetInput(BaseModel):
    company_names: List[str]
    year: str
    fields: Optional[List[str]] = None 

class SummarizeBalanceSheetOutput(BaseModel):
    comparison: Dict[str, Dict[str, Dict[str, Any]]]
    year: str

class Financial_Ratio_Input(BaseModel):
    company_names: List[str]
    year: str
    fields: Optional[List[str]] = None 

class Financial_Ratio_Output(BaseModel):
    comparison: Dict[str, Dict[str, Dict[str, Any]]]
    year: str

class QuarterlyIncomeInput(BaseModel):
    company_names: List[str]
    year: str
    quarter_month: List[str]
    fields: Optional[List[str]] = None 


class QuarterlyIncomeOutput(BaseModel):
    comparison: Dict[str, Dict[str, Dict[str, Any]]]
    year: str


class QuarterlyShareholdingInput(BaseModel):
    company_names: List[str]
    year: str
    quarter_month: List[str]
    fields: Optional[List[str]] = None 


class QuarterlyShareholdingOutput(BaseModel):
    comparison: Dict[str, Dict[str, Dict[str, Any]]]
    year: str

class YearlyShareholdingInput(BaseModel):
    company_names: List[str]
    year: str
    fields: Optional[List[str]] = None 

class YearlyShareholdingOutput(BaseModel):
    comparison: Dict[str, Dict[str, Dict[str, Any]]]
    year: str


class SectorWiseCompanyInput(BaseModel):
    sector: List[str]



class CompanyMetrics(BaseModel):
    company_name: str
    nse: Optional[str] = None
    bse: Optional[str] = None
    market_cap: Optional[float] = None
    current_price: Optional[float] = None
    stock_pe: Optional[float] = None
    roe: Optional[float] = None
    roce: Optional[float] = None


class SectorWiseCompanyOutput(BaseModel):
    comparison: Dict[str, List[CompanyMetrics]]