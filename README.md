![](Images/PersonalFinancePNG.png)

# Personal Finance
The purpose of this application to easily track your financials by giving the program a set of keywords.
. As daily life usually has quite a lot of similar transactions (groceries, shopping, eating out etc.)
you can create a complete overview of your spending patern rather quickly.

The program creates the following:
- All transactions per year
    - If you include your transactions from the past 10 years, you will get a total of 10 files.
    - Each file includes the tabs 1 till 12 (for each month)
- All transactions split by category
    - Comes in handy when you want to check if transactions are recorded correctly.
    - The "Other" tab collects all transactions the program failed to assign a category to.
- A complete overview for each year and month
    - this sheet can be altered by yourself as the program does not overwrite any
    changes you make to the file. Therefore you can include averages and such
    
## Set-Up / Installation
1. Download the input sheet from the "templates" folder and fill it in
    - The sheet names (tabs) are the categories which you alter yourself
    - The grey area is the space for inputting keywords
    - **Note:** the first sheet is _always_ excluded from the total overview. This is so you can filter out
    transactions that are merely moving money around between your own accounts.
2. Download your transaction data.
    - Currently the only working bank is [ING](https://www.ing.nl/). If you want to make it work with your bank,
    please send me a file with the format your bank uses so I can include it as an option.
3. Run the program and observe the different files it creates. By looking at the categories assigned to each transaction
you can make changes to the input file until you are satisfied with the result.
4. Make adjustments to the Complete Overview file however you like.

## Contribution
If you wish to make this work for your bank, you can contribute by showing me
formats of your (or other) bank(s) so I can include then. 

If you wish to test the packaging, you can do so by:
- Clone/Download this repository.
- Open CMD/PowerShell/Terminal in folder.
- Install dependencies: ``pip install -r requirements.txt``
- Run the command: ``python program.py``

### Build
Installation:

- Windows:
    - ``pyinstaller --add-data="images;images" --icon=images\iconICO.ico --name=ThePassiveInvestor program.py``
- MacOS/Linux:
    - ``pyinstaller --add-data="images:images" --icon=images/iconICO.ico --name=ThePassiveInvestor
    --windowed program.py``

Open the 'dist' folder and the 'ThePassiveInvestor' folder, run exe/app. Or:

- Windows:
    - CMD:
        - ``start dist\ThePassiveInvestor\ThePassiveInvestor.exe``
    - PowerShell:
        - ``dist\ThePassiveInvestor\ThePassiveInvestor.exe``
- MacOS
    - ``open dist/ThePassiveInvestor.app``