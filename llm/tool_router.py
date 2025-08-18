import re
import json
from data1.db import SessionLocal
from sqlalchemy import text
import difflib
from fuzzywuzzy import fuzz




def get_all_company_sector_names():
    session = SessionLocal()
    query = text("SELECT company_name, sector FROM companies")
    rows = session.execute(query).fetchall()
    session.close()
    
    return [
        {"company_name": row[0], "sector": row[1]}
        for row in rows
    ]



# def get_all_sector_names():
#     session = SessionLocal()
#     query = text("SELECT sector FROM companies")
#     rows = session.execute(query).fetchall()
#     session.close()
#     return [row[0] for row in rows]



def find_matching_companies(user_input: str, company_list: list):
    return [company for company in company_list if company.lower() in user_input.lower()]


def get_typo_tolerant_matches(field_list, user_input, threshold=80, match_ratio=0.8):
    input_words = user_input.lower().split()
    matches = []

    for field in field_list:
        field_words = field.lower().split()
        match_count = 0

        for fw in field_words:
            for iw in input_words:
                if fuzz.ratio(fw, iw) >= threshold:
                    match_count += 1
                    break  # stop checking after first good match

        if (match_count / len(field_words)) >= match_ratio:
            matches.append(field)

    return matches


import re

def get_best_field_from_prompt(gemini_response_lower: str, matching_sheets_yearly_pnl: list) -> list:
    # Clean and tokenize the prompt
    prompt_tokens = re.findall(r'\b\w+\b', gemini_response_lower.lower())
    prompt_text = " ".join(prompt_tokens)

    field_scores = {}

    for field in matching_sheets_yearly_pnl:
        field_tokens = field.lower().split()
        
        # Token match count
        token_match_count = sum(1 for token in field_tokens if token in prompt_tokens)
        
        # Boost if full field appears as a phrase
        full_phrase_boost = 2 if field.lower() in prompt_text else 0
        
        # Small preference to longer fields (e.g., "net income" > "income")
        length_weight = len(field_tokens) * 0.1
        
        # Final score
        score = token_match_count + full_phrase_boost + length_weight
        field_scores[field] = score

    # Sort fields by score in descending order
    sorted_fields = sorted(field_scores.items(), key=lambda x: x[1], reverse=True)

    selected_fields = []
    used_tokens = set()

    for field, _ in sorted_fields:
        field_tokens = set(field.lower().split())
        
        # Skip if this field is fully contained in already selected field tokens (to avoid overlaps like "income" when "net income" is already selected)
        if not field_tokens & used_tokens:
            selected_fields.append(field)
            used_tokens.update(field_tokens)

    return selected_fields


# def get_best_field_from_prompt(gemini_response_lower: str, matching_sheets_yearly_pnl: list) -> str:
#     # Clean and tokenize the prompt
#     prompt_tokens = re.findall(r'\b\w+\b', gemini_response_lower.lower())
#     prompt_text = " ".join(prompt_tokens)

#     field_scores = {}
#     matchess = []

#     for field in matching_sheets_yearly_pnl:
#         field_tokens = field.lower().split()
        
#         # Token match count
#         token_match_count = sum(1 for token in field_tokens if token in prompt_tokens)
        
#         # Boost if full field appears as a phrase
#         full_phrase_boost = 2 if field.lower() in prompt_text else 0
        
#         # Small preference to longer fields (e.g., "net income" > "income")
#         length_weight = len(field_tokens) * 0.1
        
#         # Final score
#         score = token_match_count + full_phrase_boost + length_weight
#         field_scores[field] = score

#     # Return field with highest score
#     if field_scores:
#         matchess.append(max(field_scores, key=field_scores.get))
#         return matchess
#     return None



def extract_tool_call(gemini_response: str) -> dict:
    
    """
    Extracts the tool name and parameters from a Gemini model response.
    Returns:
        dict: with keys "tool_name" and "parameters"
    """
    gemini_response_lower = gemini_response.lower()
    

    matching_sheets_company_info_ = []
    matching_sheets_yearly_pnl = []
    matching_sheets_cashflow = []
    matching_balance_sheet = []
    matching_financial_ratio = []
    matching_sheets_quarterly_pnl = []
    matching_yearly_shareholding = []
    matching_quarterly_shareholding = []
    get_matches_cash_flow_debt = []
    matching_financial_statement = []
    matching_sheets_cashflow_to_debt = []
    get_matches_debt_to_financing_ratio = []
    matching_sheets_debt_to_financing_ratio = []
    get_matches_operating_cash_flow_to_intrest = []
    matching_sheets_operating_cash_flow_to_intrest = []
    matching_sheets_net_cash_flow_margin_ = []
    get_matches_net_cash_flow_margin_ = []
    matching_sheets_fixed_asset_turnover_ = []
    get_matches_fixed_asset_turnover_ = []
    matching_sheets_operating_cf_liabilities_ = []
    get_matches_operating_cf_liabilities = []
    matched_cleaned_sectors = []
    sectors_ = []
    
   
    
    # 
    ALL_COMPANIES_SECTOR = get_all_company_sector_names()
    # companies = find_matching_companies(gemini_response_lower, ALL_COMPANIES)
    ALL_COMPANIES_ = [item["company_name"] for item in ALL_COMPANIES_SECTOR]
    companies_11 = get_typo_tolerant_matches(ALL_COMPANIES_, gemini_response_lower)
    companies = get_best_field_from_prompt(gemini_response_lower, companies_11)


    
   
    # ALL_SECTOR_ = list(set(item["sector"] for item in ALL_COMPANIES_SECTOR))
    # cleaned_list = [re.sub(r'[^A-Za-z ]+', '', item).strip().lower() for item in ALL_SECTOR_]
    # sectors = get_typo_tolerant_matches(cleaned_list, gemini_response_lower)

    # Step 1: Create a cleaned → original sector mapping
    sector_map = {}
    for item in ALL_COMPANIES_SECTOR:
        raw_sector = item["sector"]
        cleaned_sector = re.sub(r'[^A-Za-z ]+', '', raw_sector).strip().lower()
        sector_map[cleaned_sector] = raw_sector  # cleaned:original

    # Step 2: Prepare cleaned list for matching
    cleaned_list = list(sector_map.keys())

    # Step 3: Get typo-tolerant matches from Gemini response
    
    matched_cleaned_sectors = get_typo_tolerant_matches(cleaned_list, gemini_response_lower)

    # Step 4: Convert matched cleaned sectors back to original DB sectors
    if "sector" in gemini_response_lower or "sectors" in gemini_response_lower:
        sectors_ = [sector_map[sec] for sec in matched_cleaned_sectors] 
   

    if not gemini_response_lower:
        return {"tool_name": None, "parameters": {}}

    # ✅ Year extraction
    year_match = re.search(r"\b(20\d{2})\b", gemini_response)
    year = year_match.group(1) if year_match else "2023"


    # 🛠 1. Net Income Tool
    if ("quarter" not in gemini_response_lower and 
        "quarterly" not in gemini_response_lower and
        "roe ratio" not in gemini_response_lower and
        "roce ratio" not in gemini_response_lower and 
        "debtor days" not in gemini_response_lower and
        "avg collection period" not in gemini_response_lower and
        "debtor turnover days" not in gemini_response_lower and
        "dso" not in gemini_response_lower and
        "days sales outstanding" not in gemini_response_lower and
        "receivables days" not in gemini_response_lower and
        "cash flow to debt" not in gemini_response_lower and
        "debt to financing ratio" not in gemini_response_lower and
        "operating cf to interest" not in gemini_response_lower and
        "operating cash flow to interest" not in gemini_response_lower and
        "net cash flow margin" not in gemini_response_lower and
        "fixed asset turnover" not in gemini_response_lower and
        "fixed asset ratio" not in gemini_response_lower and
        "operating cash flow to liabilities" not in gemini_response_lower and
        "operating cf to liabilities"  not in gemini_response_lower and
        "return ratios"  not in gemini_response_lower and
        "earing per share trends"  not in gemini_response_lower and
        "eps trends"  not in gemini_response_lower and
        "debt trends"  not in gemini_response_lower and
        "debt growth"  not in gemini_response_lower



    ):
        # 🛠 1. For company info
        _company_info_ = [
            "basic company details", "company profile", "company profile","basic information","basic info","company details",
            "company overview","company summary", "firm profile","business profile",
            "corporate profile" , "company background", "organization overview",
            "company name", "firm name", "entity name",
            "sector", "industry", "business segment",
            "bse", "bse code", "bse ticker", "bse symbol",
            "nse", "nse code", "nse ticker", "nse symbol",
            "market cap", "market capitalization", "company size", "market value",
            "current price", "stock price", "share price", "cmp (current market price)",
            "high / low", "52-week high", "52-week low", "stock range", "high low",
            "stock p/e", "p/e ratio", "price to earnings", "stock pe",
            "book value", "book value per share", "net asset value",
            "dividend yield", "dividend %", "payout ratio",
            "roce", "return on capital employed", "efficiency ratio",
            "roe", "return on equity", "shareholder return",
            "face value", "fv", "nominal value", "par value",
            "price to sales", "p/s ratio", "price to revenue",
            "sales growth 3years", "3y sales growth", "cagr (sales 3y)","sales growth of 3 years","sales growth of 3year",
            "sales growth 5years", "5y sales growth", "cagr (sales 5y)", "sales growth of 5 years","sales growth of 5year",
            "sales growth 7years", "7y sales growth", "cagr (sales 7y)", "sales growth of 7 years","sales growth of 7year",
            "sales growth 10years", "10y sales growth", "long-term sales growth", "sales growth of 10 years","sales growth of 10year",
            "profit growth 3years", "3y profit growth", "cagr (profit 3y)", "profit growth of 3 years", "profit growth of 3year",
            "profit growth 5years", "5y profit growth", "cagr (profit 5y)", "profit growth of 5 years","profit growth of 5year",
            "profit growth 7years", "7y profit growth", "cagr (profit 7y)",  "profit growth of 7 years",  "profit growth of 7year", 
            "profit growth 10years", "10y profit growth", "long-term profit growth", "profit growth of 10 years","profit growth of 10year",
            "eps", "earnings per share", "eps (current)",
            "eps last year", "eps (previous year)", "last year eps","earning per share last year",
            "debt", "current debt", "total debt", "outstanding debt",
            "debt 3years back", "debt (3y ago)", "historical debt (3y)", "debt 3 years of back","debt 3year of back","debt 3 years back",
            "debt 5years back", "debt (5y ago)", "historical debt (5y)", "debt 5 years of back","debt 5year of back","debt 5 years back",
            "debt 7years back", "debt (7y ago)", "historical debt (7y)","debt 7 years of back","debt 7year of back","debt 7 years back",
            "debt 10years back", "debt (10y ago)", "historical debt (10y)", "debt 10 years of back","debt 10year of back","debt 10 years back",
            "profit growth", "net profit growth", "earnings growth","sales growth", "revenue growth", "sales increase"
        ]
        
        matching_sheets_company_info_11 = get_typo_tolerant_matches(_company_info_, gemini_response_lower)
        matching_sheets_company_info_ = get_best_field_from_prompt(gemini_response_lower, matching_sheets_company_info_11) 

        
        # 🛠 1. For yearlypnl
        yearly_pnl_ = [
            "profit and loss statement","income statement",
            "net income", "net profit", "profit after tax", "bottom line",
            "yearly net income", "annual net income", "annual profit", "yearly profit after tax",
            "yearly net profit", "annual net profit", "annual earnings", "yearly profit",
            "sales", "turnover", "gross sales", "total sales",
            "expenses", "total expenses", "operating expenses", "costs",
            "operating profit", "ebit", "earnings before interest and taxes", "operating income",
            "other income", "non-operating income", "miscellaneous income",
            "interest", "interest expense", "finance costs", "interest paid",
            "depreciation", "depreciation expense", "amortization",
            "profit before tax", "pbt", "earnings before tax", "pre-tax profit",
            "tax percentage", "effective tax rate", "tax rate",
            "earnings per share", "basic eps",
            "revenue", "total revenue", "gross revenue", "income",
            "financing profit", "net interest income", "financial income",
            "financing margin percentage", "net interest margin", "financial margin",
            "eps", "basic earnings per share", "omp", 
            "operating margin percentage","opm", "operating profit margin", "net margin"
        ]

        # 
        matching_sheets_yearly_pnl11 = get_typo_tolerant_matches(yearly_pnl_, gemini_response_lower)
        matching_sheets_yearly_pnl = get_best_field_from_prompt(gemini_response_lower, matching_sheets_yearly_pnl11)
        # matching_sheets_yearly_pnl  = [sheet for sheet in yearly_pnl_ if sheet in gemini_response_lower]
        
        # 🛠 2. For cashflow
        yearly_cashflow = [
            "cash from operating activities" ," net cash from operations", "operating cash flow","operating activities",
            "cash flow from operations","operating activities","investing activities","financing activities","cash flow",
            "cash from investing activities","net cash used in investing"," investing cash flow","investing activities",
            "cash from financing activities",  "net cash from financing", "financing cash flow","financing activities",
            "net cash flow","net increase/decrease in cash" ," net change in cash",
            "cash flow","cash movements","statement of cash flows","overall cash flow"
        ]
        matching_sheets_cashflow11 = get_typo_tolerant_matches(yearly_cashflow, gemini_response_lower)
        matching_sheets_cashflow = get_best_field_from_prompt(gemini_response_lower, matching_sheets_cashflow11)

        # matching_sheets_cashflow = [sheet for sheet in yearly_cashflow if sheet in gemini_response_lower]

        financial_ratio_ = [
            "financial ratio", "financial ratios", "ratios",
            "ratio date", "date", "reporting date", "data as of", "period end", "fiscal date",
            "inventory days", "days inventory outstanding", "inventory holding period", "inventory turnover days", "doi",
            "days payable", "payable days", "days payables outstanding", "dpo", "average payment period", "creditor days",
            "cash conversion cycle", "ccc", "working capital cycle", "cash cycle", "net operating cycle",
            "working capital days", "net working capital days", "wc days", "working capital cycle",
            "roce percent",  "roce ratio", "operating return", "capital efficiency",
            "roe percent", "roe ratio", "shareholders  return", "equity return", "net worth return"
        ]

        matching_financial_ratio11 = get_typo_tolerant_matches(financial_ratio_, gemini_response_lower)
        matching_financial_ratio = get_best_field_from_prompt(gemini_response_lower, matching_financial_ratio11)


        # 🛠 3. For yearly balance sheet
        yearly_balance_sheet = [
            "balance sheet", "statement of financial position",
            "total assets", "gross assets", "sum of assets",
            "net loans", "net advances", "loans and advances (net)", "net loan portfolio",
            "total liabilities", "aggregate liabilities", "total obligations",
            "equity capital", "shareholders’ equity", "owner’s equity", "paid-up capital", "common equity",
            "reserves", "retained earnings", "surplus reserves", "capital reserves",
            "other liabilities", "miscellaneous liabilities", "sundry liabilities",
            "fixed assets", "property, plant & equipment (PPE)", "tangible assets",
            "cwip", "capital work-in-progress", "assets under construction",
            "investments", "long-term investments", "financial investments",
            "other assets", "miscellaneous assets", "sundry assets",
            "preference capital", "preferred stock", "preference shares"
        ]

        # matching_balance_sheet = [sheet for sheet in yearly_balance_sheet if sheet in gemini_response_lower]
        matching_balance_sheet11 = get_typo_tolerant_matches(yearly_balance_sheet, gemini_response_lower)
        matching_balance_sheet = get_best_field_from_prompt(gemini_response_lower, matching_balance_sheet11)


        yearly_shareholding = [
            "shareholdingpattern","shareholding pattern", "ownership structure", "capital structure", "institutional holding pattern",
            "promoters", "promoter holding", "promoter group", "owner holding", "founders", "controlling shareholders",
            "fiis", "fii holding", "foreign institutional investors", "foreign investors", "overseas shareholders",
            "diis", "dii holding", "domestic institutional investors", "mutual funds", "insurance companies",
            "public", "public holding", "retail investors", "non-institutional investors", "general public",
            "no. of shareholders", "shareholder count", "number of shareholders", "investor base size",
            "others", "others category", "miscellaneous holding", "unidentified shareholders",
            "government", "government holding", "state holding", "public sector holding", "govt stake"
        ]

        matching_yearly_shareholding11 = get_typo_tolerant_matches(yearly_shareholding, gemini_response_lower)
        matching_yearly_shareholding = get_best_field_from_prompt(gemini_response_lower, matching_yearly_shareholding11)


        financial_statement_list = ["financial statement"]
        matching_financial_statement = get_typo_tolerant_matches(financial_statement_list, gemini_response_lower)

        #     matching_balance_sheet = ["net loans"]
    #     cash_flow_debt = ["cash flow to debt"]
    #     get_matches_cash_flow_debt = get_typo_tolerant_matches(cash_flow_debt, gemini_response_lower)
    # elif get_matches_cash_flow_debt:
    #         matching_sheets_cashflow_to_debt = ["cash from operating activities","net loans"]
       
    else:
        
        if "quarter" not in gemini_response_lower and "quarterly" not in gemini_response_lower:
            cash_flow_debt = ["cash flow to debt"]
            get_matches_cash_flow_debt = get_typo_tolerant_matches(cash_flow_debt, gemini_response_lower)

            debt_to_financing_ratio = ["debt to financing ratio"]
            get_matches_debt_to_financing_ratio = get_typo_tolerant_matches(debt_to_financing_ratio, gemini_response_lower)

            operating_cash_flow_to_intrest = ["operating cf to interest", "operating cash flow to interest"]
            get_matches_operating_cash_flow_to_intrest = get_typo_tolerant_matches(operating_cash_flow_to_intrest, gemini_response_lower)
            
            net_cash_flow_margin = ["net cash flow margin"]
            get_matches_net_cash_flow_margin_ = get_typo_tolerant_matches(net_cash_flow_margin, gemini_response_lower)

            fixed_asset_turnover = ["fixed asset turnover" , "fixed asset ratio"]
            get_matches_fixed_asset_turnover_ = get_typo_tolerant_matches(fixed_asset_turnover, gemini_response_lower)

            operating_cf_to_liabilities  = ["operating cf to liabilities" , "operating cash flow to liabilities"]
            get_matches_operating_cf_liabilities = get_typo_tolerant_matches(operating_cf_to_liabilities, gemini_response_lower)
           
            _company_info_ = ["return ratios", "earing per share trends" , "eps trends", "debt trends" , "debt growth"]
            matching_sheets_company_info_ = [comp for comp in _company_info_ if comp in gemini_response_lower]


        else:  
            quarterly_pnl_ = [
                "quarterly performance",
                "profit and loss statement", "income statement","quarterly results", "quarterly pnl","quarter wise results",
                "sales", "turnover", "gross sales", "total sales", "revenue",
                "expenses", "total expenses", "operating expenses", "costs", "outflows",
                "operating_profit", "ebit", "earnings before interest and taxes", "operating income",
                "opm_percentage", "operating margin %", "operating profit margin", "opm %",
                "other income", "non-operating income", "miscellaneous income", "additional income",
                "interest", "interest expense", "finance costs", "interest paid",
                "depreciation", "depreciation expense", "amortization",
                "profit_before_tax", "pbt", "earnings before tax", "pre-tax profit", "ebt",
                "tax_percentage", "effective tax rate", "tax rate",
                "net_profit", "net income", "profit after tax", "bottom line", "earnings",
                "eps_in_rs", "earnings per share", "basic eps",
                "revenue", "total revenue", "gross revenue", "income",
                "financing_profit", "net interest income", "financial income",
                "financing_margin", "net interest margin", "financial margin",
                "gross_npa", "gross non-performing assets", "gross npa ratio",
                "net_npa", "net non-performing assets", "net npa ratio", "non-performing assets"
            ]

            matching_sheets_quarterly_pnl11 = get_typo_tolerant_matches(quarterly_pnl_, gemini_response_lower)
            matching_sheets_quarterly_pnl = get_best_field_from_prompt(gemini_response_lower, matching_sheets_quarterly_pnl11)


            quarterly_shareholding = [
                "shareholdingpattern","shareholding pattern", "ownership structure", "capital structure", "institutional holding pattern",
                "promoters", "promoter holding", "promoter group", "owner holding", "founders", "controlling shareholders",
                "fiis", "fii holding", "foreign institutional investors", "foreign investors", "overseas shareholders",
                "diis", "dii holding", "domestic institutional investors", "mutual funds", "insurance companies",
                "public", "public holding", "retail investors", "non-institutional investors", "general public",
                "no. of shareholders", "shareholder count", "number of shareholders", "investor base size",
                "others", "others category", "miscellaneous holding", "unidentified shareholders",
                "government", "government holding", "state holding", "public sector holding", "govt stake"
            ]

            matching_quarterly_shareholding11 = get_typo_tolerant_matches(quarterly_shareholding, gemini_response_lower)
            matching_quarterly_shareholding = get_best_field_from_prompt(gemini_response_lower, matching_quarterly_shareholding11)


        # ratios_to_check = []
        # matching_financial_ratio = [r for r in ratios_to_check if r in gemini_response_lower]
    
        debtor_to_check = ['roe ratio','roce ratio','debtor days', "receivables days", "days sales outstanding", "dso", "debtor turnover days", "avg collection period"]
        matching_financial_ratio = get_typo_tolerant_matches(debtor_to_check, gemini_response_lower)

    
    tool_calls = []

    # 🧠 Company Info
    if matching_sheets_company_info_ and companies:
        tool_calls.append({
            "tool_name": "company_info_",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": matching_sheets_company_info_
            }
        })

    # 🧠 Yearly PnL (e.g. Net Income)
    if matching_sheets_yearly_pnl and companies:
        tool_calls.append({
            "tool_name": "compare_net_income",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": matching_sheets_yearly_pnl
            }
        })

    # 🧠 Cash Flow
    if matching_sheets_cashflow and companies:
        tool_calls.append({
            "tool_name": "cash_flow",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": matching_sheets_cashflow
            }
        })

    # 🧠 Balance Sheet
    if matching_balance_sheet and companies:
        tool_calls.append({
            "tool_name": "summarize_balance_sheet",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": matching_balance_sheet
            }
        })

    # 🧠 Yearly Shareholding
    if matching_yearly_shareholding and companies:
        tool_calls.append({
            "tool_name": "yearly_shareholding",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": matching_yearly_shareholding
            }
        })

    # 🧠 Financial Ratio
    if matching_financial_ratio and companies:
        tool_calls.append({
            "tool_name": "financial_ratio",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": matching_financial_ratio
            }
        })

    # 🧠 Quarterly Income
    quarter_month = {
        "first": "first", "1st": "first",
        "second": "second", "2nd": "second",
        "third": "third", "3rd": "third",
        "fourth": "fourth", "4th": "fourth",
        "last": "fourth"
    }
    detected_quarters = [v for k, v in quarter_month.items() if k in gemini_response_lower]

    if matching_sheets_quarterly_pnl and companies:
        tool_calls.append({
            "tool_name": "compare_quarterly_income",
            "parameters": {
                "company_names": companies,
                "year": year,
                "quarter_month": detected_quarters,
                "fields": matching_sheets_quarterly_pnl
            }
        })

    # 🧠 Quarterly Shareholding
    if matching_quarterly_shareholding and companies:
        tool_calls.append({
            "tool_name": "quarterly_shareholding",
            "parameters": {
                "company_names": companies,
                "year": year,
                "quarter_month": detected_quarters,
                "fields": matching_quarterly_shareholding
            }
        })

    # 🧠 Financial Statements
    if matching_financial_statement and companies:
        tool_calls.append({
            "tool_name": "three_statements_",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": matching_financial_statement
            }
        })

    # 🧠 Sector-wise Company Comparison
    if sectors_:
        tool_calls.append({
            "tool_name": "sector_wise_company",
            "parameters": {
                "sector": sectors_
            }
        })

    # 🧠 Extra Ratios (custom logic tools)
    if get_matches_cash_flow_debt:
        tool_calls.append({
            "tool_name": "cash_flow_to_debt_",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": ["cash from operating activities", "net loans"]
            }
        })

    if get_matches_debt_to_financing_ratio:
        tool_calls.append({
            "tool_name": "debt_to_financing_ratio_",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": ["net loans", "cash from financing activities"]
            }
        })

    if get_matches_operating_cash_flow_to_intrest:
        tool_calls.append({
            "tool_name": "operating_cf_to_interest_",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": ["cash from operating activities", "interest"]
            }
        })

    if get_matches_net_cash_flow_margin_:
        tool_calls.append({
            "tool_name": "_net_c_f_margin",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": ["net cash flow", "sales"]
            }
        })

    if get_matches_fixed_asset_turnover_:
        tool_calls.append({
            "tool_name": "_fixed_asset_turnover_ratio",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": ["sales", "fixed assets"]
            }
        })

    if get_matches_operating_cf_liabilities:
        tool_calls.append({
            "tool_name": "_operating_cf_to_liablities",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": ["cash from operating activities", "total liabilities"]
            }
        })

    # ✅ Final return
    if tool_calls:
        return tool_calls
    else:
        return {"error": "No matching tools found in prompt."}


    

    
    # 
    # if matching_sheets_company_info_ and companies:
    #     return {
    #         "tool_name": "company_info_",
    #         "parameters": {
    #             "company_names": companies,
    #             "year": year,
    #             "fields": matching_sheets_company_info_
    #         }
    # }

    # elif matching_sheets_yearly_pnl and companies:
    #     return {
    #         "tool_name": "compare_net_income",
    #         "parameters": {
    #             "company_names": companies,
    #             "year": year,
    #             "fields": matching_sheets_yearly_pnl
    #         }
    # }

    # elif matching_sheets_cashflow and companies:

    #     return {
    #         "tool_name": "cash_flow",
    #         "parameters": {
    #             "company_names": companies,
    #             "year": year,
    #             "fields": matching_sheets_cashflow
    #         }
    #     }

    # elif matching_balance_sheet and companies:

    #         if companies:
    #             return {
    #                 "tool_name": "summarize_balance_sheet",
    #                 "parameters": {
    #                     "company_names": companies,
    #                     "year": year,
    #                     "fields" : matching_balance_sheet
    #                 }
    #             }
    # elif matching_yearly_shareholding and companies:

    #         if companies:
    #             return {
    #                 "tool_name": "yearly_shareholding",
    #                 "parameters": {
    #                     "company_names": companies,
    #                     "year": year,
    #                     "fields" : matching_yearly_shareholding
    #                 }
    #             }
    # elif matching_financial_ratio and companies:

    #             return {
    #                 "tool_name": "financial_ratio",
    #                 "parameters": {
    #                     "company_names": companies,
    #                     "year": year,
    #                     "fields" : matching_financial_ratio
    #                 }
    #             }

    # elif matching_sheets_quarterly_pnl and companies:
    #     quarter_month = {
    #         "first": "first",
    #         "1st" : "first",
    #         "second": "second",
    #         "2nd": "second",
    #         "third": "third",
    #         "3rd" : "third",
    #         "fourth": "fourth",
    #         "4th": "fourth",
    #         "last" : "fourth"
    #     }

    #     quarter_get = []
    #     for k, v in quarter_month.items():
    #         if k in gemini_response_lower:
    #             quarter_get.append(v)

    #     return {
    #         "tool_name": "compare_quarterly_income",
    #         "parameters": {
    #             "company_names": companies,
    #             "year": year,
    #             "quarter_month": quarter_get,
    #             "fields": matching_sheets_quarterly_pnl
    #         }
    #     }
    

    # elif matching_quarterly_shareholding and companies:
    #     quarter_month = {
    #         "first": "first",
    #         "1st" : "first",
    #         "second": "second",
    #         "2nd": "second",
    #         "third": "third",
    #         "3rd" : "third",
    #         "fourth": "fourth",
    #         "4th": "fourth",
    #         "last" : "fourth"
    #     }

    #     quarter_get = []
    #     for k, v in quarter_month.items():
    #         if k in gemini_response_lower:
    #             quarter_get.append(v)


    #     return {
    #         "tool_name": "quarterly_shareholding",
    #         "parameters": {
    #             "company_names": companies,
    #             "year": year,
    #             "quarter_month": quarter_get,
    #             "fields": matching_quarterly_shareholding
    #         }
    #     }

    # elif matching_financial_statement and companies:

    #         return {
    #             "tool_name": "three_statements_",
    #             "parameters": {
    #                 "company_names": companies,
    #                 "year": year,
    #                 "fields" : matching_financial_statement
    #             }
    #         }
    
    # elif sectors_:
    #     return {
    #         "tool_name": "sector_wise_company",
    #         "parameters": {
    #             "sector": sectors_
    #         }
    #     }

    # elif matching_sheets_cashflow_to_debt and companies:
    #         return {
    #             "tool_name": "cash_flow_to_debt_",
    #             "parameters": {
    #                 "company_names": companies,
    #                 "year": year,
    #                 "fields" : matching_sheets_cashflow_to_debt
    #             }
    #         }

    # elif matching_sheets_debt_to_financing_ratio and companies:
    #         return {
    #             "tool_name": "debt_to_financing_ratio_",
    #             "parameters": {
    #                 "company_names": companies,
    #                 "year": year,
    #                 "fields" : matching_sheets_debt_to_financing_ratio
    #             }
    #         }

    # elif matching_sheets_operating_cash_flow_to_intrest and companies:
    #         return {
    #             "tool_name": "operating_cf_to_interest_",
    #             "parameters": {
    #                 "company_names": companies,
    #                 "year": year,
    #                 "fields" : matching_sheets_operating_cash_flow_to_intrest
    #             }
    #         }

    # elif matching_sheets_net_cash_flow_margin_ and companies:
    #         return {
    #             "tool_name": "_net_c_f_margin",
    #             "parameters": {
    #                 "company_names": companies,
    #                 "year": year,
    #                 "fields" : matching_sheets_net_cash_flow_margin_
    #             }
    #         }

    # elif matching_sheets_fixed_asset_turnover_ and companies:
    #         return {
    #             "tool_name": "_fixed_asset_turnover_ratio",
    #             "parameters": {
    #                 "company_names": companies,
    #                 "year": year,
    #                 "fields" : matching_sheets_fixed_asset_turnover_
    #             }
    #         }

    # elif matching_sheets_operating_cf_liabilities_ and companies:
    #         return {
    #             "tool_name": "_operating_cf_to_liablities",
    #             "parameters": {
    #                 "company_names": companies,
    #                 "year": year,
    #                 "fields" : matching_sheets_operating_cf_liabilities_
    #             }
    # tool_calls = []

    # if get_matches_cash_flow_debt:
    #     tool_calls.append({
    #         "tool_name": "cash_flow_to_debt_",
    #         "parameters": {
    #             "company_names": companies,
    #             "year": year,
    #             "fields": ["cash from operating activities", "net loans"]
    #         }
    #     })

    # if get_matches_debt_to_financing_ratio:
    #     tool_calls.append({
    #         "tool_name": "debt_to_financing_ratio_",
    #         "parameters": {
    #             "company_names": companies,
    #             "year": year,
    #             "fields": ["net loans", "cash from financing activities"]
    #         }
    #     })

    # if get_matches_operating_cash_flow_to_intrest:
    #     tool_calls.append({
    #         "tool_name": "operating_cf_to_interest_",
    #         "parameters": {
    #             "company_names": companies,
    #             "year": year,
    #             "fields": ["cash from operating activities", "interest"]
    #         }
    #     })

    # if get_matches_net_cash_flow_margin_:
    #     tool_calls.append({
    #         "tool_name": "_net_c_f_margin",
    #         "parameters": {
    #             "company_names": companies,
    #             "year": year,
    #             "fields": ["net cash flow", "sales"]
    #         }
    #     })

    # if get_matches_fixed_asset_turnover_:
    #     tool_calls.append({
    #         "tool_name": "_fixed_asset_turnover_ratio",
    #         "parameters": {
    #             "company_names": companies,
    #             "year": year,
    #             "fields": ["sales", "fixed assets"]
    #         }
    #     })

    # if get_matches_operating_cf_liabilities:
    #     tool_calls.append({
    #         "tool_name": "_operating_cf_to_liablities",
    #         "parameters": {
    #             "company_names": companies,
    #             "year": year,
    #             "fields": ["cash from operating activities", "total liabilities"]
    #         }
    #     })

    # Return all matched tools
    # if tool_calls:
    #     return tool_calls
    # else:
    #     return {"error": "No matching tools found in prompt."}


    # # 🛑 If nothing matched
    # return {
    #     "tool_name": None,
    #     "parameters": {}
    # }


# {'comparison': {'3i Infotech Ltd': {'2022': {'fixed asset turnover': 1.624}}}, 'year': '2022'}
# {'comparison': {'3i Infotech Ltd': {'2022': {'Operating CF to liabilities': '-5.21%'}}}, 'year': '2022'}


# "\n\n[Context based on tool result]\nComparison of fixed asset turnover :\n\n3i Infotech Ltd:\n  2022: {'fixed asset turnover': 1.624}"

