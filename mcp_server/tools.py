import pandas as pd
from data1.db import SessionLocal
from collections import defaultdict
from decimal import Decimal
from sqlalchemy import text
from mcp_server.schemas import (
    CompareNetIncomeInput,
    CashFlowInput,
    CompareNetIncomeOutput,
    CashFlowOutput,
    SummarizeBalanceSheetInput,
    SummarizeBalanceSheetOutput,
    QuarterlyIncomeInput,
    QuarterlyIncomeOutput,
    Company_Info_Input,
    Company_Info_Output,
    Financial_Ratio_Input,
    Financial_Ratio_Output,
    YearlyShareholdingInput,
    YearlyShareholdingOutput,
    QuarterlyShareholdingInput,
    QuarterlyShareholdingOutput,
    SectorWiseCompanyInput,
    SectorWiseCompanyOutput,
)
from datetime import datetime
from typing import Union, List, Dict, Any , Optional


#For calculate net margin
def calculate_net_margin(net_profit: float, sales: float) -> Optional[float]:
    return f"{round((net_profit / sales) * 100, 2)}%" if sales else None


def list_tools():
    return {
        "tools": [
            {
                "name": "company_info_",
                "description": "Get company financial info by name and year",
                "parameters": Company_Info_Input.schema()["properties"]
            },
            {
                "name": "compare_net_income",
                "description": "Compare net income between companies over time",
                "parameters": CompareNetIncomeInput.schema()["properties"]
            },
            {
                "name": "cash_flow",
                "description": "Get cash flow for a given company and year",
                "parameters": CashFlowInput.schema()["properties"]
            },
            {
                "name": "summarize_balance_sheet",
                "description": "Summarize balance sheet for a specific company and year",
                "parameters": SummarizeBalanceSheetInput.schema()["properties"]
            },
            {
                "name": "yearly_shareholding",
                "description": "Get yearly shareholding data for a company",
                "parameters": YearlyShareholdingInput.schema()["properties"]
            },
            {
                "name": "financial_ratio",
                "description": "Get financial ratios for a company and year",
                "parameters": Financial_Ratio_Input.schema()["properties"]
            },
            {
                "name": "compare_quarterly_income",
                "description": "Compare quarterly income of a company for a given year",
                "parameters": QuarterlyIncomeInput.schema()["properties"]
            },
            {
                "name": "quarterly_shareholding",
                "description": "Get quarterly shareholding of a company for a specific year",
                "parameters": QuarterlyShareholdingInput.schema()["properties"]
            },
            {
                "name": "sector_wise_company",
                "description": "Get top companies in a given sector by market cap",
                "parameters": SectorWiseCompanyInput.schema()["properties"]
            }
        ]
    }


def call_tool(tool_name, parameters):
    
    if tool_name == "company_info_":
        validated = Company_Info_Input(**parameters)
        return company_info(validated).dict()

    elif tool_name == "compare_net_income":
        validated = CompareNetIncomeInput(**parameters)
        return compare_net_income(validated).dict()

    elif tool_name == "cash_flow":
        validated = CashFlowInput(**parameters)
        return cash_flow(validated).dict()

    elif tool_name == "summarize_balance_sheet":
        validated = SummarizeBalanceSheetInput(**parameters)
        return summarize_balance_sheet(validated).dict()

    elif tool_name == "yearly_shareholding":
        validated = YearlyShareholdingInput(**parameters)
        return yearly_shareholding(validated).dict()

    elif tool_name == "financial_ratio":
        validated = Financial_Ratio_Input(**parameters)
        return financial_ratio(validated).dict()

    elif tool_name == "compare_quarterly_income":
        validated = QuarterlyIncomeInput(**parameters)
        return compare_quarterly_income(validated).dict()

    elif tool_name == "quarterly_shareholding":
        validated = QuarterlyShareholdingInput(**parameters)
        return quarterly_shareholding(validated).dict()

    elif tool_name == "sector_wise_company":
        validated = SectorWiseCompanyInput(**parameters)
        return sector_wise_company(validated).dict()
    
     # ✅ Add your custom tools here
    elif tool_name == "three_statements_":
        return three_statements_tool(tool_name, parameters)

    elif tool_name == "cash_flow_to_debt_":
        return cash_flow_to_debt(tool_name, parameters)

    elif tool_name == "debt_to_financing_ratio_":
        return debt_to_financing_ratio(tool_name, parameters)

    elif tool_name == "operating_cf_to_interest_":
        return operating_cf_to_interest(tool_name, parameters)

    elif tool_name == "_net_c_f_margin":
        return net_cash_flow_margin(tool_name, parameters)

    elif tool_name == "_fixed_asset_turnover_ratio":
        return fixed_asset_turnover(tool_name, parameters)

    elif tool_name == "_operating_cf_to_liablities":
        return operating_cash_flow_to_interest(tool_name, parameters)

    else:
        return "Unknown tool"

#For three statements tool
def three_statements_tool(tool_name, parameters):

    total_statements_data = []
    if tool_name == "three_statements_":
        validated = CompareNetIncomeInput(**parameters)
        f1_data = compare_net_income(validated).dict()
        total_statements_data.append(f1_data)

    if tool_name == "three_statements_":
        validated = CashFlowInput(**parameters)
        f2_data = cash_flow(validated).dict()
        total_statements_data.append(f2_data)

    if tool_name == "three_statements_":
        validated = SummarizeBalanceSheetInput(**parameters)
        f3_data = summarize_balance_sheet(validated).dict()
        total_statements_data.append(f3_data)
        return total_statements_data
    


#For financial ratio
def financial_ratio(input_data: Financial_Ratio_Input) -> Financial_Ratio_Output:
    result = {}
    session = SessionLocal()


    for company in input_data.company_names:
        year = input_data.year
        query = text("""
                SELECT
                f.ratio_date AS year,   
                f.debtor_days,
                f.inventory_days,
                f.days_payable,
                f.cash_conversion_cycle,
                f.working_capital_days,
                f.roce_percentage,
                f.roe_percentage
                FROM financial_ratios f
                INNER JOIN companies c ON f.company_id = c.id
                WHERE c.company_name = :company  AND YEAR(f.ratio_date) = :year
            """)

        try:
            row = session.execute(query, {
                "company": company,
                "year": input_data.year  # ✅ Year should be int for SQL
            }).mappings().fetchone()
        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}  # ✅ always return dict
            continue

        if not row:
            result[company] = {"error": "Data not available"}
        else:
            all_fields = {
                    "total_financial_ratio" : ["financial ratio","financial ratios", "ratios"],
                    "ratio_date": ["ratio date", "date", "reporting date", "data as of", "period end", "fiscal date"],
                    "debtor_days": ["debtor days", "receivables days", "days sales outstanding", "dso", "debtor turnover days", "avg collection period"],
                    "inventory_days": ["inventory days", "days inventory outstanding", "inventory holding period", "inventory turnover days", "doi"],
                    "days_payable": ["days payable", "payable days", "days payables outstanding", "dpo", "average payment period", "creditor days"],
                    "cash_conversion_cycle": ["cash conversion cycle", "ccc", "working capital cycle", "cash cycle", "net operating cycle"],
                    "working_capital_days": ["working capital days", "net working capital days", "wc days", "working capital cycle"],
                    "roce_percentage": ["roce percent","roce ratio", "roce %", "return on capital employed", "roce", "operating return", "capital efficiency"],
                    "roe_percentage": ["roe percent", "roe ratio", "roe %", "return on equity", "roe", "shareholders return", "equity return", "net worth return"]
                }

             # Filter fields if input_data.fields provided
            if input_data.fields:

                field_data = {
                    i: {
                        # "ratio date" : float(row["ratio_date"]) if row["ratio_date"] is not None else "N/A",
                        "debtor days": float(row["debtor_days"]) if row["debtor_days"] is not None else "N/A",
                        "inventory days" : float(row["inventory_days"]) if row["inventory_days"] is not None else "N/A",
                        "days payable": float(row["days_payable"]) if row["days_payable"] is not None else "N/A",
                        "cash conversion cycle": float(row["cash_conversion_cycle"]) if row["cash_conversion_cycle"] is not None else "N/A",
                        "working capital days": float(row["working_capital_days"]) if row["working_capital_days"] is not None else "N/A",
                        "roce percentage": float(row["roce_percentage"]) if row["roce_percentage"] is not None else "N/A",
                        "roe percentage": float(row["roe_percentage"]) if row["roe_percentage"] is not None else "N/A"
                    } if k == "total_financial_ratio" else float(row[k]) if row[k] is not None else "N/A"
                    for i in input_data.fields
                    for k, v in all_fields.items()
                    if i.lower() in v
                }

            else:
                field_data = all_fields

            year_key = str(row["year"].year) if hasattr(row["year"], 'year') else str(row["year"])
            result[company] = {year_key: field_data}
 

    session.close()

    # ✅ FIXED: Return both comparison and year
    return Financial_Ratio_Output(
        comparison=result,
        year=input_data.year
    )


def company_info(input_data: Company_Info_Input) -> Company_Info_Output:
    result = {}
    session = SessionLocal()

    for company in input_data.company_names:
        query = text("""
            SELECT 
                c.id,
                y.year_period AS year, 
                c.company_name,
                c.sector,
                c.bse,
                c.nse,
                c.market_cap,
                c.current_price,
                c.high_low,
                c.stock_pe,
                c.book_value,
                c.dividend_yield,
                c.roce,
                c.roe,
                c.face_value,
                c.price_to_sales,
                c.sales_growth,
                c.sales_growth_3years,
                c.sales_growth_5years,
                c.sales_growth_7years,
                c.sales_growth_10years,
                c.profit_growth,
                c.profit_growth_3years,
                c.profit_growth_5years,
                c.profit_growth_7years,
                c.profit_growth_10years,
                c.eps,
                c.eps_last_year,
                c.debt,
                c.debt_3years_back,
                c.debt_5years_back,
                c.debt_7years_back,
                c.debt_10years_back
            FROM companies c
            INNER JOIN yearly_pnl y ON c.id = y.company_id
            WHERE c.company_name = :company AND y.year_period = :year
        """)

        try:
            row = session.execute(query, {
                "company": company,
                "year": f"{input_data.year}-03-31"
            }).mappings().fetchone()
        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}
            continue

        if not row:
            result[company] = {"error": "Data not available"}
            continue

        all_fields = {
            "company info": ["basic company details", "company profile", "company details",
                             "company overview", "company summary", "firm profile", "business profile",
                             "corporate profile", "company background", "organization overview", "basic information"],
            "sector": ["industry", "sector", "business segment"],
            "bse": ["bse", "bse code", "bse ticker", "bse symbol"],
            "nse": ["nse", "nse code", "nse ticker", "nse symbol"],
            "market_cap": ["market cap", "market capitalization", "company size", "market value"],
            "current_price": ["current price", "stock price", "share price", "cmp", "current market price"],
            "high_low": ["high low", "52-week high", "52-week low", "stock range"],
            "stock_pe": ["stock pe", "p/e ratio", "price to earnings"],
            "book_value": ["book value", "book value per share", "net asset value"],
            "dividend_yield": ["dividend yield", "dividend %", "payout ratio"],
            "roce": ["roce", "return on capital employed", "efficiency ratio"],
            "roe": ["roe", "return on equity", "shareholder return"],
            "face_value": ["face value", "fv", "nominal value", "par value"],
            "price_to_sales": ["price to sales", "p/s ratio", "price to revenue"],
            "sales_growth": ["sales growth", "revenue growth", "sales increase"],
            "sales_growth_3years": ["sales growth 3years", "3y sales growth", "cagr (sales 3y)", "sales growth of 3 years"],
            "sales_growth_5years": ["sales growth 5years", "5y sales growth", "cagr (sales 5y)", "sales growth of 5 years"],
            "sales_growth_7years": ["sales growth 7years", "7y sales growth", "cagr (sales 7y)", "sales growth of 7 years"],
            "sales_growth_10years": ["sales growth 10years", "10y sales growth", "long-term sales growth", "sales growth of 10 years"],
            "profit_growth": ["profit growth", "net profit growth", "earnings growth"],
            "profit_growth_3years": ["profit growth 3years", "3y profit growth", "cagr (profit 3y)"],
            "profit_growth_5years": ["profit growth 5years", "5y profit growth", "cagr (profit 5y)"],
            "profit_growth_7years": ["profit growth 7years", "7y profit growth", "cagr (profit 7y)"],
            "profit_growth_10years": ["profit growth 10years", "10y profit growth", "long-term profit growth"],
            "eps": ["eps", "earnings per share", "eps (current)"],
            "eps_last_year": ["eps last year", "eps (previous year)", "last year eps"],
            "debt": ["debt", "current debt", "total debt", "outstanding debt"],
            "debt_3years_back": ["debt 3years back", "debt (3y ago)", "historical debt (3y)", "debt 3 years back"],
            "debt_5years_back": ["debt 5years back", "debt (5y ago)", "historical debt (5y)", "debt 5 years back"],
            "debt_7years_back": ["debt 7years back", "debt (7y ago)", "historical debt (7y)", "debt 7 years back"],
            "debt_10years_back": ["debt 10years back", "debt (10y ago)", "historical debt (10y)", "debt 10 years back"]
        }
        
        if input_data.fields:
            requested = [f.lower() for f in input_data.fields]
            field_data = {}

            # Handle special case: "return ratios"
            if "eps trends" in requested or "earing per share trends" in requested:
                field_data["company name"] = str(row["company_name"]) if row["company_name"] is not None else "N/A"
                field_data["eps"] = float(row["eps"]) if row["nse"] is not None else "N/A"
                field_data["eps_last_year"] = float(row["eps_last_year"]) if row["roce"] is not None else "N/A"

                if row["eps"] is not None and row["eps_last_year"] not in (None, 0):
                    eps_growth = ((float(row["eps"]) - float(row["eps_last_year"])) / float(row["eps_last_year"])) * 100
                    field_data["eps_growth"] = f"{round(eps_growth, 2)}%"
                else:
                    field_data["eps_growth"] = "N/A"


            if "return ratios" in requested:
                field_data["company name"] = str(row["company_name"]) if row["company_name"] is not None else "N/A"
                field_data["nse"] = str(row["nse"]) if row["nse"] is not None else "N/A"
                field_data["roce"] = float(row["roce"]) if row["roce"] is not None else "N/A"
                field_data["roe"] = float(row["roe"]) if row["roe"] is not None else "N/A"
                field_data["stock pe"] = float(row["stock_pe"]) if row["stock_pe"] is not None else "N/A"
                if row["stock_pe"] is not None and row["stock_pe"] != 0:
                    field_data["earnings_yield"] = f"{round((1 / float(row['stock_pe'])) * 100, 2)}%"
                    
                else:
                    field_data["earnings_yield"] = "N/A"

            if "debt trends" in requested and "debt growth" in requested:
                field_data["company name"] = str(row["company_name"]) if row["company_name"] is not None else "N/A"
                field_data["nse"] = str(row["nse"]) if row["nse"] is not None else "N/A"
                field_data["debt"] = float(row["debt"]) if row["debt"] is not None else "N/A"
                field_data["debt_3years_back"] = float(row["debt_3years_back"]) if row["roe"] is not None else "N/A"
                field_data["debt_5years_back"] = float(row["debt_5years_back"]) if row["debt_5years_back"] is not None else "N/A"
                field_data["debt_7years_back"] = float(row["debt_7years_back"]) if row["debt_7years_back"] is not None else "N/A"
                field_data["debt_10years_back"] = float(row["debt_10years_back"]) if row["debt_10years_back"] is not None else "N/A"
                if row["debt"] is not None and row["debt_5years_back"] != 0:
                    field_data["debt_growth_5y"] = f"{round(((float(row['debt']) - float(row['debt_5years_back'])) / float(row['debt_5years_back'])) * 100, 2)}%"
                    
                else:
                    field_data["debt_growth_5y"] = "N/A"
            else:
                for user_field in requested:
                    for key, aliases in all_fields.items():
                        if user_field in aliases:
                            value = row.get(key)
                            if key in ["nse", "bse", "sector"]:
                                field_data[user_field] = str(value) if value is not None else "N/A"
                            elif key == "high_low":
                                field_data[user_field] = value.strip() if value is not None else "N/A"
                            elif isinstance(value, (int, float, Decimal)):
                                field_data[user_field] = float(value)

                            elif key == "company info":
                                field_data = {k: str(v) if v is not None else "N/A" for k, v in row.items()}

                            else:
                                field_data[user_field] = "N/A"
                            break
                    # else:
                    #     field_data[user_field] = "Invalid field"


        # else:
        #     # No specific fields requested, return all raw DB fields
           
        year_key = str(row["year"].year) if hasattr(row["year"], 'year') else str(row["year"])
        result[company] = {year_key: field_data}

    session.close()

    return Company_Info_Output(
        comparison=result,
        year=input_data.year
    )


#For net income
def compare_net_income(input_data: CompareNetIncomeInput) -> CompareNetIncomeOutput:
    result = {}
    session = SessionLocal()


    for company in input_data.company_names:
        year = input_data.year
        query = text("""
                SELECT y.net_profit AS net_income,
                y.year_period AS year,
                y.sales,
                y.expenses,
                y.operating_profit,
                y.omp_percentage,
                y.other_income,
                y.interest,
                y.depreciation,
                y.profit_before_tax,
                y.tax_percentage,
                y.eps_in_rs,
                y.revenue,
                y.financing_profit,
                y.financing_margin_percentage
                FROM yearly_pnl y
                INNER JOIN companies c ON y.company_id = c.id
                WHERE c.company_name = :company  AND YEAR(y.year_period) = :year
            """)

        try:
            row = session.execute(query, {
                "company": company,
                "year": int(input_data.year)  # ✅ Year should be int for SQL
            }).mappings().fetchone()
        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}  # ✅ always return dict
            continue

        if not row:
            result[company] = {"error": "Data not available"}
        else:
            all_fields = {
                "yearly_income_statement":["profit and loss statement", "income statement", "financial statement","three financial statement"],
                "net_income": ["net income","net profit", "profit after tax", "bottom line"],
                "sales": ["turnover", "gross sales", "total sales","sales"],
                "expenses": ["total expenses", "operating expenses", "costs", "expenses"],
                "operating_profit" : ["ebit", "earnings before interest and taxes", "operating income", "operating profit"],
                "other_income": ["non-operating income", "miscellaneous income", "other income"],
                "interest" : ["interest expense", "finance costs", "interest paid", "interest"],
                "depreciation": ["depreciation expense", "amortization", "depreciation"],
                "profit_before_tax" : ["pbt", "earnings before tax", "pre-tax profit", "profit before tax"],
                "tax_percentage" : ["effective tax rate", "tax rate", "tax percentage"],
                "eps_in_rs" : ["earnings per share", "basic eps","eps", "eps in rs"],
                "revenue" : ["total revenue", "gross revenue", "income", "revenue"],
                "financing_profit" : ["net interest income", "financial income", "financing profit"],
                "financing_margin_percentage" : ["net interest margin", "financial margin", "financing margin percentage"],
                "omp_percentage" : ["omp", "opm", "operating profit margin","omp percentage"],
                "net_margin_" : ["net margin"]
            }
             # Filter fields if input_data.fields provided
            if input_data.fields:
                # requested_fields = [f.lower() for f in input_data.fields]
                # field_data = {field: all_fields[field] for field in requested_fields if field in all_fields}

                field_data = {
                    i: {
                        "net income" : float(row["net_income"]) if row["net_income"] is not None else "N/A",
                        "sales": float(row["sales"]) if row["sales"] is not None else "N/A",
                        "expenses" : float(row["expenses"]) if row["expenses"] is not None else "N/A",
                        "operating profit": float(row["operating_profit"]) if row["operating_profit"] is not None else "N/A",
                        "other income": float(row["other_income"]) if row["other_income"] is not None else "N/A",
                        "interest": float(row["interest"]) if row["interest"] is not None else "N/A",
                        "depreciation": float(row["depreciation"]) if row["depreciation"] is not None else "N/A",
                        "profit before tax": float(row["profit_before_tax"]) if row["profit_before_tax"] is not None else "N/A",
                        "tax percentage": float(row["tax_percentage"]) if row["tax_percentage"] is not None else "N/A",
                        "eps in rs": float(row["eps_in_rs"]) if row["eps_in_rs"] is not None else "N/A",
                        "revenue": float(row["revenue"]) if row["revenue"] is not None else "N/A",
                        "financing_profit": float(row["financing_profit"]) if row["financing_profit"] is not None else "N/A",
                        "financing margin percentage": float(row["financing_margin_percentage"]) if row["financing_margin_percentage"] is not None else "N/A",
                        "omp percentage": float(row["omp_percentage"]) if row["omp_percentage"] is not None else "N/A",
                    } if k == "yearly_income_statement" else (
                        calculate_net_margin(row["net_income"], row["sales"]) if k == "net_margin_" is not None else 
                        float(row[k]) if row[k] is not None else "N/A"
                    )
                    for i in input_data.fields
                    for k, v in all_fields.items()
                    if i.lower() in v
                }
                # field_data = {keyword : float(row[field]) if row[field] is not None else "N/A"
                #             for keyword in input_data.fields 
                #             for field, aliases in all_fields.items()if keyword.lower() in aliases }

            else:
                field_data = all_fields

            year_key = str(row["year"].year) if hasattr(row["year"], 'year') else str(row["year"])
            result[company] = {year_key: field_data}
 
    

    session.close()

    # ✅ FIXED: Return both comparison and year
    return CompareNetIncomeOutput(
        comparison=result,
        year=input_data.year
    )


#For cash flow
def cash_flow(input_data: CashFlowInput) -> CashFlowOutput:
    result = {}
    session = SessionLocal()
    
    
    for company in input_data.company_names:
        year = input_data.year
        query = text("""
                    SELECT
                    c.company_name,
                    y.cashflow_date as year, 
                    y.cash_from_operating_activity, 
                    y.cash_from_investing_activity, 
                    y.cash_from_financing_activity, 
                    y.net_cash_flow 
                    FROM yearly_cash_flow y 
                    INNER JOIN companies c ON y.company_id = c.id
                    WHERE c.company_name = :company  AND YEAR(y.cashflow_date) = :year
                """)

        try:
            row = session.execute(query, {
                "company": company,
                "year": int(input_data.year)  # ✅ Year should be int for SQL
            }).mappings().fetchone()
        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}  # ✅ always return dict
            continue

        if not row:
            result[company] = {"error": "Data not available"}
        else:
            all_fields = {
                "cash_from_operating_activity": ["cash from operating activities","operating activities", "net cash from operations","operating cash flow","cash flow from operations"],
                "cash_from_investing_activity": ["cash from investing activities", "investing activities", "net cash used in investing","investing cash flow"],
                "cash_from_financing_activity": ["cash from financing activities","financing activities","net cash from financing","financing cash flow"],
                "net_cash_flow": ["net cash flow", "net increase/decrease in cash","net change in cash","cash flow"],
                "cash_flow" : ["cash flow", "cash movements","statement of cash flows","overall cash flow","financial statement", "three financial statement"]
            }


             # Filter fields if input_data.fields provided
            if input_data.fields:
                # requested_fields = [f.lower() for f in input_data.fields]
                field_data = {
                    i: {
                        "cash from operating activities": float(row["cash_from_operating_activity"]) if row["cash_from_operating_activity"] is not None else "N/A",
                        "cash from investing activities": float(row["cash_from_investing_activity"]) if row["cash_from_investing_activity"] is not None else "N/A",
                        "cash from financing activities": float(row["cash_from_financing_activity"]) if row["cash_from_financing_activity"] is not None else "N/A",
                        "net cash flow": float(row["net_cash_flow"]) if row["net_cash_flow"] is not None else "N/A",
                    } if k == "cash_flow" else float(row[k]) if row[k] is not None else "N/A"
                    for i in input_data.fields
                    for k, v in all_fields.items()
                    if i.lower() in v
                }
                # field_data = {field: all_fields[field] for field in requested_fields if field in all_fields}
            else:
                field_data = all_fields

            year_key = str(row["year"].year) if hasattr(row["year"], 'year') else str(row["year"])
            result[company] = {year_key: field_data}


    session.close()

    # ✅ FIXED: Return both comparison and year
    return CashFlowOutput(
        comparison=result,
        year=input_data.year
    )


#For balance sheet
def summarize_balance_sheet(input_data: SummarizeBalanceSheetInput) -> SummarizeBalanceSheetOutput:
    session = SessionLocal()
    result = {}
   
    for company in input_data.company_names:
        query = text("""
            SELECT
                c.company_name, 
                y.balance_date AS year, 
                y.total_assets,
                y.total_liabilities,
                y.borrowings AS net_loans,
                y.equity_capital,
                y.reserves,
                y.other_liabilities,
                y.fixed_assets,
                y.cwip,
                y.investments,
                y.other_assets,
                y.Preference_Capital
            FROM companies c
            INNER JOIN yearly_balance_sheet y ON c.id = y.company_id
            WHERE c.company_name = :company
            AND YEAR(y.balance_date) = :balance_date
            LIMIT 1
        """)

        try:
            row = session.execute(query, {
                "company": company,
                "balance_date": f"{input_data.year}-03-31"
            }).mappings().fetchone()
        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}
            continue
        
        if not row:
            result[company] = {"error": "Data not found"}
            continue
        
        # All fields available in the DB row
        all_fields = {
            "balance_sheet": [ "balance sheet", "statement of financial position","financial statement", "three financial statement"],
            "total_assets": [ "total assets","gross assets", "sum of assets"],
            "net_loans": ["net loans","net advances", "loans and advances (net)", "net loan portfolio"],
            "total_liabilities": ["total liabilities", "aggregate liabilities", "total obligations"],
            "equity_capital": [ "equity capital", "shareholders’ equity", "owner’s equity", "paid-up capital", "common equity"],
            "reserves": ["reserves", "retained earnings", "surplus reserves", "capital reserves"],
            "other_liabilities": ["other liabilities", "miscellaneous liabilities", "sundry liabilities"],
            "fixed_assets": ["fixed assets", "property, plant & equipment (PPE)", "tangible assets"],
            "cwip": [ "cwip", "capital work-in-progress", "assets under construction"],
            "investments": ["investments", "long-term investments", "financial investments"],
            "other_assets": ["other assets", "miscellaneous assets", "sundry assets"],
            "Preference_Capital": ["preference capital", "preferred stock", "preference shares"]
        }
        
        # Filter fields if input_data.fields provided
        if input_data.fields:
            # requested_fields = [f.lower() for f in input_data.fields]
            summary = {
                    i: {
                        "total assets" : float(row["total_assets"]) if row["total_assets"] is not None else "N/A",
                        "net loans": float(row["net_loans"]) if row["net_loans"] is not None else "N/A",
                        "total liabilities" : float(row["total_liabilities"]) if row["total_liabilities"] is not None else "N/A",
                        "equity capital": float(row["equity_capital"]) if row["equity_capital"] is not None else "N/A",
                        "reserves": float(row["reserves"]) if row["reserves"] is not None else "N/A",
                        "other liabilities": float(row["other_liabilities"]) if row["other_liabilities"] is not None else "N/A",
                        "fixed assets": float(row["fixed_assets"]) if row["fixed_assets"] is not None else "N/A",
                        "cwip": float(row["cwip"]) if row["cwip"] is not None else "N/A",
                        "investments": float(row["investments"]) if row["investments"] is not None else "N/A",
                        "other assets": float(row["other_assets"]) if row["other_assets"] is not None else "N/A",
                        "Preference Capital": float(row["Preference_Capital"]) if row["Preference_Capital"] is not None else "N/A",
                    } if k == "balance_sheet" else float(row[k]) if row[k] is not None else "N/A"
                    for i in input_data.fields
                    for k, v in all_fields.items()
                    if i.lower() in v
                }
        else:
            summary = all_fields

        result[company] = {input_data.year: summary}

    session.close()

    return SummarizeBalanceSheetOutput(
        comparison=result,
        year = input_data.year
    )


#For yearly shareholding
def yearly_shareholding(input_data: YearlyShareholdingInput) -> YearlyShareholdingOutput:
    result = {}
    session = SessionLocal()
    
    
    for company in input_data.company_names:
        year = input_data.year
        query = text("""        
                SELECT 
                y.yearly_shareholding_date AS year,
                y.promoters,
                y.fiis,
                y.diis,
                y.public,
                y.no_of_shareholders,
                y.others,
                y.government
                FROM yearly_shareholding y
                INNER JOIN companies c ON y.company_id = c.id
                WHERE c.company_name = :company  AND YEAR(y.yearly_shareholding_date) = :year
            """)

        try:
            row = session.execute(query, {
                "company": company,
                "year": input_data.year  # ✅ Year should be int for SQL
            }).mappings().fetchone()
        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}  # ✅ always return dict
            continue

        if not row:
            result[company] = {"error": "Data not available"}
        else:
            all_fields = {
                "shareholdingpattern": ["shareholdingpattern","shareholding pattern", "ownership structure", "capital structure", "institutional holding pattern"],
                "promoters": ["promoters", "promoter holding", "promoter group", "owner holding", "founders", "controlling shareholders"],
                "fiis": ["fiis", "fii holding", "foreign institutional investors", "foreign investors", "overseas shareholders"],
                "diis": ["diis", "dii holding", "domestic institutional investors", "mutual funds", "insurance companies"],
                "public": ["public", "public holding", "retail investors", "non-institutional investors", "general public"],
                "no_of_shareholders": ["no of shareholders", "shareholder count", "number of shareholders", "investor base size"],
                "others": ["others", "others category", "miscellaneous holding", "unidentified shareholders"],
                "government": ["government", "government holding", "state holding", "public sector holding", "govt stake"]
            }


             # Filter fields if input_data.fields provided
            if input_data.fields:

                field_data = {
                    i: {
                        # "ratio date" : float(row["ratio_date"]) if row["ratio_date"] is not None else "N/A",
                        "promoters": float(row["promoters"]) if row["promoters"] is not None else "N/A",
                        "fiis" : float(row["fiis"]) if row["fiis"] is not None else "N/A",
                        "diis": float(row["diis"]) if row["diis"] is not None else "N/A",
                        "public": float(row["public"]) if row["public"] is not None else "N/A",
                        "no. of shareholders": float(row["no_of_shareholders"]) if row["no_of_shareholders"] is not None else "N/A",
                        "others": float(row["others"]) if row["others"] is not None else "N/A",
                        "government": float(row["government"]) if row["government"] is not None else "N/A"
                    } if k == "shareholdingpattern" else float(row[k]) if row[k] is not None else "N/A"
                    for i in input_data.fields
                    for k, v in all_fields.items()
                    if i.lower() in v
                }

            else:
                field_data = all_fields

            year_key = str(row["year"].year) if hasattr(row["year"], 'year') else str(row["year"])
            result[company] = {year_key: field_data}
            
    
    session.close()

    # ✅ FIXED: Return both comparison and year
    return YearlyShareholdingOutput(
        comparison=result,
        year=input_data.year
    )



#For quarterly income
def compare_quarterly_income(input_data: QuarterlyIncomeInput) -> QuarterlyIncomeOutput:
    result = {}
    session = SessionLocal()
    
    all_fields = {
        "quaterly_income_statement": ["profit and loss statement","quarterly profit and loss statement", "income statement" , "quarterly results", "quarterly pnl","quarter wise results"],
        "sales": ["turnover", "gross sales", "total sales", "revenue", "sales"],
        "expenses": ["total expenses", "operating expenses", "costs", "outflows", "expenses"],
        "operating_profit": ["ebit", "earnings before interest and taxes", "operating income", "operating profit"],
        "opm_percentage": ["operating margin %", "operating profit margin", "opm %", "opm percentage"],
        "other_income": ["non-operating income", "miscellaneous income", "additional income", "other income"],
        "interest": ["interest expense", "finance costs", "interest paid", "interest"],
        "depreciation": ["depreciation expense", "amortization", "depreciation"],
        "profit_before_tax": ["pbt", "earnings before tax", "pre-tax profit", "ebt", "profit before tax"],
        "tax_percentage": ["effective tax rate", "tax rate", "tax percentage"],
        "net_profit": ["net income", "profit after tax", "bottom line", "earnings", "net profit"],
        "eps_in_rs": ["earnings per share", "basic eps", "eps in rs"],
        "revenue": ["total revenue", "gross revenue", "income", "revenue"],
        "financing_profit": ["net interest income", "financial income", "financing profit"],
        "financing_margin": ["net interest margin", "financial margin", "financing margin"],
        "gross_npa": ["gross non-performing assets", "gross npa ratio", "gross npa"],
        "net_npa": ["net non-performing assets", "net npa ratio", "non-performing assets", "net npa"]
    }



    def resolve_field(user_field: str) -> Union[str, None]:
        for key, aliases in all_fields.items():
            if user_field.lower() in aliases:
                return key
        return None

    def get_month_and_adjusted_year(quarter: str, year: int):
        if "first" in quarter:
            return 6, year
        elif "second" in quarter:
            return 9, year
        elif "third" in quarter:
            return 12, year
        elif "fourth" in quarter:
            return 3, year + 1
        return None, year

    for company in input_data.company_names:
        try:
            base_query = """
                SELECT
                    q.net_profit,
                    q.quarter_date AS year,
                    q.sales,
                    q.expenses,
                    q.operating_profit,
                    q.opm_percentage,
                    q.other_income,
                    q.interest,
                    q.depreciation,
                    q.profit_before_tax,
                    q.tax_percentage,
                    q.net_profit,
                    q.eps_in_rs,
                    q.revenue,
                    q.financing_profit,
                    q.financing_margin,
                    q.gross_npa,
                    q.net_npa
                FROM quarterly_pnl q
                INNER JOIN companies c ON q.company_id = c.id
                WHERE c.company_name = :company AND YEAR(q.quarter_date) = :year
            """

            rows = []
            params = {"company": company, "year": int(input_data.year)}
            # 
            if input_data.quarter_month:
                for qtr in input_data.quarter_month:
                    month, year_adj = get_month_and_adjusted_year(qtr, int(input_data.year))
                    query = base_query + " AND MONTH(q.quarter_date) = :month AND YEAR(q.quarter_date) = :year"
                    q_params = {"company": company, "year": year_adj, "month": month}
                    data = session.execute(text(query), q_params).mappings().fetchall()
                    rows.extend(data)
            else:
                data = session.execute(text(base_query), params).mappings().fetchall()
                rows = [r for r in data if r["year"].month != 3]
                q4_params = {"company": company, "year": int(input_data.year) + 1, "month": 3}
                q4_query = base_query + " AND MONTH(q.quarter_date) = :month AND YEAR(q.quarter_date) = :year"
                q4_data = session.execute(text(q4_query), q4_params).mappings().fetchall()
                rows.extend(q4_data)

        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}
            continue

        
        

        if not rows:
            result[company] = {"error": "Data not available"}
            continue
        
        resolved_fields = [resolve_field(f) for f in input_data.fields if resolve_field(f)]
        

        field_data = {}

        if "quarterly performance" in input_data.fields:
            performance_data = {}

            # Sort rows by 'quarter_date' or 'year' in descending order
            rows = sorted(rows, key=lambda x: x["year"], reverse=True)

            # Optional: define quarters for readability
            quarters = ["Q4", "Q3", "Q2", "Q1"]
            company_name_d = "".join(input_data.company_names)

            for index, row in enumerate(rows):
                quarter_label = quarters[index % 4]  # wrap around if more than 4 quarters
                key = f"{row['year']} {quarter_label}"  # e.g., "2022 Q1"

                performance = {
                    "company name": company_name_d or "N/A",
                    "quarter date": str(row["year"]) or "N/A",
                    "sales": float(row["sales"]) if row["sales"] is not None else "N/A",
                    "net profit": float(row["net_profit"]) if row["net_profit"] is not None else "N/A",
                    "opm percentage": float(row["opm_percentage"]) if row["opm_percentage"] is not None else "N/A",
                    "eps in rs": float(row["eps_in_rs"]) if row["eps_in_rs"] is not None else "N/A"
                }

                performance_data[key] = performance  # ✅ dictionary, not list

            field_data["quarterly performance"] = performance_data  # ✅ now a dict



        if "quaterly_income_statement" not in resolved_fields:
            for field in resolved_fields:
                field_data[field] = {
                    str(r["year"]): format(r[field], ".4f") if r[field] is not None else "N/A"
                    for r in rows
                    if field in r and (
                        r["year"].year == int(input_data.year) or
                        (r["year"].year == int(input_data.year) + 1 and r["year"].month == 3)
                    )
                }
        else:
            if isinstance(rows, dict):
                field_data = {
                    str(rows["year"]): {
                        k: float(v) if v is not None else "N/A"
                        for k, v in rows.items() if k != "year"
                    }
                }
            else:
                field_data = {
                    str(row["year"]): {
                        k: float(v) if v is not None else "N/A"
                        for k, v in row.items() if k != "year"
                    }
                    for row in rows
                }

        result[company] = field_data

    session.close()

    return QuarterlyIncomeOutput(
        comparison=result,
        year=input_data.year
    )


#For quarterly shareholding
def quarterly_shareholding(input_data: QuarterlyShareholdingInput) -> QuarterlyShareholdingOutput:
    result = {}
    session = SessionLocal()
    
    all_fields = {
        "shareholdingpattern": ["shareholdingpattern","shareholding pattern", "ownership structure", "capital structure", "institutional holding pattern"],
        "promoters": ["promoters", "promoter holding", "promoter group", "owner holding", "founders", "controlling shareholders"],
        "fiis": ["fiis", "fii holding", "foreign institutional investors", "foreign investors", "overseas shareholders"],
        "diis": ["diis", "dii holding", "domestic institutional investors", "mutual funds", "insurance companies"],
        "public": ["public", "public holding", "retail investors", "non-institutional investors", "general public"],
        "no_of_shareholders": ["no of shareholders", "shareholder count", "number of shareholders", "investor base size"],
        "others": ["others", "others category", "miscellaneous holding", "unidentified shareholders"],
        "government": ["government", "government holding", "state holding", "public sector holding", "govt stake"]
    }
    

    def resolve_field(user_field: str) -> Union[str, None]:
        for key, aliases in all_fields.items():
            if user_field.lower() in aliases:
                return key
        return None

    def get_month_and_adjusted_year(quarter: str, year: int):
        if "first" in quarter:
            return 6, year
        elif "second" in quarter:
            return 9, year
        elif "third" in quarter:
            return 12, year
        elif "fourth" in quarter:
            return 3, year + 1
        return None, year

    for company in input_data.company_names:
        try:
            base_query = """
            SELECT 
            q.shareholding_date AS year,
            q.promoters,
            q.fiis,
            q.diis,
            q.public,
            q.no_of_shareholders,
            q.others,
            q.government
            FROM quarterly_shareholding q
            INNER JOIN companies c ON q.company_id = c.id
            WHERE c.company_name = :company AND YEAR(q.shareholding_date) = :year
            """
               
            rows = []
            params = {"company": company, "year": int(input_data.year)}
            # 
            if input_data.quarter_month:
                for qtr in input_data.quarter_month:
                    month, year_adj = get_month_and_adjusted_year(qtr, int(input_data.year))
                    query = base_query + " AND MONTH(q.shareholding_date ) = :month AND YEAR(q.shareholding_date ) = :year"
                    q_params = {"company": company, "year": year_adj, "month": month}
                    data = session.execute(text(query), q_params).mappings().fetchall()
                    rows.extend(data)
            else:
                data = session.execute(text(base_query), params).mappings().fetchall()
                rows = [r for r in data if r["year"].month != 3]
                q4_params = {"company": company, "year": int(input_data.year) + 1, "month": 3}
                q4_query = base_query + " AND MONTH(q.shareholding_date) = :month AND YEAR(q.shareholding_date) = :year"
                q4_data = session.execute(text(q4_query), q4_params).mappings().fetchall()
                rows.extend(q4_data)

        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}
            continue

        if not rows:
            result[company] = {"error": "Data not available"}
            continue

        resolved_fields = [resolve_field(f) for f in input_data.fields if resolve_field(f)]

        if "shareholdingpattern" not in resolved_fields:
            field_data = {}
            for field in resolved_fields:
                field_data[field] = {
                    str(r["year"]): format(r[field], ".4f") if r[field] is not None else "N/A"
                    for r in rows
                    if field in r and (
                        r["year"].year == int(input_data.year) or
                        (r["year"].year == int(input_data.year) + 1 and r["year"].month == 3)
                    )
                }
        else:
            if isinstance(rows, dict):
                field_data = {
                    str(rows["year"]): {
                        k: float(v) if v is not None else "N/A"
                        for k, v in rows.items() if k != "year"
                    }
                }
            else:
                field_data = {
                    str(row["year"]): {
                        k: float(v) if v is not None else "N/A"
                        for k, v in row.items() if k != "year"
                    }
                    for row in rows
                }

        result[company] = field_data

    session.close()

    return QuarterlyIncomeOutput(
        comparison=result,
        year=input_data.year
    )



#For company info
def sector_wise_company(input_data: SectorWiseCompanyInput) -> SectorWiseCompanyOutput:
    result = {}
    session = SessionLocal()

    
    for sector in input_data.sector:
        query = text("""
                SELECT 
                    company_name, 
                    nse, 
                    bse, 
                    market_cap, 
                    current_price, 
                    stock_pe, 
                    roe, 
                    roce 
                FROM companies
                WHERE sector = :sector
                ORDER BY market_cap DESC, roe DESC, roce DESC, stock_pe DESC
            """)

        try:
            rows = session.execute(query, {"sector": sector}).mappings().fetchall()
            if rows:
                result[sector] = [dict(row) for row in rows]
            else:
                result[sector] = {"message": "No data found for this sector"}
        except Exception as e:
            result[sector] = {"error": f"Query failed: {str(e)}"}
        # 
        if not rows:
            result[sector] = {"error": "Data not available"}

    cleaned_result = {}
    for sector, companies in result.items():
        cleaned_companies = []

        for company in companies:
            cleaned_company = {}
            for key, value in company.items():
                if isinstance(value, Decimal):
                    cleaned_company[key] = float(value)
                else:
                    cleaned_company[key] = value
            cleaned_companies.append(cleaned_company)

        cleaned_result[sector] = cleaned_companies


    session.close()

    # ✅ FIXED: Return both comparison and year
    return SectorWiseCompanyOutput(
        comparison=cleaned_result
    )


#For cash flow to debt
def cash_flow_to_debt(tool_name, parameters):
    if tool_name != "cash_flow_to_debt_":
        return None  # Or raise an error if invalid tool

    # Step 1: Extract cash from operating activities
    cashflow_params = parameters.copy()
    cashflow_params["fields"] = [parameters["fields"][0]]  # e.g., "cash from operating activities"
    validated_cashflow = CashFlowInput(**cashflow_params)
    cash_data = cash_flow(validated_cashflow).dict()

    # Step 2: Extract net loans
    balance_params = parameters.copy()
    balance_params["fields"] = [parameters["fields"][1]]  # e.g., "net loans"
    validated_balance = SummarizeBalanceSheetInput(**balance_params)
    loans_data = summarize_balance_sheet(validated_balance).dict()

    # Step 3: Dynamically extract the value
    company_name = list(cash_data["comparison"].keys())[0]
    year = cash_data.get("year")

    cash_value = cash_data["comparison"][company_name][year].get(parameters["fields"][0])
    loan_value = loans_data["comparison"][company_name][year].get(parameters["fields"][1])

    # Step 4: Avoid division by zero
    if loan_value in [0, None]:
        return None

    return {
    "comparison": {
        company_name: {
            year: {
                "cash flow to debt ratio": round(cash_value / loan_value, 4)
            }
        }
    },
    "year": year
}


#For debt to financing ratio
def debt_to_financing_ratio(tool_name, parameters):
    
    if tool_name != "debt_to_financing_ratio_":
        return None  # Or raise an error if invalid tool


    # Step 2: Extract net loans
    balance_params = parameters.copy()
    balance_params["fields"] = [parameters["fields"][0]]  # e.g., "net loans"
    validated_balance = SummarizeBalanceSheetInput(**balance_params)
    loans_data = summarize_balance_sheet(validated_balance).dict()

    # Step 1: Extract cash from operating activities
    cashflow_params = parameters.copy()
    cashflow_params["fields"] = [parameters["fields"][1]]  # e.g., "cash from operating activities"
    validated_cashflow = CashFlowInput(**cashflow_params)
    cash_data = cash_flow(validated_cashflow).dict()

    # Step 3: Dynamically extract the value
    company_name = list(cash_data["comparison"].keys())[0]
    year = cash_data.get("year")

    loan_value = loans_data["comparison"][company_name][year].get(parameters["fields"][0])
    cash_value = cash_data["comparison"][company_name][year].get(parameters["fields"][1])

    # Step 4: Avoid division by zero
    if cash_value in [0, None]:
        return None

    return {
    "comparison": {
        company_name: {
            year: {
                "debt to financing ratio": f"{round((loan_value / cash_value)*100, 2)}%"
            }
        }
    },
    "year": year
}

#For operating cash flow interest
def operating_cf_to_interest(tool_name, parameters):
    
    if tool_name != "operating_cf_to_interest_":
        return None  # Or raise an error if invalid tool


    # Step 1: Extract cash from operating activities
    cashflow_params = parameters.copy()
    cashflow_params["fields"] = [parameters["fields"][0]]  # e.g., "cash from operating activities"
    validated_cashflow = CashFlowInput(**cashflow_params)
    cash_data = cash_flow(validated_cashflow).dict()

    # Step 2: Extract net interest
    balance_params = parameters.copy()
    balance_params["fields"] = [parameters["fields"][1]]  # e.g., "net interest"
    validated_balance = CompareNetIncomeInput(**balance_params)
    interest_data = compare_net_income(validated_balance).dict()

    # Step 3: Dynamically extract the value
    company_name = list(cash_data["comparison"].keys())[0]
    year = cash_data.get("year")
    date_key = list(interest_data["comparison"][company_name].keys())[0]
    
    cash_value = cash_data["comparison"][company_name][year].get(parameters["fields"][0])
    interest_value = interest_data["comparison"][company_name][date_key].get(parameters["fields"][1])

    # Step 4: Avoid division by zero
    if interest_value in [0, None]:
        return None

    return {
    "comparison": {
        company_name: {
            year: {
                "operating cash flow to interest": round(cash_value / interest_value, 4)
            }
        }
    },
    "year": year
}

#For net cash flow margin
def net_cash_flow_margin(tool_name, parameters):

    if tool_name != "_net_c_f_margin":
        return None  # Or raise an error if invalid tool


    # Step 1: Extract cash from operating activities
    cashflow_params = parameters.copy()
    cashflow_params["fields"] = [parameters["fields"][0]]  # e.g., "cash flow"
    validated_cashflow = CashFlowInput(**cashflow_params)
    cash_data = cash_flow(validated_cashflow).dict()

    # Step 2: Extract net interest
    balance_params = parameters.copy()
    balance_params["fields"] = [parameters["fields"][1]]  # e.g., "sales"
    validated_balance = CompareNetIncomeInput(**balance_params)
    sales_data = compare_net_income(validated_balance).dict()

    # Step 3: Dynamically extract the value
    company_name = list(cash_data["comparison"].keys())[0]
    year = cash_data.get("year")
    date_key = list(sales_data["comparison"][company_name].keys())[0]
    
    cash_value = cash_data["comparison"][company_name][year].get(parameters["fields"][0])
    sales_value = sales_data["comparison"][company_name][date_key].get(parameters["fields"][1])

    # Step 4: Avoid division by zero
    if sales_data in [0, None]:
        return None

    return {
    "comparison": {
        company_name: {
            year: {
                "net cash flow margin": f"{round((cash_value / sales_value)*100, 2)}%"
            }
        }
    },
    "year": year
}


#For fixed asset turnover
def fixed_asset_turnover(tool_name, parameters):

    if tool_name != "_fixed_asset_turnover_ratio":
        return None  # Or raise an error if invalid tool

         # Step 2: Extract net interest
    balance_params = parameters.copy()
    balance_params["fields"] = [parameters["fields"][0]]  # e.g., "sales"
    validated_balance = CompareNetIncomeInput(**balance_params)
    sales_data = compare_net_income(validated_balance).dict()


    # Step 1: Extract cash from operating activities
    cashflow_params = parameters.copy()
    cashflow_params["fields"] = [parameters["fields"][1]]  # e.g., "cash flow"
    validated_cashflow = SummarizeBalanceSheetInput(**cashflow_params)
    fixed_asset_data = summarize_balance_sheet(validated_cashflow).dict()

    # Step 3: Dynamically extract the value
    company_name = list(fixed_asset_data["comparison"].keys())[0]
    year = fixed_asset_data.get("year")
    date_key = list(sales_data["comparison"][company_name].keys())[0]

    
    sales_value = sales_data["comparison"][company_name][date_key].get(parameters["fields"][0])
    fixed_asset_value = fixed_asset_data["comparison"][company_name][year].get(parameters["fields"][1])

    # Step 4: Avoid division by zero
    if fixed_asset_value in [0, None]:
        return None

    return {
    "comparison": {
        company_name: {
            year: {
                "fixed asset turnover": round(sales_value / fixed_asset_value , 3)
            }
        }
    },
    "year": year
}



#For operating cash
def operating_cash_flow_to_interest(tool_name, parameters):
    
    if tool_name != "_operating_cf_to_liablities":
        return None  # Or raise an error if invalid tool

         # Step 2: Extract net interest
    balance_params = parameters.copy()
    balance_params["fields"] = [parameters["fields"][0]]  # e.g., "sales"
    validated_balance = CashFlowInput(**balance_params)
    cash_data = cash_flow(validated_balance).dict()


    # Step 1: Extract cash from operating activities
    cashflow_params = parameters.copy()
    cashflow_params["fields"] = [parameters["fields"][1]]  # e.g., "cash flow"
    validated_cashflow = SummarizeBalanceSheetInput(**cashflow_params)
    total_liabilities = summarize_balance_sheet(validated_cashflow).dict()

    # Step 3: Dynamically extract the value
    company_name = list(cash_data["comparison"].keys())[0]
    year = cash_data.get("year")
    date_key = list(total_liabilities["comparison"][company_name].keys())[0]

    
    cash_value = cash_data["comparison"][company_name][date_key].get(parameters["fields"][0])
    liabilities_value = total_liabilities["comparison"][company_name][year].get(parameters["fields"][1])

    # Step 4: Avoid division by zero
    if liabilities_value in [0, None]:
        return None

    return {
    "comparison": {
        company_name: {
            year: {
                "Operating CF to liabilities" : f"{round((cash_value / liabilities_value)*100 , 2)}%"
            }
        }
    },
    "year": year
}
