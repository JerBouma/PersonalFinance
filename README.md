# Personal Finance
The purpose of this application to easily track your personal finance by giving the script a set of keywords.
As daily life usually has quite a lot of similar transactions (groceries, shopping, eating out etc.)
you can create a complete overview of your spending pattern rather quickly.

![](images/SpreadsheetImageExample.PNG)

## Set-Up / Installation
1. Copy the spreadsheet template you can find [here](
https://docs.google.com/spreadsheets/d/183sUTSwVHJ600WKz7DN-OzPW8FxVmDkVkNy6M_GFZsQ/edit?usp=sharing).
2. Connect a Spreadsheet to gspread, follow [this guide](
https://towardsdatascience.com/accessing-google-spreadsheet-data-using-python-90a5bc214fd2) until "Reading
spreadsheet data with Python". Don't forget to also include the Google Sheets API which is not mentioned in
the article.
3. Clone this repository.
4. Run `pip install -e .` in this repository, this will install it as CLI tool.
5. Configure `config.yaml` to your needs. For example:
    ```yaml
    spreadsheet_name: Finances
    input_sheet: Input
    bank_data_sheet: Bank Data
    client_secret_file: ./client_secret.json
    ```
    If you use my template, these are already correct if you change the name of the spreadsheet to "Finances".
6. Don't forget to add the "client_secret.json" file to the same folder.
7. Download your transaction data as CSV (for example: *NLXXINGBXXXXXXXXXX_01-01-2011_02-07-2020.csv*)
    - Currently the only working bank is [ING](https://www.ing.nl/). If you want to make it work with your bank,
    please send me a file with the format your bank uses so I can include it as an option.
8. Run **personal_finance** in your terminal and checkout the result.
