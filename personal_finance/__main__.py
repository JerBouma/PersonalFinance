from dataclasses import dataclass
from pathlib import Path
import textwrap
from typing import List, Literal, TypeVar
import pandas as pd
import numpy as np
from tqdm import tqdm
import yaml
import gspread
import gspread_dataframe as gd
from oauth2client.service_account import ServiceAccountCredentials


CONFIG_FILE = Path("./config.yaml")
CSV_CONFIG_LOCATION = Path("./csv_configs/")
DEFAULT_CSV_FILE_LOCATION = Path("input.csv")
DEFAULT_CSV_CONFIG_FILE = Path("ing.yaml")

@dataclass
class Config:
    spreadsheet_name: str = "Finances"
    input_sheet: str = "Input"
    bank_data_sheet: str = "Bank Data"
    client_secret_file: str = "./client_secret.json"


@dataclass
class CsvConfig:
    # Column for transaction date
    date_col: str
    # Format in which the date is provided, uses strftime format codes:
    # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    date_format: str
    # Column for transaction amount
    amount_col: str
    # Transaction amount delimiter for decimal values
    amount_decimal_delimiter: Literal[",", "."]
    # Column for name/description of transaction
    name_description_col: str
    # Column with description/notification of transaction
    notification_col: str
    # Column which defines whether it's a credit or debit transaction
    # Leave empty if CSV already provides a negative amount for a debit transaction
    debit_credit_col: str = None
    # The value in the debit_credit_col which defines a debit transaction
    debit: str = None
    # The value in the debit_credit_col which defines a credit transaction
    credit: str = None
    # Delimiter of the CSV file itself
    delimiter: str = ","
    # Optional custom column names if the CSV has no header row
    columns_names: List[str] = None


def personal_finance():
    """
    Description
    ----
    Performs all functions to fully load in your bank data and write it out with categories assigned.

    Requires a YAML CONFIG_FILE to be set with the contents as defined in the Config dataclass.

    Output
    ----
    Returns no variable but loads data, assigns categories and writes to the spreadsheet
    """
    config = data_from_yaml(CONFIG_FILE, Config)

    print(
        textwrap.dedent(f"""
            \033[1m
            Welcome to the Personal Finance tool
            \033[0m
            -------------------------------------
            This tool currently only works for ING bank.

            To use this program please follow the following steps:
            1. Connect gspread to the spreadsheet, fill tab {config.input_sheet} with your category filters
            and create the tab {config.bank_data_sheet}.
            2. Download your transactions history as CSV file when logging into your account on ING
            3. Enter the CSV file (location) from ING below and press ENTER
        """)
    )
    bank_file = Path(input(f"CSV File Location [{DEFAULT_CSV_FILE_LOCATION}]: ") or DEFAULT_CSV_FILE_LOCATION)
    csv_config_file = Path(input(f"CSV config file [{DEFAULT_CSV_CONFIG_FILE}]: ") or DEFAULT_CSV_CONFIG_FILE)

    csv_config = data_from_yaml(CSV_CONFIG_LOCATION / csv_config_file, CsvConfig)

    print("\nParsing your data and assigning categories...\n")

    # Create Client
    spreadsheet = initialize_spreadsheet(config.client_secret_file, config.spreadsheet_name)

    # Load Bank File (.csv) & Input from Spreadsheet
    bank_data = load_bank_file(bank_file, csv_config)
    bank_input = load_personal_input(spreadsheet, config.input_sheet)

    # Perform Category assignment
    bank_data_selected = category_selector(bank_data, bank_input, csv_config)

    # Write to the Spreadsheet
    columns = [csv_config.name_description_col, csv_config.amount_col, csv_config.notification_col]
    write_to_spreadsheet(bank_data_selected[columns], spreadsheet, config.bank_data_sheet)

    print(f"\nDone! Find the data in the spreadsheet {config.spreadsheet_name} on the tab {config.bank_data_sheet}!")
    return


T = TypeVar("T")
def data_from_yaml(file: str, dataclass_: T) -> T:
    """Read the config file from the given location in YAML."""
    try:
        with open(file, "r") as f:
            return dataclass_(**yaml.safe_load(f))
    except yaml.YAMLError as e:
        print(e)
        exit()
    except FileNotFoundError as e:
        print("No config file found at {config_file}, using defaults.")
        pass
    return dataclass_()


def initialize_spreadsheet(client_secret: str, spreadsheet: gspread.Spreadsheet):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(client_secret, scope)
    client = gspread.authorize(credentials)
    return client.open(spreadsheet)


def load_bank_file(file: str, csv_config: CsvConfig) -> pd.DataFrame:
    """
    Description
    ----
    Loads the CSV file found by logging into ING.com and downloading your data. This can be up to
    10 years in the past. See for more information here: https://www.ing.nl/particulier/mobiel-en-
    internetbankieren/internetbankieren/digitale-afschiften/papierloos-bankieren/index.html

    Input
    ----
    file (string)
        The bank file.

    Output
    ----
    data (DataFrame)
        All bank data neatly converted to a DataFrame to be used by the program.
    """
    df = pd.read_csv(file, delimiter=csv_config.delimiter, names=csv_config.columns_names)

    df[csv_config.amount_col] = (
        df[csv_config.amount_col].astype(str).str.replace(csv_config.amount_decimal_delimiter, ".", regex=False)
    )
    df[csv_config.amount_col] = pd.to_numeric(df[csv_config.amount_col], errors='coerce')

    if csv_config.debit_credit_col:
        values = []
        for _, value in df.iterrows():
            if value[csv_config.debit_credit_col] == csv_config.debit:
                values.append(-value[csv_config.amount_col])
            elif value[csv_config.debit_credit_col] == csv_config.credit:
                values.append(value[csv_config.amount_col])
        df[csv_config.amount_col] = values

    # Parse date column
    date = pd.to_datetime(df[csv_config.date_col], format=csv_config.date_format)
    return df.set_index(date)


def load_personal_input(spreadsheet, sheet):
    """
    Description
    ----
    Loading personal input. Requires connection to a Google Spreadsheet and the correct Input format.
    This refers to putting the category titles at the top and placing the keywords beneath each category.

    Thus you would get:
    Header: "Groceries"
    Row2: "supermarket"
    Row3: "amazon"
    etc.

    Input
    ----
    spreadsheet (string)
        Your spreadsheet that you linked the Google Drive API and Google Sheets API to.
    sheet (string)
        The specific sheet you wish to load the input from.

    Output
    ----
    input_data (DataFrame)
        All input data neatly converted to a DataFrame to be used by the program.
    """
    sheet = spreadsheet.worksheet(sheet)
    input_data = pd.DataFrame(sheet.get_all_records())
    return input_data.replace('', np.nan)


def category_selector(bank_data: pd.DataFrame, input_data: pd.DataFrame, csv_config: CsvConfig) -> pd.DataFrame:
    """
    Description
    ----
    The algorithm that determines what category should be assigned based on bank data and input data.

    Input
    ----
    bank_data (DataFrame)
        DataFrame created by load_bank_file()
    input_data (DataFrame)
        DataFrame created by load_personal_input()

    Output
    ----
    bank_data (DataFrame)
        Returns the bank data with an extra column, "Category".
    """
    categories = []
    # Make sure we don't modify the input
    new_bank_data = bank_data.copy()

    for _, value in tqdm(new_bank_data.iterrows(), total=new_bank_data.shape[0]):
        category_decision = "Other"
        for category in input_data.columns:
            if category_decision == "Other":
                for item in input_data[category].dropna():
                    if item.lower() in str(value[csv_config.notification_col]).lower():
                        category_decision = category
                        continue
                    elif item.lower() in str(value[csv_config.name_description_col]).lower():
                        category_decision = category
                        continue
        categories.append(category_decision)

    new_bank_data["Categories"] = categories

    return new_bank_data


def write_to_spreadsheet(bank_data, spreadsheet, sheet):
    """
    Description
    ----
    Writes all data to the spreadsheet and sheet of your choice.

    Input
    ----
    bank_data (DataFrame)
        DataFrame created by load_bank_file() or category_selector()
    spreadsheet (string)
        The specific spreadsheet
    sheet (string)
        The sheet
    Output
    ----
    Writes the data to the spreadsheet. No variable outputted.
    """
    sheet = spreadsheet.worksheet(sheet)
    gd.set_with_dataframe(sheet, bank_data, include_index=True)


if __name__ == "__main__":
    try:
        personal_finance()
    except KeyboardInterrupt as e:
        print("\nCancelled by CTRL + C.")



