"""Portfolio Model"""

import os

import numpy as np
import pandas as pd
from tqdm import tqdm

from financeportfolio import helpers

# pylint: disable=too-many-locals

# Matches up with currency codes EUR, USD, JPY etc. This is used for
# Yahoo Finance's notation of currencies. E.g. EURUSD=X
CURRENCY_CODE_LENGTH = 3


def read_portfolio_dataset(
    excel_location: list,
    adjust_duplicates: bool,
    date_column: list[str],
    date_format: str,
    name_columns: list[str],
    ticker_columns: list[str],
    price_columns: list[str],
    volume_columns: list[str],
    column_mapping: dict[str, str],
    currency_columns: list[str] | str | None = None,
    costs_columns: list[str] | None = None,
) -> tuple[pd.DataFrame, str, str, str, str, str, str]:
    """
    Read and preprocess a cash flow dataset from Excel files.

    This function reads one or more Excel files located at 'excel_location' and combines them into
    a single portfolio dataset. It performs formatting and preprocessing tasks on the dataset, including
    renaming columns to lowercase, handling duplicates, and parsing dates. The resulting dataset is returned,
    along with information about column names and processing.

    Args:
        excel_location (list): A list of file paths to Excel files containing cash flow data.
        adjust_duplicates (bool): A flag indicating whether to adjust for duplicate entries in the dataset.
        date_column (list[str]): A list of column names representing date information in the dataset.
        date_format (str): The format of date strings in the date column.
        name_columns (list[str]): A list of column names representing transaction descriptions.
        ticker_columns (list[str]): A list of column names representing asset tickers.
        price_columns (list[str]): A list of column names representing asset prices in the dataset.
        volume_columns (list[str]): A list of column names representing asset volumes in the dataset.
        currency_columns (list[str] | str | None, optional): A list of column names representing currency
            codes or a single currency column name. Defaults to None.
        costs_columns (list[str] | None, optional): A list of column names representing transaction costs or
            None if not applicable.
        column_mapping (dict | None, optional): A dictionary mapping column names in the dataset to standardized names.
            Defaults to None.

    Returns:
        tuple[pd.DataFrame, str, str, str, str, str, str | None]: A tuple containing the
        processed cash flow dataset as the first element, and the following information:
        - date_column: The name of the selected date column.
        - name_columns: A list of formatted description column names.
        - ticker_columns: The name of the selected ticker column.
        - price_columns: The name of the selected price column.
        - volume_columns: The name of the selected volume column.
        - currency_columns: The name of the selected currency column (if processed).
        - costs_columns: The name of the selected costs column (if processed).

    Raises:
        ValueError: If no valid Excel files are found at the specified 'excel_location'.
        ValueError: If no date columns are found in the portfolio dataset.
        ValueError: If no ticker columns are found in the portfolio dataset.
        ValueError: If no name columns are found in the portfolio dataset.
        ValueError: If no price columns are found in the portfolio dataset.
        ValueError: If no volume columns are found in the portfolio dataset.
    """
    combined_portfolio_dataset = pd.DataFrame()
    additional_files = []
    for file in excel_location:
        if file.split(".")[-1] not in ["xlsx", "csv"]:
            excel_location.remove(file)

            for sub_file in os.listdir(file):
                if sub_file.endswith(("xlsx", "csv")):
                    additional_files.append(f"{file}/{sub_file}")

    excel_location = excel_location + additional_files

    for file in (
        tqdm(excel_location, desc="Reading Portfolio Files")
        if len(excel_location) > 1
        else excel_location
    ):
        portfolio_dataset = helpers.read_excel(file)
        portfolio_dataset.columns = portfolio_dataset.columns.str.lower()

        (
            portfolio_dataset,
            selected_date_column,
            selected_name_column,
            selected_ticker_column,
            selected_price_column,
            selected_volume_column,
            selected_currency_column,
            selected_costs_column,
        ) = format_portfolio_dataset(
            dataset=portfolio_dataset,
            date_columns=date_column,
            date_format=date_format,
            name_columns=name_columns,
            tickers_columns=ticker_columns,
            price_columns=price_columns,
            volume_columns=volume_columns,
            column_mapping=column_mapping,
            currency_columns=currency_columns,
            costs_columns=costs_columns,
        )

        if portfolio_dataset.duplicated().any() and adjust_duplicates:
            print(f"Found duplicates in {file}. These will be added together.")
            duplicates = portfolio_dataset[portfolio_dataset.duplicated()]
            originals = portfolio_dataset[portfolio_dataset.duplicated(keep="first")]

            number_columns = list(
                duplicates.select_dtypes(np.number).columns.intersection(
                    originals.select_dtypes(np.number).columns
                )
            )

            # It shouldn't add together the prices as this falsely indicates a higher investment
            # than actually made and result in false return calculations.
            number_columns.remove(selected_price_column)  # type: ignore

            duplicates.loc[:, number_columns] = duplicates.loc[:, number_columns].add(
                originals[number_columns], fill_value=0
            )

            portfolio_dataset = pd.concat(
                [portfolio_dataset, duplicates]
            ).drop_duplicates(keep=False)

        combined_portfolio_dataset = pd.concat(
            [combined_portfolio_dataset, portfolio_dataset]
        )

    if combined_portfolio_dataset.duplicated().any() and adjust_duplicates:
        print(
            "Found duplicates in the combination of datasets. This is usually due to overlapping periods. "
            "The duplicates will be removed from the datasets to prevent counting the same transaction twice."
        )
        combined_portfolio_dataset = combined_portfolio_dataset.drop_duplicates()

    combined_portfolio_dataset = combined_portfolio_dataset.sort_values(
        by=selected_date_column, ascending=False  # type: ignore
    )

    return (
        combined_portfolio_dataset,
        selected_date_column,  # type: ignore
        selected_name_column,  # type: ignore
        selected_ticker_column,  # type: ignore
        selected_price_column,  # type: ignore
        selected_volume_column,  # type: ignore
        selected_currency_column,  # type: ignore
        selected_costs_column,  # type: ignore
    )


def format_portfolio_dataset(
    dataset: pd.DataFrame,
    date_columns: list[str],
    date_format: str,
    name_columns: list[str],
    tickers_columns: list[str],
    price_columns: list[str],
    volume_columns: list[str],
    column_mapping: dict[str, str],
    currency_columns: list[str] | str | None = None,
    costs_columns: list[str] | None = None,
) -> tuple[pd.DataFrame, str, str, str, str, str, str, str]:
    """
    Format and preprocess a portfolio dataset.

    This function takes a raw cash flow dataset and performs formatting and preprocessing tasks
    to prepare it for analysis. It includes actions like setting the date column, converting
    date strings to datetime objects, formatting description columns as categories, and handling
    numeric values, including decimal separators. It also optionally handles cost or income columns
    based on the provided criteria.

    Args:
        dataset (pd.DataFrame): The raw cash flow dataset to be formatted.
        date_columns (list[str]): A list of column names representing date information in the dataset.
        date_format (str): The format of date strings in the date column.
        name_columns (list[str]): A list of column names representing transaction descriptions.
        tickers_columns (list[str]): A list of column names representing asset tickers.
        price_columns (list[str]): A list of column names representing asset prices in the dataset.
        volume_columns (list[str]): A list of column names representing asset volumes in the dataset.
        currency_columns (list[str] | str | None, optional): A list of column names representing currency codes
            or a single currency column name. Defaults to None.
        costs_columns (list[str] | None, optional): A list of column names representing transaction costs
            or None if not applicable.
        column_mapping (dict | None, optional): A dictionary mapping column names in the dataset to standardized names.
            Defaults to None.

    Returns:
        tuple[pd.DataFrame, str, str, str, str, str, str | None]: A tuple containing the
        formatted cash flow dataset as the first element and the following information:
        - date_columns: The name of the selected date column.
        - name_columns: A list of formatted description column names.
        - tickers_columns: The name of the selected ticker column.
        - price_columns: The name of the selected price column.
        - volume_columns: The name of the selected volume column.
        - currency_columns: The name of the selected currency column (if processed).
        - costs_columns: The name of the selected costs column (if processed).

    Raises:
        ValueError: If no date columns are found in the portfolio dataset.
        ValueError: If no ticker columns are found in the portfolio dataset.
        ValueError: If no name columns are found in the portfolio dataset.
        ValueError: If no price columns are found in the portfolio dataset.
        ValueError: If no volume columns are found in the portfolio dataset.
        ValueError: If cost or income columns are specified in the configuration, but none are found in the dataset.
        ValueError: If the currency column contains values other than 3-letter currency codes.
        ValueError: If the provided currency code is not a 3-letter code.
    """
    date_columns = [column.lower() for column in date_columns]
    date_column_match = [column for column in date_columns if column in dataset.columns]

    if not date_column_match:
        raise ValueError(
            "No date columns found in the portfolio dataset. Please specify the columns in the configuration file"
            "or set the 'date_columns' variable in the initialization."
        )
    date_column_first = date_column_match[0]

    dataset = dataset.set_index(date_column_first)

    dataset.index = pd.to_datetime(dataset.index, format=date_format).to_period(
        freq="D"
    )

    dataset = dataset.reset_index()

    tickers_columns = [column.lower() for column in tickers_columns]
    tickers_columns_match = [
        column for column in tickers_columns if column in dataset.columns
    ]

    if not tickers_columns_match:
        raise ValueError(
            "No tickers columns found in the portfolio dataset. Please specify the columns in the configuration file. "
            "or set the 'tickers_columns' variable in the initialization."
        )
    tickers_column_first = tickers_columns_match[0]
    dataset[tickers_column_first] = dataset[tickers_column_first].astype("category")

    name_columns = [column.lower() for column in name_columns]
    name_columns_match = [
        column for column in name_columns if column in dataset.columns
    ]

    if not name_columns_match:
        print(
            "No name columns found in the portfolio dataset. Please specify the columns in the configuration file.\n"
            "or set the 'name_columns' variable in the initialization. Using the ticker column as the name column "
            "instead."
        )
        name_columns_match = tickers_columns_match

    name_column_first = name_columns_match[0]
    dataset[name_column_first] = dataset[name_column_first].astype("category")

    price_columns = [column.lower() for column in price_columns]
    price_columns_match = [
        column for column in price_columns if column in dataset.columns
    ]

    if not price_columns_match:
        raise ValueError(
            "No price columns found in the portfolio dataset. Please specify the columns in the configuration file. "
            "or set the 'price_columns' variable in the initialization."
        )
    price_column_first = price_columns_match[0]
    dataset[price_column_first] = dataset[price_column_first].astype("float")

    volume_columns = [column.lower() for column in volume_columns]
    volume_columns_match = [
        column for column in volume_columns if column in dataset.columns
    ]

    if not volume_columns_match:
        raise ValueError(
            "No volume columns found in the portfolio dataset. Please specify the columns in the configuration file. "
            "or set the 'volume_columns' variable in the initialization."
        )
    volume_column_first = volume_columns_match[0]
    dataset[volume_column_first] = dataset[volume_column_first].astype("float")

    if costs_columns:
        costs_columns = [column.lower() for column in costs_columns]
        costs_columns_match = [
            column for column in costs_columns if column in dataset.columns
        ]

        if not costs_columns_match:
            print(
                "No costs columns found in the portfolio dataset. Please specify the columns in the configuration file. "
                "or set the 'cost_columns' variable in the initialization. Setting costs to zero for now."
            )
            costs_column_first = "TEMP Costs"
            dataset[costs_column_first] = 0.0
        else:
            costs_column_first = costs_columns_match[0]
            dataset[costs_column_first] = dataset[costs_column_first].astype("float")
            dataset[costs_column_first] = dataset[costs_column_first].fillna(0)
    else:
        costs_column_first = None

    if isinstance(currency_columns, list):
        currency_columns = [column.lower() for column in currency_columns]
        currency_columns_match = [
            column for column in currency_columns if column in dataset.columns
        ]

        if not currency_columns_match:
            print(
                "No currency columns found in the portfolio dataset. Please specify the columns in the "
                "configuration file or set the 'currency_columns' variable in the initialization. "
                "Setting the currency to EUR for now."
            )
            currency_column_first = "TEMP Currency"
            dataset[currency_column_first] = "EUR"
        else:
            currency_column_first = currency_columns_match[0]

            if dataset[currency_column_first].str.len().max() != CURRENCY_CODE_LENGTH:
                raise ValueError(
                    "Currency column must contain 3-letter currency codes only (e.g. EUR, USD or JPY)."
                )

            dataset[currency_column_first] = dataset[currency_column_first].astype(
                "category"
            )
            dataset[currency_column_first] = dataset[currency_column_first].str.upper()

            # This is mostly done given that Unnamed columns could exist in the dataset, specifically in
            # the DEGIRO dataset and are automatically dropped. This prevents this column from being dropped.
            dataset = dataset.rename(columns={currency_column_first: "currency"})
            currency_column_first = "currency"

    elif isinstance(currency_columns, str):
        if len(currency_columns) != CURRENCY_CODE_LENGTH:
            raise ValueError(
                "Currency must be a 3-letter currency code (e.g. EUR, USD or JPY)."
            )
        currency_column_first = currency_columns.upper()
    else:
        currency_column_first = None

    # Rename all columns that are relevant and drop the others. This is done so that any type of file
    # can be added to your portfolio and it will still work.
    dataset = dataset.rename(
        columns={
            date_column_first: column_mapping["date"],
            name_column_first: column_mapping["name"],
            tickers_column_first: column_mapping["ticker"],
            price_column_first: column_mapping["price"],
            volume_column_first: column_mapping["volume"],
            currency_column_first: column_mapping["currency"],
            costs_column_first: column_mapping["costs"],
        }
    )

    # Drop out any other columns, this is done so that any type of file can be added to your portfolio
    # and it will still work.
    dataset = dataset[column_mapping.values()]

    return (
        dataset,
        column_mapping["date"],
        column_mapping["name"],
        column_mapping["ticker"],
        column_mapping["price"],
        column_mapping["volume"],
        column_mapping["currency"],
        column_mapping["costs"],
    )


def create_transactions_overview(
    portfolio_volume: pd.Series,
    portfolio_price: pd.Series,
    portfolio_costs: pd.Series,
    latest_returns: pd.Series,
):
    """
    Calculate an overview of transaction performance for individual assets.

    This function calculates an overview of transaction performance metrics for each
    asset in the portfolio, including metrics such as 'Invested Amount', 'Current Value',
    'Percentage Return', and 'Value Return'.

    Args:
        portfolio_volume (pd.Series): A Series containing asset volumes in the portfolio.
        portfolio_price (pd.Series): A Series containing asset prices in the portfolio.
        portfolio_costs (pd.Series): A Series containing transaction costs for assets in the portfolio.
        latest_returns (pd.Series): A Series containing the latest returns for assets in the portfolio.

    Returns:
        pd.DataFrame: A DataFrame containing an overview of transaction performance metrics
        for individual assets in the portfolio.
    """

    invested_amount = []
    current_value = []
    percentage_return = []
    value_return = []

    for row, (_, ticker) in enumerate(portfolio_volume.index):
        bought_value = portfolio_volume.iloc[row] * portfolio_price.iloc[row] - abs(
            portfolio_costs.iloc[row]
        )
        recent_value = portfolio_volume.iloc[row] * latest_returns.loc[ticker]

        invested_amount.append(bought_value)
        current_value.append(recent_value)
        percentage_return.append((recent_value / bought_value) - 1)
        value_return.append(recent_value - bought_value)

    new_columns = pd.DataFrame(
        [invested_amount, current_value, percentage_return, value_return],
        columns=portfolio_volume.index,
        index=["Invested Amount", "Current Value", "% Return", "Return"],
    ).T

    return new_columns


def create_portfolio_overview(
    portfolio_name: pd.Series,
    portfolio_volume: pd.Series,
    portfolio_price: pd.Series,
    portfolio_costs: pd.Series,
    latest_returns: pd.Series,
    benchmark_prices: pd.Series,
    benchmark_latest_prices: pd.Series,
):
    """
    Calculate an overview of portfolio positions and related metrics.

    This function calculates an overview of the portfolio's positions and related metrics,
    including key statistics, performance metrics, and weights.

    Args:
        portfolio_name (pd.Series): A Series containing asset names in the portfolio.
        portfolio_volume (pd.Series): A Series containing asset volumes in the portfolio.
        portfolio_price (pd.Series): A Series containing asset prices in the portfolio.
        portfolio_costs (pd.Series): A Series containing transaction costs for assets in the portfolio.
        latest_returns (pd.Series): A Series containing the latest returns for assets in the portfolio.
        benchmark_prices (pd.Series): A Series containing historical benchmark prices.
        benchmark_latest_prices (pd.Series): A Series containing the latest benchmark prices.

    Returns:
        pd.DataFrame: A DataFrame containing an overview of portfolio positions and related metrics.

    Notes:
        The function calculates metrics such as 'Invested', 'Benchmark Invested', 'Latest Price',
        'Latest Value', 'Return', 'Return Value', 'Benchmark Return', 'Alpha', and 'Weight'
        for each asset in the portfolio.
    """

    portfolio_overview = pd.DataFrame(index=portfolio_name.index)
    portfolio_overview["Name"] = portfolio_name
    portfolio_overview["Volume"] = portfolio_volume
    portfolio_overview["Costs"] = portfolio_costs
    portfolio_overview["Invested"] = portfolio_volume * portfolio_price - abs(
        portfolio_costs
    )
    portfolio_overview["Benchmark Invested"] = (
        portfolio_volume * benchmark_prices.to_numpy()
    )

    portfolio_overview_grouped = portfolio_overview.groupby(
        "Ticker", observed=True
    ).agg(
        {
            "Name": "first",
            "Volume": "sum",
            "Costs": "sum",
            "Invested": "sum",
            "Benchmark Invested": "sum",
        }
    )

    latest_price_values = []
    for ticker in portfolio_overview_grouped.index:
        latest_price_values.append(latest_returns.loc[ticker])

    portfolio_overview_grouped.insert(
        2,
        "Price",
        portfolio_overview_grouped["Invested"] / portfolio_overview_grouped["Volume"],
    )

    portfolio_overview_grouped["Latest Price"] = latest_price_values
    portfolio_overview_grouped["Latest Value"] = (
        portfolio_overview_grouped["Volume"]
        * portfolio_overview_grouped["Latest Price"]
    )

    benchmark_latest_value = (
        portfolio_overview_grouped["Volume"] * benchmark_latest_prices
    )

    portfolio_overview_grouped["Return"] = (
        portfolio_overview_grouped["Latest Value"]
        / portfolio_overview_grouped["Invested"]
        - 1
    )
    portfolio_overview_grouped["Return Value"] = (
        portfolio_overview_grouped["Latest Value"]
        - portfolio_overview_grouped["Invested"]
    )
    portfolio_overview_grouped["Benchmark Return"] = (
        benchmark_latest_value / portfolio_overview_grouped["Benchmark Invested"] - 1
    )
    portfolio_overview_grouped["Alpha"] = (
        portfolio_overview_grouped["Return"]
        - portfolio_overview_grouped["Benchmark Return"]
    )
    portfolio_overview_grouped["Weight"] = (
        portfolio_overview_grouped["Latest Value"]
        / portfolio_overview_grouped["Latest Value"].sum()
    )

    portfolio_overview_grouped = portfolio_overview_grouped.drop(
        columns=["Benchmark Invested"]
    )

    portfolio_overview_grouped = portfolio_overview_grouped.round(2)

    return portfolio_overview_grouped


def create_transactions_performance(
    portfolio_dataset: pd.DataFrame,
    ticker_column: str,
    date_column: str,
    volume_column: str,
    price_column: str,
    costs_column: str,
    period_prices: pd.DataFrame,
    period_string: str,
    original_ticker_combinations: dict,
    benchmark_per_ticker: dict,
    benchmark_specific_prices: pd.Series,
    benchmark_period_prices: pd.DataFrame,
):
    """
    Calculate transaction performance metrics for a specified period.

    This function calculates various transaction performance metrics, such as returns,
    costs, and benchmarks, for the specified period using the provided datasets.

    Args:
        portfolio_dataset (pd.DataFrame): The dataset containing portfolio transaction data.
        ticker_column (str): The name of the column representing asset tickers.
        date_column (str): The name of the column representing transaction dates.
        volume_column (str): The name of the column representing transaction volumes.
        price_column (str): The name of the column representing transaction prices.
        costs_column (str): The name of the column representing transaction costs.
        period_prices (pd.DataFrame): Historical price data for assets during the specified period.
        period_string (str): The time period for which transaction performance metrics
            should be calculated. This can be 'yearly', 'quarterly', 'monthly', 'weekly', or 'daily'.
        original_ticker_combinations (dict): A dictionary mapping adjusted tickers to their original forms.
        benchmark_per_ticker (dict): A dictionary mapping original tickers to their benchmark tickers.
        benchmark_specific_prices (pd.Series): Historical benchmark-specific prices.
        benchmark_period_prices (pd.DataFrame): Historical benchmark prices during the specified period.

    Returns:
        pd.DataFrame: A DataFrame containing transaction performance metrics.

    Raises:
        ValueError: If an invalid or unsupported period_string is provided.
    """
    portfolio_dataset["Benchmark Price"] = benchmark_specific_prices.to_numpy()

    period_performance = portfolio_dataset.reset_index()

    period_performance = period_performance.set_index([date_column, ticker_column])

    dates = period_performance.index.get_level_values(date_column).asfreq(period_string)

    period_performance_grouped = period_performance.groupby(
        [dates, ticker_column], observed=True
    ).agg(
        {
            volume_column: "sum",
            price_column: "mean",
            costs_column: "sum",
            "Benchmark Price": "mean",
        }
    )

    period_performance_grouped = period_performance_grouped.round(2)

    period_performance_grouped["Invested Amount"] = (
        period_performance_grouped[volume_column]
        * period_performance_grouped[price_column]
        + abs(period_performance_grouped[costs_column])
    ).round(2)

    last_prices = []
    last_benchmark_prices = []

    for period, _ in period_performance_grouped.iterrows():
        last_prices.append(period_prices.loc[period[0], period[1]])

        original_ticker = original_ticker_combinations[period[1]]
        benchmark_ticker = benchmark_per_ticker[original_ticker]

        last_benchmark_prices.append(
            benchmark_period_prices.loc[period[0], benchmark_ticker]
        )

    period_performance_grouped["Current Value"] = (
        period_performance_grouped[volume_column] * last_prices
    ).round(2)

    period_performance_grouped["Return"] = (
        period_performance_grouped["Current Value"]
        / period_performance_grouped["Invested Amount"]
        - 1
    ).round(4)

    total_benchmark_invested = (
        period_performance_grouped[volume_column]
        * period_performance_grouped["Benchmark Price"]
    ).round(2)
    end_of_period_benchmark_value = (
        period_performance_grouped[volume_column] * last_benchmark_prices
    ).round(2)

    period_performance_grouped["Benchmark Return"] = (
        end_of_period_benchmark_value / total_benchmark_invested - 1
    ).round(4)

    period_performance_grouped["Alpha"] = (
        period_performance_grouped["Return"]
        - period_performance_grouped["Benchmark Return"]
    ).round(4)

    # Dropping Benchmark Prices since it has no meaning in the current layout
    period_performance_grouped = period_performance_grouped.drop(
        "Benchmark Price", axis=1
    )

    return period_performance_grouped


def create_positions_overview(
    portfolio_tickers: list[str],
    period_dates: pd.DatetimeIndex,
    portfolio_dataset: pd.DataFrame,
    historical_prices: pd.Series,
    columns: list[str] | None = None,
):
    """
    Calculate an overview of portfolio positions and related metrics.

    This function calculates an overview of the portfolio's positions, including
    key statistics and performance metrics. It returns a DataFrame summarizing these
    metrics.

    Args:
        portfolio_tickers (list[str]): A list of tickers representing assets in the portfolio.
        period_dates (pd.DatetimeIndex): A datetime index representing the dates for which
            position metrics should be calculated.
        portfolio_dataset (pd.DataFrame): The dataset containing portfolio positions,
            typically with columns like 'Volume', 'Costs', 'Invested Amount', and others.
        historical_prices (pd.Series): A Series containing historical prices, often
            used for calculating the 'Current Value' of positions.
        columns (list[str] | None, optional): A list of columns to consider when calculating
            positions overview metrics. Defaults to None, which includes ['Volume', 'Costs',
            'Invested Amount'].

    Returns:
        pd.DataFrame: A DataFrame containing an overview of portfolio positions and related metrics.

    Notes:
        The function calculates various position metrics such as 'Current Value', 'Cumulative Return',
        'Invested Weight', and 'Current Weight' for each asset in the portfolio.
    """
    if not columns:
        columns = ["Volume", "Costs", "Invested Amount"]

    positions = {}
    for column in columns:
        positions[column] = pd.DataFrame(index=period_dates, columns=portfolio_tickers)

        for ticker in portfolio_tickers:
            positions[column].loc[:, ticker] = (
                portfolio_dataset.loc[:, ticker, :][column].groupby(level=0).sum()
            )

        positions[column] = positions[column].fillna(0).cumsum()

    positions["Current Value"] = positions["Volume"] * historical_prices["Adj Close"]
    positions["Cumulative Return"] = (
        positions["Current Value"] / positions["Invested Amount"]
    )
    positions["Invested Weight"] = positions["Invested Amount"].div(
        positions["Invested Amount"].sum(axis=1), axis=0
    )
    positions["Current Weight"] = positions["Current Value"].div(
        positions["Current Value"].sum(axis=1), axis=0
    )

    positions_df = pd.concat(positions, axis=1).fillna(0)

    positions_df = positions_df.round(2)

    return positions_df


def create_portfolio_performance(
    positions_dataset: pd.DataFrame,
    date_column: str,
    ticker_column: str,
    period_string: str,
):
    """
    Calculate portfolio performance metrics based on positions dataset.

    This function calculates various portfolio performance metrics, such as returns,
    for the specified period using the provided positions dataset. It aggregates
    and calculates metrics for each date and ticker combination.

    Args:
        positions_dataset (pd.DataFrame): The dataset containing portfolio positions,
            typically with columns like 'Volume', 'Costs', 'Invested Amount', 'Current Value',
            'Invested Weight', and 'Current Weight'.
        date_column (str): The name of the column in positions_dataset that represents dates.
        ticker_column (str): The name of the column in positions_dataset that represents tickers.
        period_string (str): The time period for which portfolio performance metrics
            should be calculated. This can be 'yearly', 'quarterly', 'monthly', 'weekly', or 'daily'.

    Returns:
        pd.DataFrame: A DataFrame containing portfolio performance metrics aggregated by date and ticker.

    Raises:
        ValueError: If an invalid or unsupported period_string is provided.
    """
    positions_dataset_stacked = positions_dataset.melt()
    positions_dataset_stacked.index.names = [date_column, ticker_column]

    dates = positions_dataset_stacked.index.get_level_values(date_column).asfreq(
        period_string
    )
    tickers = positions_dataset_stacked.index.get_level_values(ticker_column)

    positions_dataset_grouped = positions_dataset_stacked.groupby(
        [dates, tickers], observed=True
    ).agg(
        {
            "Volume": "last",
            "Costs": "last",
            "Invested Amount": "last",
            "Current Value": "last",
            "Invested Weight": "last",
            "Current Weight": "last",
        }
    )

    positions_dataset_grouped["Return"] = (
        positions_dataset_grouped["Current Value"]
        / positions_dataset_grouped["Invested Amount"]
        - 1
    )

    positions_dataset_grouped = positions_dataset_grouped.round(2)

    return positions_dataset_grouped
