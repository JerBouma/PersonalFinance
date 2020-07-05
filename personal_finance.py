import pandas as pd
import numpy as np
from tqdm import tqdm
import gspread
import gspread_dataframe as gd
from oauth2client.service_account import ServiceAccountCredentials


def personal_finance(spreadsheet_name="Finances", input_sheet="Input", bank_data_sheet="Bank Data",
                     client_secret="client_secret.json"):
    """
    Description
    ----
    Performs all functions to fully load in your bank data and write it out with categories assigned.

    Input
    ----
    spreadsheet_name (string)
        Name of the spreadsheet
    input_sheet (string)
        Name of the input sheet inside the spreadsheet
    bank_data_sheet (string)
        Name of the bank data sheet inside the spreadsheet
    client_secret (string)
        Client secret from your Google API used to access the spreadsheet

    Output
    ----
    Returns no variable but loads data, assigns categories and writes to the spreadsheet
    """
    print("\033[1m" + "Welcome to the Personal Finance tool" + "\033[0m")
    print("-------------------------------------")
    print("This tool currently only works for ING bank.")
    print('')
    print("To use this program please follow the following steps:")
    print("1. Connect gspread to the spreadsheet, fill tab " + input_sheet + " with your category filters")
    print("and create the tab " + bank_data_sheet)
    print("2. Download your transactions history as CSV file when logging into your account on ING")
    print("3. Enter the CSV file (+ location) from ING below and press ENTER")
    print('')
    bank_file = input("File: ")
    print('')
    print("Parsing your data and assigning categories..")
    print('')

    # Create Client
    spreadsheet = initialize_spreadsheet(client_secret, spreadsheet_name)

    # Load Bank File (.csv) & Input from Spreadsheet
    bank_data = load_bank_file(bank_file)
    bank_input = load_personal_input(spreadsheet, input_sheet)

    # Perform Category assignment
    bank_data_selected = category_selector(bank_data, bank_input)

    # Write to the Spreadsheet
    write_to_spreadsheet(bank_data_selected, spreadsheet, bank_data_sheet)

    print('')
    print("Done! Find the data in the spreadsheet " + spreadsheet_name
          + " on the tab " + bank_data_sheet)
    print('')


def initialize_spreadsheet(client_secret="client_secret.json", spreadsheet='Financien'):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(client_secret, scope)
    client = gspread.authorize(credentials)

    spreadsheet = client.open(spreadsheet)

    return spreadsheet


def load_bank_file(file):
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
    data = pd.read_csv(file)

    debit_credit = data.columns[5]
    amount = data.columns[6]

    year = data['Datum'].astype(str).str[:4]
    month = data['Datum'].astype(str).str[4:6]
    day = data['Datum'].astype(str).str[6:]
    date = pd.to_datetime(year + "-" + month + "-" + day).dt.date

    data[amount] = data[amount].apply(
        lambda x: x.replace(',', '.'))
    data[amount] = pd.to_numeric(data[amount])
    values = []

    for row, value in data.iterrows():
        if value[debit_credit] in ('Debit', 'Af'):
            values.append(-value[amount])
        elif value[debit_credit] in ('Credit', 'Bij'):
            values.append(value[amount])

    data[amount] = values

    data = data.set_index(date)
    data = data.drop(
        [data.columns[0], data.columns[2],
         data.columns[3], data.columns[4],
         data.columns[5], data.columns[7]], axis=1)

    return data


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
    input_data = input_data.replace('', np.nan)

    return input_data


def category_selector(bank_data, input_data):
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
    notifications = bank_data.columns[2]
    description = bank_data.columns[0]

    for row, value in tqdm(bank_data.iterrows(), total=bank_data.shape[0]):
        category_decision = "Other"
        for category in input_data.columns:
            if category_decision == "Other":
                for item in input_data[category].dropna():
                    if item.lower() in value[notifications].lower():
                        category_decision = category
                        continue
                    elif item.lower() in value[description].lower():
                        category_decision = category
                        continue
        categories.append(category_decision)

    bank_data["Categories"] = categories

    return bank_data


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
    personal_finance()



