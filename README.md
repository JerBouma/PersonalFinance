![FinancePortfolio](https://github.com/JerBouma/FinancePortfolio/assets/46355364/d3560ff3-1d2a-4ba2-a99d-dcf7b6ec2c5c)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor_this_Project-grey?logo=github)](https://github.com/sponsors/JerBouma)
[![Documentation](https://img.shields.io/badge/Documentation-grey?logo=readme)](https://www.jeroenbouma.com/projects/FinancePortfolio)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/FinancePortfolio)](https://pypi.org/project/FinancePortfolio/)
[![PYPI Version](https://img.shields.io/pypi/v/FinancePortfolio)](https://pypi.org/project/FinancePortfolio/)
[![PYPI Downloads](https://static.pepy.tech/badge/FinanceToolkit/month)](https://pepy.tech/project/FinancePortfolio)

Tracking your investment portfolio and personal finances can be tedious. It either requires proprietary software to be used that often have limited features until you pay for a subscription or/and it requires a great amount of manual input just to get the overview you are looking for. And even once you have this overview, it is often not in the format you desire, does not apply the categorization as you wish or is simply not accurate in the first place.

**I want to give you back the control to properly and efficiently track your finances with the FinancePortfolio**. Through the usage of configuration files, it becomes possible to connect multiple brokers as you desire and have the FinancePortfolio do the heavy lifting for you. It will automatically obtain historical data for all instruments in your portfolio, calculate the returns, benchmark returns, alpha and weight of each instrument and (optionally) provide you with a neat looking Excel file that you can further customize yourself. It is up to you how you wish to proceed. Perhaps continue in Python or expand on the Excel created. Next to that, it also allows you to track your personal finances by categorizing your transactions as you desire allowing you to be in full control of your finances.

By doing most of these things through Python and Excel, you have the complete freedom to decide what to do with the output. For example, you can use it to create your own personalized dashboards via any programming language or application such as Excel, PowerBI, Tableau, etc. **I don't want to bore you with custom dashboards that I tailored to myself just so that you can come to the conclusion that it isn't a perfect fit for you.**

# Table of Contents

- [Installation](#installation)
- [Analyzing your Investment Portfolio](#analyzing-your-investment-portfolio)
- [Tracking your Personal Finances](#tracking-your-personal-finances)


# Installation

Before installation, consider starring the project on GitHub which helps others find the project as well. 

To install the FinancePortfolio it simply requires the following:

```
pip install financeportfolio -U
```

Then for **Investment Portfolio** features within Python use:

```python
from financeportfolio import Portfolio

portfolio = Portfolio()
```

This will generate the configuration file for you to use which you can supply again by using `configuration_file='portfolio.yaml`. See below for more information about each capability and what you can do with this file.

# Analyzing your Investment Portfolio

This package allows you to track your portfolio by accepting your portfolio transactions and doing (basic) analysis on the portfolio. It uses functionality from the [Finance Toolkit 🛠️](https://github.com/JerBouma/FinanceToolkit) to be able to determine asset classes as well as obtain historical data and do currency conversions and can directly use ALL of the 130+ metrics that the FinanceToolkit has. It features the following core functionality:

- The ability to read in any combination of datasets, based off the .yaml file, which allows you to combine multiple brokers or multiple accounts into one portfolio.
- The ability to obtain historical data for all instruments in the portfolio including a custom benchmark for each instrument.
- The ability to perform financial analysis on each individual asset and the portfolio as a whole by using the [Finance Toolkit 🛠️](https://github.com/JerBouma/FinanceToolkit).
- An Excel integration in which all of the acquired data can easily be send over to Excel to be further analysed as you desire in case Python isn't your cup of tea. 

It can generate the following overiews:
- **Positions Overview:** an overview which shows the cumulative volumes, costs, invested amount, current value, returns, invested weight and current weight since the inception of the portfolio.
- **Portfolio Overview:** an overview which is an aggregation of each instrument based on volume, price, costs, invested and most recent value. Next to that, it also calculates the return, benchmark return, acquired alpha and the current portfolio weight.
- **Portfolio Performance Overview:** an overview in which the portfolio is shown on a weekly, monthly, quarterly or yearly basis and shows the performance of the portfolio, the benchmark, alpha and weight.
- **Transactions Overview:** an overview which shows all transactions that have been made in the portfolio and their current performance.
- **Transactions Performance Overview:** an overview in which the transactions are shown on a weekly, monthly, quarterly or yearly basis and and shows the end of period returns of the transactions and the benchmark including the alpha.

## Getting Started

To get started, you need to acquire a configuration file that defines your portfolio. This file consists of things such as the location of the datasets, the columns that define e.g. the volume, ticker and price, the currency of the portfolio, the benchmark to use, etc. An example version is automatically downloaded on initialization.

___ 

<b><div align="center">Find detailed guide how to use the Portfolio functionalities <a href="https://www.jeroenbouma.com/projects/financetoolkit">here</a>.</div></b>
___

A basic example is depicted below. This uses the same configuration file as also found in the guide above.

```python
from financeportfolio import Portfolio

portfolio = Portfolio(
    example=True
)

# Positions Overview
positions_overview = portfolio.portfolio.get_positions_overview()

# Portfolio Overview
portfolio_overview = portfolio.portfolio.get_portfolio_overview()

# Quarterly Portfolio Performance Overview
portfolio_performance_overview = portfolio.portfolio.get_portfolio_performance_overview(period='quarterly')

# Transactions Overview
transactions_overview = portfolio.portfolio.get_transactions_overview()

# Yearly Transactions Performance Overview
transactions_performance_overview = portfolio.portfolio.get_transactions_performance_overview(period='monthly')

# The ability to utilize the FinanceToolkit to do further analysis
portfolio_toolkit = portfolio.to_toolkit()

# Show 12-month Rolling Sharpe Ratio
rolling_sharpe_ratio = portfolio_toolkit.performance.get_sharpe_ratio(rolling=12, period='monthly')
```

This returns DataFrame objects which can be used to further analyze the data in Python or send over to Excel.

Furthermore, it is possible to send all of this information (specified in the .yaml file) over to Excel. This is done with the following piece of code:

```python
from financeportfolio import Portfolio

portfolio = Portfolio(
    example=True
)

portfolio.create_excel_report()
```

This creates the following file:

![Portfolio Excel Example](https://github.com/JerBouma/FinancePortfolio/assets/46355364/ffda33c2-b594-46af-9454-48db4205ff05)

# Tracking your Personal Finances

Tracking personal finances can be tedious. It either requires a massive time investment to keep everything well categorized as new transactions come in or it is far from accurate with tools that try to do prediction to define categories for you. Perhaps it works fine for names such as "Wall Mart" or "Starbucks" but your local bakery called "Morty's Place" is definitely not going to get picked up by the model. Many personal finance tools allow you to manually adjust these categories but that is just as tedious as doing it from scratch.

This solution still requires some proper time investment as you will have to define each category but once you have your categories and keywords written down, you can be sure that the model will categorise transactions how you defined them. This is because it is not a generic model that is trained on a large dataset of transactions from all over the world. It is trained on your own data, which means that it will be able to categorise transactions that are specific to you. This results in Morty's Place being correctly categorised as a Bakery.

To assist in not needing to get **exact** matches, the package makes use of the [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance) to determine how similar two strings are. This means that if you have a category called "Groceries" with the keyword "Supermarket" and a transaction comes in with the name "Rick's Super Market", it will still be categorised as "Groceries". There is a limited amount of Mumbo Jumbo going on here on purpose so that it still becomes logical why it is categorised as such.

Once categorization is done, it is able to create a neat looking Excel file for you that you can fully customize yourself further. It is up to you how you wish to proceed. Perhaps continue in Python or expand on the Excel created. I believe that everyone has his custom needs in which no tool can fully provide whereas Python and Excel gives you the freedom to expand how you'd like.
