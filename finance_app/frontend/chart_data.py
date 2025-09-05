import math
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



def sanitize_for_json(obj):
    """
    Recursively walk through lists/dicts and replace NaN/inf with None.
    Ensures valid JSON for Postgres JSONField.
    """
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj


