![FinancePortfolio](https://github.com/JerBouma/FinancePortfolio/assets/46355364/d3560ff3-1d2a-4ba2-a99d-dcf7b6ec2c5c)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor_this_Project-grey?logo=github)](https://github.com/sponsors/JerBouma)
[![Documentation](https://img.shields.io/badge/Documentation-grey?logo=readme)](https://www.jeroenbouma.com/projects/FinancePortfolio)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/FinancePortfolio)](https://pypi.org/project/FinancePortfolio/)
[![PYPI Version](https://img.shields.io/pypi/v/FinancePortfolio)](https://pypi.org/project/FinancePortfolio/)
[![PYPI Downloads](https://static.pepy.tech/badge/FinanceToolkit/month)](https://pepy.tech/project/FinancePortfolio)

Tracking your investment portfolio and personal finances can be tedious. It either requires proprietary software to be used that often have limited features until you pay for a subscription or/and it requires a great amount of manual input just to get the overview you are looking for. And even once you have this overview, it is often not in the format you desire, does not apply the categorization as you wish or is simply not accurate in the first place.

**I want to give you back the control to properly and efficiently track your finances with the FinancePortfolio**. Through the usage of configuration files, it becomes possible to connect multiple brokers as you desire and have the FinancePortfolio do the heavy lifting for you. It will automatically obtain historical data for all instruments in your portfolio, calculate the returns, benchmark returns, alpha and weight of each instrument and (optionally) provide you with a neat looking Excel file that you can further customize yourself.

**It has the ability to send over your assets and portfolio to the [Finance Toolkit 🛠️](https://github.com/JerBouma/FinanceToolkit) automatically which allows the calculation of 130+ ratios, technicals, performance and risk measurements directly onto your portfolio. See [here](#finance-toolkit-support).**

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

Then to use the features within Python use:

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
positions_overview = portfolio.get_positions_overview()

# Portfolio Overview
portfolio_overview = portfolio.get_portfolio_overview()

# Quarterly Portfolio Performance Overview
portfolio_performance_overview = portfolio.get_portfolio_performance_overview(period='quarterly')

# Transactions Overview
transactions_overview = portfolio.get_transactions_overview()

# Yearly Transactions Performance Overview
transactions_performance_overview = portfolio.get_transactions_performance_overview(period='monthly')

# The ability to utilize the FinanceToolkit to do further analysis
portfolio_toolkit = portfolio.to_toolkit()

# Show 12-month Rolling Sharpe Ratio
rolling_sharpe_ratio = portfolio_toolkit.performance.get_sharpe_ratio(rolling=12, period='monthly')
```

This returns DataFrame objects which can be used to further analyze the data in Python or send over to Excel.

### Positions Overview

The Positions Overview shows the cumulative volumes, costs, invested amount, current value, returns, invested weight and current weight since the inception of the portfolio. Here, the first few rows for the instrument 'VUSA.AS' are shown (Vanguard's S&P 500 ETF):

| Date       |   Volume |   Costs |   Invested Amount |   Current Value |   Cumulative Return |   Invested Weight |   Current Weight |
|:-----------|---------:|--------:|------------------:|----------------:|--------------------:|------------------:|-----------------:|
| 2020-01-15 |        4 |       0 |            224.32 |          224.41 |                1    |              0.44 |             0.44 |
| 2020-01-16 |        4 |       0 |            224.32 |          225.5  |                1.01 |              0.44 |             0.44 |
| 2020-01-17 |        4 |       0 |            224.32 |          227.54 |                1.01 |              0.44 |             0.44 |
| 2020-01-20 |        4 |       0 |            224.32 |          227.86 |                1.02 |              0.44 |             0.44 |
| 2020-01-21 |        4 |       0 |            224.32 |          227.71 |                1.02 |              0.44 |             0.44 |

### Portfolio Overview

The Portfolio Overview is an aggregation of each instrument based on volume, price, costs, invested and most recent value. Next to that, it also calculates the return, benchmark return, acquired alpha and the current portfolio weight.

| Ticker   | Name                                      |   Volume |   Price |   Costs |   Invested |   Latest Price |   Latest Value |   Return |   Return Value |   Benchmark Return |   Alpha |   Weight |
|:---------|:------------------------------------------|---------:|--------:|--------:|-----------:|---------------:|---------------:|---------:|---------------:|-------------------:|--------:|---------:|
| ESP0.DE  | VANECK VIDEO GAMING AND ESPORTS UCITS ETF |        5 |   36.07 |    0    |     180.37 |          31    |         155.02 |    -0.14 |         -25.34 |               0.01 |   -0.16 |     0    |
| IUSA.AS  | ISHARES S&P 500                           |       96 |   38.15 |   -1    |    3662.57 |          41.09 |        3944.93 |     0.08 |         282.36 |               0.16 |   -0.08 |     0.08 |
| IWDA.AS  | ISHARES MSCI WOR A                        |      247 |   68.34 |   -5.14 |   16880.8  |          77.83 |       19225.2  |     0.14 |        2344.42 |               0.23 |   -0.09 |     0.38 |
| SMH.MI   | VANECK SEMICONDUCTOR UCITS ETF            |       -2 |  -22.33 |    0    |      44.67 |          26.42 |         -52.84 |    -2.18 |         -97.51 |              -1.2  |   -0.98 |    -0    |
| UST.PA   | MULTI NASDAQ 100                          |       84 |   43.48 |   -7.02 |    3652.35 |          57.54 |        4833.36 |     0.32 |        1181.01 |               0.19 |    0.13 |     0.1  |
| VUSA.AS  | VANGUARD S&P500                           |      116 |   62.97 |   -3    |    7304.21 |          78.27 |        9079.32 |     0.24 |        1775.11 |               0.2  |    0.04 |     0.18 |
| VWRL.AS  | VANGUARD FTSE AW                          |      132 |   99.24 |    0    |   13099.2  |         102.82 |       13572.2  |     0.04 |         473.07 |               0.02 |    0.01 |     0.27 |

### Portfolio Performance Overview

The Portfolio Performance Overview shows the performance of the portfolio, the benchmark, alpha and weight on a weekly, monthly, quarterly or yearly basis. Here some of the data is shown that represents the performance of the portfolio on a quarterly basis:

| Date   | Ticker   |   Volume |   Costs |   Invested Amount |   Current Value |   Invested Weight |   Current Weight |   Return |
|:-------|:---------|---------:|--------:|------------------:|----------------:|------------------:|-----------------:|---------:|
| 2023Q3 | ESP0.DE  |        5 |    0    |            180.37 |          153.42 |              0    |             0    |    -0.15 |
| 2023Q3 | IUSA.AS  |       96 |   -1    |           3662.57 |         3895.78 |              0.08 |             0.08 |     0.06 |
| 2023Q3 | IWDA.AS  |      247 |   -5.14 |          16880.8  |        19090.6  |              0.38 |             0.38 |     0.13 |
| 2023Q3 | SMH.MI   |       -2 |    0    |             44.67 |          -51.24 |              0    |            -0    |    -2.15 |
| 2023Q3 | UST.PA   |       84 |   -7.02 |           3652.35 |         4715.09 |              0.08 |             0.09 |     0.29 |
| 2023Q3 | VUSA.AS  |      116 |   -3    |           7304.21 |         8962.74 |              0.16 |             0.18 |     0.23 |
| 2023Q3 | VWRL.AS  |      132 |    0    |          13099.2  |        13490.4  |              0.29 |             0.27 |     0.03 |
| 2023Q4 | ESP0.DE  |        5 |    0    |            180.37 |          155.02 |              0    |             0    |    -0.14 |
| 2023Q4 | IUSA.AS  |       96 |   -1    |           3662.57 |         3944.93 |              0.08 |             0.08 |     0.08 |
| 2023Q4 | IWDA.AS  |      247 |   -5.14 |          16880.8  |        19225.2  |              0.38 |             0.38 |     0.14 |
| 2023Q4 | SMH.MI   |       -2 |    0    |             44.67 |          -52.84 |              0    |            -0    |    -2.18 |
| 2023Q4 | UST.PA   |       84 |   -7.02 |           3652.35 |         4833.36 |              0.08 |             0.1  |     0.32 |
| 2023Q4 | VUSA.AS  |      116 |   -3    |           7304.21 |         9079.32 |              0.16 |             0.18 |     0.24 |
| 2023Q4 | VWRL.AS  |      132 |    0    |          13099.2  |        13572.2  |              0.29 |             0.27 |     0.04 |

### Transactions Overview

The Transactions Overview shows all transactions that have been made in the portfolio and their current performance. It demonstrates how well assets have performed over time and could be used for example to understand the market timing of the investor.

| Date       | Ticker   | Name                           |   Price |   Volume |   Costs | Currency   |   Invested Amount |   Current Value |   % Return |   Return |
|:-----------|:---------|:-------------------------------|--------:|---------:|--------:|:-----------|------------------:|----------------:|-----------:|---------:|
| 2022-10-27 | IWDA.AS  | ISHARES MSCI WOR A             |  71     |       22 |       0 | EUR        |          1562     |         1712.37 |  0.0962676 |  150.37  |
| 2022-12-01 | VUSA.AS  | VANGUARD S&P500                |  74.171 |        4 |       0 | EUR        |           296.684 |          313.08 |  0.0552642 |   16.396 |
| 2022-12-01 | IWDA.AS  | ISHARES MSCI WOR A             |  73.69  |       15 |       0 | EUR        |          1105.35  |         1167.52 |  0.0562492 |   62.175 |
| 2022-12-01 | VWRL.AS  | VANGUARD FTSE AW               |  99.98  |        5 |       0 | EUR        |           499.9   |          514.1  |  0.0284057 |   14.2   |
| 2022-12-01 | UST.PA   | MULTI NASDAQ 100               |  45.92  |        2 |       0 | EUR        |            91.84  |          115.08 |  0.253049  |   23.24  |
| 2022-12-30 | IWDA.AS  | ISHARES MSCI WOR A             |  68.47  |       14 |      -3 | EUR        |           955.58  |         1089.69 |  0.140344  |  134.11  |
| 2022-12-30 | SMH.MI   | VANECK SEMICONDUCTOR UCITS ETF |  17.896 |        1 |       0 | EUR        |            17.896 |           26.42 |  0.476308  |    8.524 |
| 2022-12-30 | VUSA.AS  | VANGUARD S&P500                |  67.84  |        7 |      -3 | EUR        |           471.88  |          547.89 |  0.161079  |   76.01  |
| 2022-12-30 | UST.PA   | MULTI NASDAQ 100               |  40.58  |        4 |      -3 | EUR        |           159.32  |          230.16 |  0.44464   |   70.84  |
| 2023-03-01 | SMH.MI   | VANECK SEMICONDUCTOR UCITS ETF |  21.245 |     -116 |       0 | EUR        |         -2464.42  |        -3064.72 |  0.243587  | -600.3   |
| 2023-03-01 | IUSA.AS  | ISHARES S&P 500                |  37.11  |       66 |       0 | EUR        |          2449.26  |         2712.14 |  0.10733   |  262.878 |
| 2023-06-30 | IUSA.AS  | ISHARES S&P 500                |  40.477 |       30 |      -1 | EUR        |          1213.31  |         1232.79 |  0.0160553 |   19.48  |

### Transactions Performance Overview

The Transactions Performance Overview shows the transactions on a weekly, monthly, quarterly or yearly basis and and shows the end of period returns of the transactions and the benchmark including the alpha. Here some of the data is shown that represents the performance of the transactions on a monthly basis:

| Date    | Ticker   |   Volume |   Price |   Costs |   Invested Amount |   Current Value |   Return |   Benchmark Return |   Alpha |
|:--------|:---------|---------:|--------:|--------:|------------------:|----------------:|---------:|-------------------:|--------:|
| 2022-10 | IWDA.AS  |       22 |   71    |       0 |           1562    |         1591.48 |   0.0189 |             0.0191 | -0.0002 |
| 2022-10 | SMH.MI   |        1 |   17.71 |       0 |             17.71 |           18.03 |   0.0181 |             0.017  |  0.0011 |
| 2022-10 | VUSA.AS  |        3 |   72.62 |       0 |            217.86 |          223.02 |   0.0237 |             0.017  |  0.0067 |
| 2022-10 | VWRL.AS  |        3 |   95.5  |       0 |            286.5  |          291.99 |   0.0192 |             0.017  |  0.0022 |
| 2022-12 | IWDA.AS  |       29 |   71.08 |      -3 |           2064.32 |         1980.26 |  -0.0407 |            -0.048  |  0.0073 |
| 2022-12 | SMH.MI   |        1 |   17.9  |       0 |             17.9  |           17.83 |  -0.0039 |             0      | -0.0039 |
| 2022-12 | UST.PA   |        6 |   43.25 |      -3 |            262.5  |          243.27 |  -0.0733 |            -0.048  | -0.0253 |
| 2022-12 | VUSA.AS  |       11 |   71.01 |      -3 |            784.11 |          744.94 |  -0.05   |            -0.0299 | -0.0201 |
| 2022-12 | VWRL.AS  |        5 |   99.98 |       0 |            499.9  |          463.2  |  -0.0734 |            -0.0582 | -0.0152 |
| 2023-03 | IUSA.AS  |       66 |   37.11 |       0 |           2449.26 |         2468.4  |   0.0078 |             0.1041 | -0.0963 |
| 2023-03 | SMH.MI   |     -116 |   21.24 |       0 |          -2463.84 |        -2589.7  |   0.0511 |             0.04   |  0.0111 |
| 2023-06 | IUSA.AS  |       30 |   40.48 |      -1 |           1215.4  |         1214.55 |  -0.0007 |             0      | -0.0007 |

### Finance Toolkit Support

Once everything is prepared, the true power comes from integration with the [Finance Toolkit 🛠️](https://github.com/JerBouma/FinanceToolkit) as the data is formatted in such a way that it can be directly fed into the FinanceToolkit with `.to_toolkit`. This gives access to 130+ ratios, technicals, performance and risk metrics as well as financial statements, earnings calendars, analyst estimates, snapshots and much more. Through the collected insights from the FinancePortfolio, a 'Portfolio' column is constructured which represents the performance of the portfolio as a whole.

For example, the following shows the Rolling 12-month Sharpe Ratio of both the individual assets as well as the entire portfolio as a whole.

| Date    |   VUSA.AS |   IWDA.AS |   UST.PA |   VWRL.AS |   SMH.MI |   ESP0.DE |   IUSA.AS |   Portfolio |
|:--------|----------:|----------:|---------:|----------:|---------:|----------:|----------:|------------:|
| 2023-01 |   -0.6083 |   -0.6255 |  -0.5734 |   -0.6929 |  -0.37   |   -0.6105 |   -0.6122 |     -0.6553 |
| 2023-02 |   -0.5958 |   -0.6179 |  -0.5243 |   -0.6967 |  -0.3558 |   -0.6523 |   -0.5999 |     -0.682  |
| 2023-03 |   -0.7531 |   -0.7528 |  -0.5599 |   -0.816  |  -0.347  |   -0.4768 |   -0.7566 |     -0.8007 |
| 2023-04 |   -0.7155 |   -0.718  |  -0.5107 |   -0.7887 |  -0.2837 |   -0.4632 |   -0.7194 |     -0.7653 |
| 2023-05 |   -0.5999 |   -0.6375 |  -0.2826 |   -0.7082 |  -0.1535 |   -0.395  |   -0.6009 |     -0.6476 |
| 2023-06 |   -0.4816 |   -0.5157 |  -0.1866 |   -0.6056 |  -0.0341 |   -0.2954 |   -0.4848 |     -0.55   |
| 2023-07 |   -0.8659 |   -0.906  |  -0.3859 |   -0.9468 |  -0.172  |   -0.3764 |   -0.8779 |     -0.9031 |
| 2023-08 |   -0.8485 |   -0.8999 |  -0.3687 |   -0.9525 |  -0.1313 |   -0.4005 |   -0.8604 |     -0.9427 |
| 2023-09 |   -0.865  |   -0.9332 |  -0.3442 |   -1.0091 |  -0.0857 |   -0.3609 |   -0.8757 |     -0.9862 |
| 2023-10 |   -1.0288 |   -1.1043 |  -0.3222 |   -1.1324 |  -0.0592 |   -0.3196 |   -1.0327 |     -1.1474 |

Which can also be graphically depicted through:

```python
rolling_sharpe_ratio.plot(figsize=(15, 5), title="Rolling 12-month Sharpe Ratio")
```

Which returns:

![Rolling Sharpe Ratio](https://github.com/JerBouma/FinancePortfolio/assets/46355364/b16d6593-4953-4b70-acc8-bdf4c680ec43)

### Excel Integration

It is possible to send all of this information (specified in the .yaml file) over to Excel. This is the same output as depicted above but in a neatly organized Excel file. This is done through the `create_excel_report` function.

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
