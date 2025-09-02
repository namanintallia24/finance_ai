# def prepare_chart_data(tool_result_data_list):
#     """
#     Convert list of dict financial data into Chart.js format dynamically.

#     Example input:
#     [
#         {
#             "comparison": {
#                 "3i Infotech Ltd": {
#                     "2020-03-31": {"net income": 68.0, "sales": 698.0}
#                 }
#             },
#             "year": "2020"
#         },
#         {
#             "comparison": {
#                 "TCS": {
#                     "2020-03-31": {"net income": 63.0, "sales": 28.0}
#                 }
#             },
#             "year": "2020"
#         }
#     ]

#     Output:
#     {
#         "labels": ["2020-03-31"],
#         "datasets": [
#             {"label": "3i Infotech Ltd - net income", "data": [68.0]},
#             {"label": "3i Infotech Ltd - sales", "data": [698.0]},
#             {"label": "TCS - net income", "data": [63.0]},
#             {"label": "TCS - sales", "data": [28.0]}
#         ]
#     }
#     """
#     chart_data = {"labels": [], "datasets": []}
#     datasets_map = {}  # store dataset dynamically

#     for item in tool_result_data_list:
#         comparison = item.get("comparison", {})
#         for company, years_data in comparison.items():
#             for year, metrics in years_data.items():
#                 # ensure year/label is added
#                 if year not in chart_data["labels"]:
#                     chart_data["labels"].append(year)

#                 # iterate over dynamic financial metrics
#                 for metric, value in metrics.items():
#                     dataset_key = f"{company} - {metric}"

#                     if dataset_key not in datasets_map:
#                         datasets_map[dataset_key] = {
#                             "label": dataset_key,
#                             "data": []
#                         }

#                     # maintain alignment with labels
#                     while len(datasets_map[dataset_key]["data"]) < chart_data["labels"].index(year):
#                         datasets_map[dataset_key]["data"].append(None)

#                     datasets_map[dataset_key]["data"].append(value)

#     # Normalize missing values for datasets
#     label_count = len(chart_data["labels"])
#     for dataset in datasets_map.values():
#         while len(dataset["data"]) < label_count:
#             dataset["data"].append(None)

#     chart_data["datasets"] = list(datasets_map.values())
#     return chart_data


# import pandas as pd

# def prepare_chart_data(tool_result_data_list):
#     chart_data_list = []

#     for sector_data in tool_result_data_list:
#         comparison = sector_data.get("comparison", {})
#         year = sector_data.get("year", "")

#         records = []

#         # --- Case 1: comparison has SECTORS -> list of dicts
#         if all(isinstance(v, list) for v in comparison.values()):
#             for sector, companies in comparison.items():
#                 for company in companies:
#                     row = {"Company": company.get("Company", ""),
#                            "Year": company.get("Year", year)}
#                     row.update({k: v for k, v in company.items() if k not in ["Company", "Year"]})
#                     records.append(row)

#         # --- Case 2: comparison has COMPANIES -> nested dicts
#         elif all(isinstance(v, dict) for v in comparison.values()):
#             for company_name, yearly_data in comparison.items():
#                 for date_str, metrics in yearly_data.items():
#                     row = {"Company": company_name, "Date": date_str, "Year": year}
#                     row.update(metrics)
#                     records.append(row)

#         df = pd.DataFrame(records)
#         if df.empty:
#             continue

#         df = df.fillna(0)

#         # Pick numeric columns only (financial metrics)
#         numeric_cols = df.select_dtypes(include="number").columns

#         for col in numeric_cols:
#             chart_data_list.append({
#                 "title": f"{col.capitalize()} Comparison ({year})",
#                 "labels": df["Company"].tolist(),
#                 "datasets": [
#                     {
#                         "label": col.capitalize(),
#                         "data": df[col].astype(float).round(2).tolist(),
#                         "backgroundColor": "rgba(54, 162, 235, 0.6)",
#                     }
#                 ]
#             })

#     return chart_data_list





# import pandas as pd

# def prepare_chart_data(tool_result_data_list):
#     chart_data_list = []

#     for sector_data in tool_result_data_list:
#         comparison = sector_data.get("comparison", {})
#         year = sector_data.get("year", "")

#         records = []

#         # --- Case 1: comparison has SECTORS -> list of dicts
#         if all(isinstance(v, list) for v in comparison.values()):
#             for sector, companies in comparison.items():
#                 for company in companies:
#                     row = {"Company": company.get("Company", ""),
#                            "Year": company.get("Year", year)}
#                     row.update({k: v for k, v in company.items() if k not in ["Company", "Year"]})
#                     records.append(row)

#         # --- Case 2: comparison has COMPANIES -> nested dicts
#         elif all(isinstance(v, dict) for v in comparison.values()):
#             for company_name, yearly_data in comparison.items():
#                 for date_str, metrics in yearly_data.items():
#                     # Case 2a: metrics is already flat dict (✅ existing logic)
#                     if isinstance(metrics, dict) and all(isinstance(val, (int, float, str, type(None))) for val in metrics.values()):
#                         row = {"Company": company_name, "Date": date_str, "Year": year}
#                         row.update(metrics)
#                         records.append(row)

#                     # Case 2b: metrics is nested (like {"balance sheet": {...}})
#                     elif isinstance(metrics, dict):
#                         for section_name, section_metrics in metrics.items():
#                             if isinstance(section_metrics, dict):
#                                 row = {"Company": company_name,
#                                        "Date": date_str,
#                                        "Year": year,
#                                        "Section": section_name}
#                                 row.update(section_metrics)
#                                 records.append(row)

#         df = pd.DataFrame(records)
#         if df.empty:
#             continue

#         df = df.fillna(0)

#         # Pick numeric columns only (financial metrics)
#         numeric_cols = df.select_dtypes(include="number").columns

#         for col in numeric_cols:
#             chart_data_list.append({
#                 "title": f"{col.capitalize()} Comparison ({year})",
#                 "labels": df["Company"].tolist(),
#                 "datasets": [
#                     {
#                         "label": col.capitalize(),
#                         "data": df[col].astype(float).round(2).tolist(),
#                         "backgroundColor": "rgba(54, 162, 235, 0.6)",
#                     }
#                 ]
#             })

#     return chart_data_list



import pandas as pd

def prepare_chart_data(tool_result_data_list):
    chart_data_list = []

    for sector_data in tool_result_data_list:
        comparison = sector_data.get("comparison", {})
        year = sector_data.get("year", "")

        records = []

        # --- Case 1: comparison has SECTORS -> list of dicts
        if all(isinstance(v, list) for v in comparison.values()):
            for sector, companies in comparison.items():
                for company in companies:
                    row = {
                        "Company": company.get("Company", ""),
                        "Year": company.get("Year", year)
                    }
                    row.update({
                        k: _clean_numeric(v)
                        for k, v in company.items()
                        if k not in ["Company", "Year"]
                    })
                    records.append(row)

        # --- Case 2: comparison has COMPANIES -> nested dicts
        elif all(isinstance(v, dict) for v in comparison.values()):
            for company_name, yearly_data in comparison.items():
                for date_str, metrics in yearly_data.items():

                    # Case 2a: metrics is already flat dict
                    if isinstance(metrics, dict) and all(isinstance(val, (int, float, str, type(None))) for val in metrics.values()):
                        row = {
                            "Company": company_name,
                            "Date": date_str,
                            "Year": year
                        }
                        row.update({k: _clean_numeric(v) for k, v in metrics.items()})
                        records.append(row)

                    # Case 2b: metrics is nested dict (like {"balance sheet": {...}})
                    elif isinstance(metrics, dict):
                        for section_name, section_metrics in metrics.items():
                            if isinstance(section_metrics, dict):
                                row = {
                                    "Company": company_name,
                                    "Date": date_str,
                                    "Year": year,
                                    "Section": section_name
                                }
                                row.update({k: _clean_numeric(v) for k, v in section_metrics.items()})
                                records.append(row)

        # Convert records → DataFrame
        df = pd.DataFrame(records)
        if df.empty:
            continue

        df = df.fillna(0)

        # Pick numeric columns only (financial metrics)
        numeric_cols = df.select_dtypes(include="number").columns

        for col in numeric_cols:
            chart_data_list.append({
                "title": f"{col.capitalize()} Comparison ({year})",
                "labels": df["Company"].tolist(),
                "datasets": [
                    {
                        "label": col.capitalize(),
                        "data": df[col].astype(float).round(2).tolist(),
                        "backgroundColor": "rgba(54, 162, 235, 0.6)",
                    }
                ]
            })

    return chart_data_list


# ----------------------
# Helper to clean numeric strings
# ----------------------
def _clean_numeric(value):
    """
    Convert strings like '123', '123.45', '-99%', '100%' into floats.
    Leave others unchanged.
    """
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        # Handle percentages
        if value.endswith("%"):
            try:
                return float(value.strip("%"))
            except ValueError:
                return None
        # Handle plain numeric strings
        try:
            return float(value)
        except ValueError:
            return value
    return value
