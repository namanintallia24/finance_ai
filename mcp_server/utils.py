import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data")


def get_csv_path(company_name: str, statement_type: str) -> str:
    """
    Constructs the path to the CSV file based on company name and statement type.
    """
    return os.path.join(DATA_PATH, f"{company_name.lower()}_{statement_type}.csv")

def file_exists(company_name: str, statement_type: str) -> bool:
    """
    Checks if the specified file exists.
    """
    return os.path.exists(get_csv_path(company_name, statement_type))

def load_financial_csv(company_name: str, statement_type: str) -> pd.DataFrame:
    """
    Loads the CSV as a pandas DataFrame.
    """
    path = get_csv_path(company_name, statement_type)
    return pd.read_csv(path)

def get_row_by_label(df: pd.DataFrame, label: str):
    """
    Returns the row that matches the given label in the 'Year' column.
    """
    match = df[df["Year"] == label]
    if match.empty:
        return None
    return match.iloc[0]
