import pandas as pd

def three_statements_df(data):
    income_statement = {}
    cash_flow_statement = {}
    balance_sheet = {}

    # Categorize each section of the data
    for section in data:
        comparison = section.get("comparison", {})
        for company, year_data in comparison.items():
            for date_key, content in year_data.items():
                financials = content.get("financial statement", {})
                if "sales" in financials:
                    income_statement.update(financials)
                elif "cash from operating activities" in financials:
                    cash_flow_statement.update(financials)
                elif "total assets" in financials:
                    balance_sheet.update(financials)

    # Convert dict to DataFrame with index reset
    def dict_to_df(d):
        df = pd.DataFrame(d.items(), columns=["Financial Statement", "Value"])
        df["Value"] = df["Value"].astype(str)
        return df


    df_income = dict_to_df(income_statement)
    df_cash = dict_to_df(cash_flow_statement)
    df_balance = dict_to_df(balance_sheet)

    return df_income, df_cash, df_balance



def flatten_all_financials(tool_result_data_):
    results = []

    for tool_result in tool_result_data_:
        comparison_data = tool_result.get("comparison", {})
        
        for company, section_data in comparison_data.items():
            for section_name, content in section_data.items():
                
                # Case 1: Handle quarterly performance (nested periods)
                if section_name == "quarterly performance" and isinstance(content, dict):
                    for period, metrics in content.items():
                        for field, value in metrics.items():
                            results.append({
                                "Company": company,
                                "Period": period,  # like "2023-03-01 Q1"
                                "Field": field,
                                "Value": value
                            })

                # Case 2: Handle generic sections (flat structure)
                elif isinstance(content, dict):
                    for field, value in content.items():
                        results.append({
                            "Company": company,
                            "Period": section_name,  # like "2022" or "net profit"
                            "Field": field,
                            "Value": value
                        })

    # Create DataFrame
    df = pd.DataFrame(results)

    # Convert values to string (optional; only if values are mixed types)
    df["Value"] = df["Value"].astype(str)

    return df

