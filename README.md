# Personal Finance
The purpose of this application to easily track your personal finance by giving the script a set of keywords.
As daily life usually has quite a lot of similar transactions (groceries, shopping, eating out etc.)
you can create a complete overview of your spending pattern rather quickly.

![](images/SpreadsheetImageExample.PNG)

## Set-Up / Installation
1. Copy the spreadsheet template you can find [here](
https://docs.google.com/spreadsheets/d/183sUTSwVHJ600WKz7DN-OzPW8FxVmDkVkNy6M_GFZsQ/edit?usp=sharing).
2. Connect a Spreadsheet to gspread, follow "For Bots: Using Service Account" until step 6 from [this guide](
https://docs.gspread.org/en/latest/oauth2.html#for-bots-using-service-account).
3. Clone this repository.
4. Run `pip install -e .` in this repository, this will install it as CLI tool.
5. Configure `config.yaml` to your needs. By default this is set to:
    ```yaml
    spreadsheet_name: Finances
    input_sheet: Input
    bank_data_sheet: Bank Data
    client_secret_file: client_secret.json
    ```
    If you use my template, these are already correct if you change the name of the spreadsheet to "Finances".
6. Don't forget to add the "client_secret.json" file to the same folder.
7. Download your transaction data as CSV (for example: *NLXXINGBXXXXXXXXXX_01-01-2011_02-07-2020.csv*)
    - Currently the only working banks are [ING](https://www.ing.nl/) and [ASN](https://www.asnbank.nl/). If you want to make it work with your bank, please send me a file with the format your bank uses so I can include it as an option.
8. Run **personal_finance** in your terminal and checkout the result.

## Creating a new CSV Config
Based on the `CsvConfig` dataclass in `__main__.py` you can create a new CSV config for a different bank. Add it to the `csv_configs` directory and select it when running the program. Examples and default configs can be found in this folder already.