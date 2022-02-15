from dataclasses import dataclass
import textwrap
from typing import Optional, TypeVar
import pandas as pd
import numpy as np
from tqdm import tqdm
import yaml
import gspread
import gspread_dataframe as gd
from oauth2client.service_account import ServiceAccountCredentials


CONFIG_FILE = "./config.yaml"

@dataclass
class Config:
    spreadsheet_name: str = "Finances"
    input_sheet: str = "Input"
    bank_data_sheet: str = "Bank Data"
    client_secret_file: str = "./client_secret.json"
    csv_config_file: str = "./csv_configs/ing.yaml"


@dataclass
class CsvConfig:
    date_col: str
    date_format: str
    amount_col: str
    amount_decimal_separator: str
    debit_credit_col: Optional[str]
    debit: Optional[str]
    credit: Optional[str]
    name_description_col: str
    notification_col: str


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
    csv_config = data_from_yaml(config.csv_config_file, CsvConfig)

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
    DEFAULT_CSV_FILE_LOCATION = "input.csv"
    bank_file = input(f"CSV File Location [{DEFAULT_CSV_FILE_LOCATION}]: ") or DEFAULT_CSV_FILE_LOCATION

    print("\nParsing your data and assigning categories...\n")

    # Create Client
    spreadsheet = initialize_spreadsheet(config.client_secret_file, config.spreadsheet_name)

    # Load Bank File (.csv) & Input from Spreadsheet
    bank_data = load_bank_file(bank_file, csv_config)
    bank_input = load_personal_input(spreadsheet, config.input_sheet)

    # Perform Category assignment
    bank_data_selected = category_selector(bank_data, bank_input, csv_config)

    # Write to the Spreadsheet
    write_to_spreadsheet(bank_data_selected, spreadsheet, config.bank_data_sheet)

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
    df = pd.read_csv(file)

    df[csv_config.amount_col] = df[csv_config.amount_col].apply(
        lambda x: x.replace(csv_config.amount_decimal_separator, ".")
    )
    df[csv_config.amount_col] = pd.to_numeric(df[csv_config.amount_col])

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
    df = df.set_index(date)
    # Only return df with relevant columns
    columns = [csv_config.name_description_col, csv_config.amount_col, csv_config.notification_col]
    return df[columns]


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
                    if item.lower() in value[csv_config.notification_col].lower():
                        category_decision = category
                        continue
                    elif item.lower() in value[csv_config.name_description_col].lower():
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



