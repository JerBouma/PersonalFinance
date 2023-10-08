"""Portfolio Module"""

import pandas as pd
from financetoolkit import Toolkit

from financeportfolio import helpers
from financeportfolio.portfolio import excel_model, portfolio_model

# pylint: disable=too-many-instance-attributes,abstract-class-instantiated,
# pylint: disable=too-few-public-methods,protected-access,too-many-lines


class Portfolio:
    """
    A class for managing and analyzing your portfolio.

    This class provides functionality for loading, preprocessing, categorizing, and analyzing
    cash flow data based on a specified configuration file. It offers methods to read and format
    the dataset, apply cost or income indicators, categorize transactions, and create periodical
    cash flow overviews.

    Parameters:
        configuration_file (str): The file path to the configuration file in YAML format. The
            configuration file should define various settings and columns used in cash flow
            analysis.

    Attributes:
        _configuration_file (str): The file path to the configuration file.
        _cash_flow_dataset (pd.DataFrame): The cash flow dataset as a pandas DataFrame.

    Note:
        - The configuration file should be in YAML format and contain settings for date columns,
          description columns, amount columns, and optionally cost/income columns.
        - Initialize an instance of this class to begin cash flow analysis.
    """

    def __init__(
        self,
        configuration_file: str,
        portfolio_dataset: pd.DataFrame = pd.DataFrame(),
    ):
        """
        Initialize a Cashflow instance with the provided configuration file.

        This constructor sets up the Cashflow instance by loading the configuration file, defining
        default attributes, and initializing the cash flow dataset as an empty DataFrame.

        Parameters:
            configuration_file (str): The file path to the configuration file in YAML format.

        Raises:
            ValueError: If the provided configuration file does not have a '.yaml' extension.
                Only '.yaml' configuration files are supported.
        """
        self._configuration_file = configuration_file
        self._custom_dataset = portfolio_dataset
        self._yearly_overview: pd.DataFrame = pd.DataFrame()
        self._quarterly_overview: pd.DataFrame = pd.DataFrame()
        self._monthly_overview: pd.DataFrame = pd.DataFrame()
        self._yearly_cash_flow_dataset: pd.DataFrame = pd.DataFrame()
        self._quarterly_cash_flow_dataset: pd.DataFrame = pd.DataFrame()
        self._monthly_cash_flow_dataset: pd.DataFrame = pd.DataFrame()

        # Tickers
        self._ticker_combinations: dict[str, str] = {}
        self._original_ticker_combinations: dict[str, str] = {}

        # Historical Data
        self._daily_historical_data: pd.DataFrame = pd.DataFrame()
        self._weekly_historical_data: pd.DataFrame = pd.DataFrame()
        self._monthly_historical_data: pd.DataFrame = pd.DataFrame()
        self._quarterly_historical_data: pd.DataFrame = pd.DataFrame()
        self._yearly_historical_data: pd.DataFrame = pd.DataFrame()
        self._historical_statistics: pd.DataFrame = pd.DataFrame()

        # Benchmark Historical Data
        self._benchmark_tickers: dict[str, str] = {}
        self._daily_benchmark_data: pd.DataFrame = pd.DataFrame()
        self._weekly_benchmark_data: pd.DataFrame = pd.DataFrame()
        self._monthly_benchmark_data: pd.DataFrame = pd.DataFrame()
        self._quarterly_benchmark_data: pd.DataFrame = pd.DataFrame()
        self._yearly_benchmark_data: pd.DataFrame = pd.DataFrame()
        self._benchmark_prices: pd.DataFrame = pd.DataFrame()
        self._benchmark_specific_prices: pd.Series = pd.Series()
        self._benchmark_prices_per_ticker: pd.DataFrame = pd.DataFrame()
        self._latest_benchmark_price: pd.Series = pd.Series()

        # Portfolio Overveiw
        self._portfolio_overview: pd.DataFrame = pd.DataFrame()
        self._portfolio_performance: pd.DataFrame = pd.DataFrame()
        self._transactions_performance: pd.DataFrame = pd.DataFrame()
        self._portfolio_dataset: pd.DataFrame = pd.DataFrame()
        self._positions_overview: pd.DataFrame = pd.DataFrame()
        self._transactions_overview: pd.DataFrame = pd.DataFrame()

        # Finance Toolkit Initialization
        self._toolkit: Toolkit | None = None
        self._benchmark_toolkit: Toolkit | None = None
        self._currency_toolkit: Toolkit | None = None
        self._latest_price: pd.Series = pd.Series()
        self._daily_currency_data: pd.DataFrame = pd.DataFrame()

        if self._configuration_file.endswith(".yaml"):
            self._cfg: dict[str, dict] = helpers.read_yaml_file(
                location=self._configuration_file
            )
        else:
            raise ValueError("File type not supported. Please use .yaml")

        # Column Names
        self._date_column: str = self._cfg["general"]["date_columns"]
        self._name_column: str = self._cfg["general"]["name_columns"]
        self._ticker_column: str = self._cfg["general"]["ticker_columns"]
        self._price_column: str = self._cfg["general"]["price_columns"]
        self._volume_column: str = self._cfg["general"]["volume_columns"]
        self._costs_column: str = self._cfg["general"]["costs_columns"]

        self.read_portfolio_dataset()

    def read_portfolio_dataset(
        self,
        excel_location: str | list | None = None,
        adjust_duplicates: bool | None = None,
        date_column: list[str] | None = None,
        date_format: str | None = None,
        name_columns: list[str] | None = None,
        ticker_columns: list[str] | None = None,
        price_columns: list[str] | None = None,
        volume_columns: list[str] | None = None,
        currency_columns: list[str] | None = None,
        costs_columns: list[str] | None = None,
        column_mapping: dict[str, str] | None = None,
    ):
        """
        Read and consolidate cash flow data from Excel or CSV files into a single DataFrame.

        This function reads cash flow data from one or more Excel or CSV files specified by the
        'excel_location' parameter. It can accept a single file path as a string or a list of file
        paths. If 'excel_location' is not provided, it will use the default file location from the
        configuration ('self._cfg["general"]["file_location"]').

        The function identifies additional files within directories specified in 'excel_location'
        and includes them in the data consolidation. It supports Excel (.xlsx) and CSV (.csv) file
        formats.

        If the cash flow dataset is initially empty, it reads and consolidates the data, performs
        optional adjustments for duplicated rows, and sets column names to lowercase. The resulting
        dataset is sorted by index in descending order and has its index converted to daily frequency
        ('D').

        Next to that, this function performs various formatting and preprocessing steps to ensure
        data consistency and facilitate analysis. It includes options to customize column names
        for dates, descriptions, amounts, and cost/income categories.

        Parameters:
            excel_location (str | list | None): A file path or a list of file paths to Excel or CSV
                files containing cash flow data. If None, the default file location from the
                configuration is used.

            adjust_duplicates (bool | None): A boolean value indicating whether to adjust duplicated
                rows in the dataset. If None, it defaults to the value specified in the configuration
                ('self._cfg["general"]["adjust_duplicates"]').

            date_column (list[str] | None): A list of column names representing date information
                in the dataset. If None, it defaults to the date columns specified in the
                configuration ('self._cfg["general"]["date_columns"]').

            date_format (str | None): A string representing the date format in the dataset. If None,
                it defaults to the date format specified in the configuration ('self._cfg["general"]["date_format"]').

            description_columns (list[str] | None): A list of column names representing
                transaction descriptions in the dataset. If None, it defaults to the description
                columns specified in the configuration ('self._cfg["general"]["description_columns"]').

            amount_column (list[str] | None): A list of column names representing transaction
                amounts in the dataset. If None, it defaults to the amount columns specified in
                the configuration ('self._cfg["general"]["amount_columns"]').

            cost_or_income_column (list[str] | None): A list of column names representing
                cost or income categories in the dataset. If None, it defaults to the cost/income
                columns specified in the configuration ('self._cfg["general"]["cost_or_income_columns"]').

            decimal_seperator (str | None): A string representing the decimal separator used in
                the dataset. If None, it defaults to the decimal separator specified in the
                configuration ('self._cfg["general"]["decimal_seperator"]').

        Returns:
            pd.DataFrame: A DataFrame containing the consolidated cash flow data.

        Raises:
            FileNotFoundError: If any of the specified files or directories in 'excel_location'
                cannot be found.
            ValueError: If essential columns (date, description, amount) are not found in the dataset.
                - For missing columns, specify them in the configuration or provide them explicitly.
                - For cost or income columns, raise an exception if not found and configuration is empty.

        Note:
            - Duplicates in individual datasets are adjusted based on configuration settings
            ('self._cfg["general"]["adjust_duplicates"]').
            - If duplicates are found in the combination of datasets, they are removed to prevent
            double-counting.
            - The function handles formatting of date columns, converting them to datetime objects.
            - Transaction description columns are converted to categorical data.
            - Transaction amount columns are converted to float, with support for different decimal separators.
            - Cost or income columns are converted to categorical data, with optional customization.
        """

        date_column = (
            date_column if date_column else self._cfg["general"]["date_columns"]
        )
        date_format = (
            date_format if date_format else self._cfg["general"]["date_format"]
        )
        name_columns = (
            name_columns if name_columns else self._cfg["general"]["name_columns"]
        )
        ticker_columns = (
            ticker_columns if ticker_columns else self._cfg["general"]["ticker_columns"]
        )

        price_columns = (
            price_columns if price_columns else self._cfg["general"]["price_columns"]
        )

        volume_columns = (
            volume_columns if volume_columns else self._cfg["general"]["volume_columns"]
        )

        currency_columns = (
            currency_columns
            if currency_columns
            else self._cfg["adjustments"]["currency_columns"]
        )

        costs_columns = (
            costs_columns if costs_columns else self._cfg["general"]["costs_columns"]
        )

        column_mapping = (
            column_mapping if column_mapping else self._cfg["general"]["column_mapping"]
        )

        if self._portfolio_dataset.empty:
            if not self._custom_dataset.empty:
                (
                    self._portfolio_dataset,
                    self._date_column,
                    self._name_column,
                    self._ticker_column,
                    self._price_column,
                    self._volume_column,
                    self._currency_column,
                    self._costs_column,
                ) = portfolio_model.format_portfolio_dataset(
                    dataset=self._portfolio_dataset,
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

            else:
                excel_location = (
                    excel_location
                    if excel_location
                    else self._cfg["general"]["file_location"]
                )

                if isinstance(excel_location, str):
                    excel_location = [excel_location]

                adjust_duplicates = (
                    adjust_duplicates
                    if adjust_duplicates
                    else self._cfg["general"]["adjust_duplicates"]
                )
                (
                    self._portfolio_dataset,
                    self._date_column,
                    self._name_column,
                    self._ticker_column,
                    self._price_column,
                    self._volume_column,
                    self._currency_column,
                    self._costs_column,
                ) = portfolio_model.read_portfolio_dataset(  # type: ignore
                    excel_location=excel_location,
                    adjust_duplicates=adjust_duplicates,
                    date_column=date_column,
                    date_format=date_format,
                    name_columns=name_columns,
                    ticker_columns=ticker_columns,
                    price_columns=price_columns,
                    volume_columns=volume_columns,
                    currency_columns=currency_columns,
                    costs_columns=costs_columns,
                    column_mapping=column_mapping,
                )

            self._original_tickers = list(
                self._portfolio_dataset[self._ticker_column].unique()
            )

            if self._cfg["adjustments"]["isin_to_ticker"]:
                self._portfolio_dataset = self._portfolio_dataset.replace(
                    self._cfg["adjustments"]["isin_to_ticker"]
                )

            self._portfolio_dataset = self._portfolio_dataset.sort_values(
                by=self._date_column, ascending=True
            )
            self._tickers = list(self._portfolio_dataset[self._ticker_column].unique())
            self._start_date = (
                self._portfolio_dataset[self._date_column].min().strftime("%Y-%m-%d")
            )
            self._transactions_currencies = list(
                self._portfolio_dataset[self._currency_column].unique()  # type: ignore
            )

            self._portfolio_dataset = self._portfolio_dataset.set_index(
                [self._date_column, self._ticker_column]
            )

        return self._portfolio_dataset

    def collect_benchmark_historical_data(
        self,
        benchmark_ticker: str | None = None,
        benchmark_per_ticker: dict[str, str] | None = None,
    ):
        """
        Collect historical benchmark data for the portfolio.

        This method retrieves historical benchmark data, such as daily, weekly, monthly, quarterly,
        and yearly prices, for the specified benchmark ticker or per-ticker mapping. It matches the
        benchmark data to the dates of the portfolio's historical data.

        Args:
            benchmark_ticker (str | None): The benchmark ticker symbol to use if no per-ticker mapping
                is provided. If None, the default benchmark ticker from the configuration is used.
            benchmark_per_ticker (dict[str, str] | None): A dictionary that maps original portfolio
                tickers to their corresponding benchmark tickers. If not provided, it defaults to the
                mapping specified in the configuration.

        Returns:
            DataFrame: A DataFrame containing the historical benchmark data.
        """
        if self._daily_historical_data.empty:
            self.collect_historical_data()

        benchmark_ticker = (
            benchmark_ticker
            if benchmark_ticker
            else self._cfg["general"]["benchmark_ticker"]
        )

        benchmark_per_ticker = (
            benchmark_per_ticker
            if benchmark_per_ticker
            else self._cfg["general"]["benchmark_per_ticker"]
        )

        if not self._benchmark_toolkit:
            self._benchmark_tickers = {}
            for ticker in self._original_tickers:
                self._benchmark_tickers[ticker] = benchmark_per_ticker.get(
                    ticker, benchmark_ticker
                )

            self._benchmark_toolkit = Toolkit(
                tickers=list(set(self._benchmark_tickers.values())),
                benchmark_ticker=None,
                start_date=self._start_date,
            )

        # Reindex the benchmark data to the dates of the historical dataset so that they are matched up.
        self._daily_benchmark_data = self._benchmark_toolkit.get_historical_data(
            period="daily"
        ).reindex(self._daily_historical_data.index, method="backfill")

        self._weekly_benchmark_data = self._benchmark_toolkit.get_historical_data(
            period="weekly"
        )
        self._monthly_benchmark_data = self._benchmark_toolkit.get_historical_data(
            period="monthly"
        )
        self._quarterly_benchmark_data = self._benchmark_toolkit.get_historical_data(
            period="quarterly"
        )
        self._yearly_benchmark_data = self._benchmark_toolkit.get_historical_data(
            period="yearly"
        )

        # It could be that a specific date does not exist for the given benchmark. In that case,
        # the previous value is used instead.
        self._benchmark_prices = self._daily_benchmark_data["Adj Close"].iloc[
            self._daily_benchmark_data["Adj Close"].index.get_indexer(
                self._portfolio_dataset.index.get_level_values(0), method="backfill"
            )
        ]

        # The index of the benchmark prices is set to the dates of the portfolio dataset
        # so that they are matched up again.
        self._benchmark_prices = self._benchmark_prices.set_index(
            self._portfolio_dataset.index
        )

        self._benchmark_prices = self._benchmark_prices.sort_index()

        benchmark_specific_prices = []
        benchmark_latest_price = {}
        benchmark_prices_per_ticker = pd.DataFrame(
            columns=self._tickers, index=self._daily_benchmark_data.index
        )

        for (date, ticker), _ in self._portfolio_dataset.iterrows():
            original_ticker = self._original_ticker_combinations[ticker]
            benchmark_ticker = self._benchmark_tickers[original_ticker]

            # Add the specific benchmark price and, if multiple orders of the same ticker are made on the same day
            # (e.g. buying and selling), only report the benchmark price once.
            benchmark_specific_prices.append(
                self._benchmark_prices.loc[
                    (date, ticker), benchmark_ticker
                ].drop_duplicates()
            )

            benchmark_latest_price[ticker] = self._daily_benchmark_data["Adj Close"][
                benchmark_ticker
            ].iloc[-1]
            benchmark_prices_per_ticker[ticker] = self._daily_benchmark_data[
                "Adj Close"
            ][benchmark_ticker]

        self._benchmark_specific_prices = pd.concat(benchmark_specific_prices)
        self._latest_benchmark_price = pd.Series(benchmark_latest_price)
        self._benchmark_prices_per_ticker = benchmark_prices_per_ticker

        return self._daily_benchmark_data

    def collect_historical_data(
        self,
        historical_columns: list[str] | None = None,
        isin_to_ticker: dict[str, str] | None = None,
    ):
        """
        Collect historical price and currency adjustment data.

        This method retrieves historical price data for the portfolio's tickers and performs
        currency adjustments if necessary. It collects daily, weekly, monthly, quarterly, and
        yearly price data and stores it in separate DataFrames.

        Args:
            historical_columns (list[str] | None): A list of column names representing historical price data.
                If None, it defaults to the columns specified in the configuration
                ('self._cfg["adjustments"]["currency_adjustment_columns"]').
            isin_to_ticker (dict[str, str] | None): A dictionary that maps ISIN codes to ticker symbols.
                If provided, ISIN codes in the portfolio dataset will be matched to the corresponding
                tickers. If None, it defaults to the mapping specified in the configuration.

        Returns:
            pd.DataFrame: A DataFrame containing the daily historical price data for the portfolio.

        Note:
            - This method uses the Toolkit class to fetch historical price data from a data source.
            - Currency conversions are performed if there is a mismatch between the currency of transactions
            and the currency of historical data. Currency conversion rates are fetched using the Currency Toolkit.
            - The resulting historical price data is stored in separate DataFrames for different periods.
        """
        historical_columns = (
            historical_columns
            if historical_columns
            else self._cfg["adjustments"]["currency_adjustment_columns"]
        )

        isin_to_ticker = (
            isin_to_ticker
            if isin_to_ticker
            else self._cfg["adjustments"]["isin_to_ticker"]
        )

        if not self._toolkit:
            self._toolkit = Toolkit(
                tickers=self._tickers,
                benchmark_ticker=None,
                start_date=self._start_date,
            )

        # This is used in case ISIN codes are provided and therefore ISIN codes need to
        # be matched to the corresponding tickers
        self._ticker_combinations = dict(zip(self._toolkit._tickers, self._tickers))
        self._original_ticker_combinations = dict(
            zip(self._tickers, self._original_tickers)
        )

        self._daily_historical_data = self._toolkit.get_historical_data(period="daily")

        self._daily_historical_data = self._daily_historical_data.rename(
            columns=self._ticker_combinations, level=1
        )

        currency_conversions = {}
        if self._currency_column:  # type: ignore
            self._historical_statistics = self._toolkit.get_historical_statistics()
            self._historical_statistics = self._historical_statistics.rename(
                columns=self._ticker_combinations, level=0
            )

            for (_, ticker), currency in self._portfolio_dataset[
                self._currency_column  # type: ignore
            ].items():
                data_currency = self._historical_statistics.loc["Currency", ticker]
                if self._historical_statistics.loc["Currency", ticker] != currency:
                    currency_conversions[
                        ticker
                    ] = f"{currency}{data_currency}=X".upper()

        if currency_conversions:
            print(
                "Found a mismatch between the currency of the transaction and the currency of the historical data. "
                "This is usually due to working with ISIN codes.\nConsider filling the 'isin_to_ticker' parameter to "
                "correct this by finding the correct ticker on Yahoo Finance (e.g. VUSA.AS). The currencies are "
                "automatically converted but this does lead to some inaccuracies."
            )
            self._currency_toolkit = Toolkit(
                tickers=list(set(currency_conversions.values())),
                benchmark_ticker=None,
                start_date=self._start_date,
            )

            self._daily_currency_data = self._currency_toolkit.get_historical_data(
                period="daily"
            )

            for ticker, currency in currency_conversions.items():
                for column in historical_columns:
                    self._daily_historical_data.loc[:, (column, ticker)] = (
                        self._daily_historical_data.loc[:, (column, ticker)]
                        / self._daily_currency_data.loc[:, (column, currency)]
                    )

        self._weekly_historical_data = self._toolkit.get_historical_data(
            period="weekly"
        )
        self._weekly_historical_data = self._weekly_historical_data.rename(
            columns=self._ticker_combinations, level=1
        )

        self._monthly_historical_data = self._toolkit.get_historical_data(
            period="monthly"
        )
        self._monthly_historical_data = self._monthly_historical_data.rename(
            columns=self._ticker_combinations, level=1
        )

        self._quarterly_historical_data = self._toolkit.get_historical_data(
            period="quarterly"
        )
        self._quarterly_historical_data = self._quarterly_historical_data.rename(
            columns=self._ticker_combinations, level=1
        )

        self._yearly_historical_data = self._toolkit.get_historical_data(
            period="yearly"
        )
        self._yearly_historical_data = self._yearly_historical_data.rename(
            columns=self._ticker_combinations, level=1
        )

        self._latest_price = self._daily_historical_data["Adj Close"].iloc[-1]

        return self._daily_historical_data

    def get_positions_overview(self):
        """
        Calculate and provide an overview of the portfolio positions.

        This method calculates an overview of the portfolio's positions, including
        key statistics and performance metrics. It returns a DataFrame summarizing these
        metrics.

        If the necessary historical data has not been collected, this method will first
        trigger data collection using the `collect_historical_data` and
        `collect_benchmark_historical_data` methods.

        Returns:
            DataFrame: A DataFrame containing an overview of the portfolio's positions.

        Raises:
            Exception: If data collection for historical or benchmark data fails.
        """
        if self._daily_historical_data.empty:
            try:
                self.collect_historical_data()
            except ValueError as error:
                raise ValueError(
                    f"Failed to collect historical data due to {error}"
                ) from error

        if self._daily_benchmark_data.empty:
            try:
                self.collect_benchmark_historical_data()
            except ValueError as error:
                raise ValueError(
                    f"Failed to collect benchmark historical data due to {error}"
                ) from error

        if self._positions_overview.empty:
            try:
                self._positions_overview = portfolio_model.create_positions_overview(
                    portfolio_tickers=self._tickers,
                    period_dates=self._daily_historical_data.index.get_level_values(0),
                    portfolio_dataset=self._portfolio_dataset,
                    historical_prices=self._daily_historical_data,
                )
            except ValueError as error:
                raise ValueError(
                    f"Failed to create positions overview due to {error}"
                ) from error

        return self._positions_overview

    def get_portfolio_overview(self):
        """
        Calculate and provide an overview of the portfolio's key statistics.

        This method calculates various key statistics for the portfolio, including
        performance metrics and cost-related information. It returns a DataFrame
        summarizing these metrics.

        If the necessary historical data has not been collected, this method will first
        trigger data collection using the `collect_historical_data` and
        `collect_benchmark_historical_data` methods.

        Returns:
            DataFrame: A DataFrame containing key statistics and an overview of the portfolio.

        Raises:
            Exception: If data collection for historical or benchmark data fails.
            Exception: If the creation of portfolio overview fails.
        """
        if self._daily_historical_data.empty:
            try:
                self.collect_historical_data()
            except ValueError as error:
                raise ValueError(
                    f"Failed to collect historical data: {error}"
                ) from error

        if self._daily_benchmark_data.empty:
            try:
                self.collect_benchmark_historical_data()
            except ValueError as error:
                raise ValueError(
                    f"Failed to collect benchmark historical data: {error}"
                ) from error

        if self._portfolio_overview.empty:
            try:
                self._portfolio_overview = portfolio_model.create_portfolio_overview(
                    portfolio_name=self._portfolio_dataset[self._name_column],
                    portfolio_volume=self._portfolio_dataset[self._volume_column],
                    portfolio_price=self._portfolio_dataset[self._price_column],
                    portfolio_costs=self._portfolio_dataset[self._costs_column],
                    latest_returns=self._latest_price,
                    benchmark_prices=self._benchmark_specific_prices,
                    benchmark_latest_prices=self._latest_benchmark_price,
                )
            except ValueError as error:
                raise ValueError(
                    f"Failed to create portfolio overview: {error}"
                ) from error

        return self._portfolio_overview

    def get_portfolio_performance(self, period_string: str | None = None):
        """
        Calculate portfolio performance metrics for a specified period.

        This method calculates various portfolio performance metrics, such as returns,
        for the specified period. It uses the positions overview dataset for these
        calculations.

        Args:
            period_string (str | None): The time period for which portfolio performance
                metrics should be calculated. This can be 'yearly', 'quarterly', 'monthly',
                'weekly', or 'daily'. If None, the default is 'daily'.

        Returns:
            DataFrame: A DataFrame containing portfolio performance metrics.

        Raises:
            ValueError: If an invalid or unsupported period_string is provided.
        """
        if self._daily_historical_data.empty:
            try:
                self.collect_historical_data()
            except ValueError as error:
                raise ValueError(
                    f"Failed to collect historical data: {error}"
                ) from error

        if self._daily_benchmark_data.empty:
            try:
                self.collect_benchmark_historical_data()
            except ValueError as error:
                raise ValueError(
                    f"Failed to collect benchmark historical data: {error}"
                ) from error

        if self._positions_overview.empty:
            try:
                self.get_positions_overview()
            except ValueError as error:
                raise ValueError(
                    f"Failed to get positions overview: {error}"
                ) from error

        if not period_string:
            raise ValueError(
                "Please provide a period. This can be 'yearly', 'quarterly', 'monthly', 'weekly', or 'daily'"
            )

        period_string = period_string.lower()

        if period_string == "yearly":
            period_symbol = "Y"
        elif period_string == "quarterly":
            period_symbol = "Q"
        elif period_string == "monthly":
            period_symbol = "M"
        elif period_string == "weekly":
            period_symbol = "W"
        elif period_string == "daily":
            period_symbol = "D"
        else:
            raise ValueError(
                "Please provide a valid period. This can be 'yearly', 'quarterly', 'monthly', 'weekly', or 'daily'"
            )

        try:
            self._portfolio_performance = portfolio_model.create_portfolio_performance(
                positions_dataset=self._positions_overview,
                date_column=self._date_column,
                ticker_column=self._ticker_column,
                period_string=period_symbol,
            )
        except ValueError as error:
            raise ValueError(
                f"Failed to create portfolio performance: {error}"
            ) from error

        return self._portfolio_performance

    def get_transactions_overview(self):
        """
        Calculate and collect transaction overview ratios based on the provided data.

        This method calculates various transaction overview ratios, such as returns and costs,
        based on the transaction dataset. It adds these ratios as new columns to the
        portfolio dataset.

        Returns:
            DataFrame: The portfolio dataset with added transaction overview ratios.

        Raises:
            ValueError: If there is an issue with collecting historical data or creating the transaction overview.
        """
        if self._daily_historical_data.empty:
            try:
                self.collect_historical_data()
            except ValueError as error:
                raise ValueError(
                    f"Failed to collect historical data: {error}"
                ) from error

        if self._daily_benchmark_data.empty:
            try:
                self.collect_benchmark_historical_data()
            except ValueError as error:
                raise ValueError(
                    f"Failed to collect benchmark historical data: {error}"
                ) from error

        try:
            new_columns = portfolio_model.create_transactions_overview(
                portfolio_volume=self._portfolio_dataset[self._volume_column],
                portfolio_price=self._portfolio_dataset[self._price_column],
                portfolio_costs=self._portfolio_dataset[self._costs_column],
                latest_returns=self._latest_price.loc[self._tickers],
            )
        except ValueError as error:
            raise ValueError(
                f"Failed to create transaction overview: {error}"
            ) from error

        try:
            self._transactions_overview = pd.concat(
                [self._portfolio_dataset, new_columns], axis=1
            )
        except ValueError as error:
            raise ValueError(
                f"Failed to add transaction overview to portfolio dataset: {error}"
            ) from error

        return self._transactions_overview

    def get_transactions_performance(self, period_string: str | None = None):
        """
        Calculate transaction performance metrics for a specified period.

        This method calculates various transaction performance metrics, such as returns,
        costs, and benchmarks, for the specified period. It uses historical price data
        from the corresponding period for these calculations.

        Args:
            period_string (str | None): The time period for which transaction performance
                metrics should be calculated. This can be 'yearly', 'quarterly', 'monthly',
                'weekly', or 'daily'. If None, the default is 'daily'.

        Returns:
            DataFrame: A DataFrame containing transaction performance metrics.

        Raises:
            ValueError: If an invalid or unsupported period_string is provided.
        """
        if self._daily_historical_data.empty:
            try:
                self.collect_historical_data()
            except ValueError as error:
                raise ValueError(
                    f"Failed to collect historical data: {error}"
                ) from error

        if self._daily_benchmark_data.empty:
            try:
                self.collect_benchmark_historical_data()
            except ValueError as error:
                raise ValueError(
                    f"Failed to collect benchmark historical data: {error}"
                ) from error

        if not period_string:
            raise ValueError(
                "Please provide a period. This can be 'yearly', 'quarterly', 'monthly', 'weekly', or 'daily'"
            )

        period_string = period_string.lower()

        if period_string == "yearly":
            historical_dataset = self._yearly_historical_data["Adj Close"]
            benchmark_dataset = self._yearly_benchmark_data["Adj Close"]
            period_symbol = "Y"
        elif period_string == "quarterly":
            historical_dataset = self._quarterly_historical_data["Adj Close"]
            benchmark_dataset = self._quarterly_benchmark_data["Adj Close"]
            period_symbol = "Q"
        elif period_string == "monthly":
            historical_dataset = self._monthly_historical_data["Adj Close"]
            benchmark_dataset = self._monthly_benchmark_data["Adj Close"]
            period_symbol = "M"
        elif period_string == "weekly":
            historical_dataset = self._weekly_historical_data["Adj Close"]
            benchmark_dataset = self._weekly_benchmark_data["Adj Close"]
            period_symbol = "W"
        elif period_string == "daily":
            historical_dataset = self._daily_historical_data["Adj Close"]
            benchmark_dataset = self._daily_benchmark_data["Adj Close"]
            period_symbol = "D"
        else:
            raise ValueError(
                "Please provide a valid period. This can be "
                "'yearly', 'quarterly', 'monthly', 'weekly', "
                "or 'daily'"
            )

        try:
            self._transactions_performance = (
                portfolio_model.create_transactions_performance(
                    portfolio_dataset=self._portfolio_dataset,
                    ticker_column=self._ticker_column,
                    date_column=self._date_column,
                    volume_column=self._volume_column,
                    price_column=self._price_column,
                    costs_column=self._costs_column,
                    period_prices=historical_dataset,
                    period_string=period_symbol,
                    original_ticker_combinations=self._original_ticker_combinations,
                    benchmark_per_ticker=self._benchmark_tickers,
                    benchmark_specific_prices=self._benchmark_specific_prices,
                    benchmark_period_prices=benchmark_dataset,
                )
            )
        except ValueError as error:
            raise ValueError(
                f"Failed to create transaction performance metrics: {error}"
            ) from error

        return self._transactions_performance

    def create_excel_report(
        self,
        excel_file_name: str | None = None,
        currency: str | None = None,
    ):
        """
        Create an Excel report file with specified data sheets.

        This function creates an Excel file with multiple data sheets, including monthly,
        quarterly, and yearly overviews if the corresponding data is available. The data
        sheets are populated with dataframes provided by the class attributes
        _monthly_overview, _quarterly_overview, and _yearly_overview.

        The Excel file is saved with the specified name or the default name from the
        configuration. The date and datetime formats in the Excel file are set to
        "yyyy-mm-dd" for consistency.

        Args:
            excel_file_name (str | None): The name of the Excel file to be created. If None,
                the default file name specified in the configuration will be used.
            currency (str | None): The currency to be used for formatting in the Excel file.
                If None, the default currency from the configuration will be used.
        """
        excel_file_name = (
            excel_file_name if excel_file_name else self._cfg["excel"]["file_name"]
        )

        currency = currency if currency else self._cfg["excel"]["currency"]

        writer = pd.ExcelWriter(
            excel_file_name,
            engine="xlsxwriter",
            date_format="yyyy-mm-dd",
            datetime_format="yyyy-mm-dd",
        )

        try:
            # Try to create and save Portfolio Overview
            self._portfolio_overview = self.get_portfolio_overview()
            excel_model.create_portfolio_overview_excel_report(
                writer,
                dataset=self._portfolio_overview,
                sheet_name="Portfolio Overview",
                currency=currency,
            )

        except ValueError as error:
            print(f"Error occurred while creating Portfolio Overview sheet: {error}")

        try:
            # Try to create and save Portfolio Performance Overviews
            portfolio_performance_overviews = [
                portfolio_overview.lower()
                for portfolio_overview in self._cfg["excel"][
                    "portfolio_performance_overviews"
                ]
            ]

            for portfolio_overview in portfolio_performance_overviews:
                period_data = self.get_portfolio_performance(
                    period_string=portfolio_overview
                )
                sheet_name = f"{portfolio_overview.capitalize()} Portfolio Overview"
                excel_model.create_portfolio_performance_excel_report(
                    writer,
                    dataset=period_data,
                    sheet_name=sheet_name,
                    currency=currency,
                )

        except ValueError as error:
            print(
                f"Error occurred while creating Portfolio Performance sheets: {error}"
            )

        try:
            # Try to create and save Transactions Performance Overviews
            transactions_performance_overviews = [
                transactions_overview.lower()
                for transactions_overview in self._cfg["excel"][
                    "transactions_overviews"
                ]
            ]

            for transactions_overview in transactions_performance_overviews:
                period_data = self.get_transactions_performance(
                    period_string=transactions_overview
                )
                sheet_name = (
                    f"{transactions_overview.capitalize()} Transactions Overview"
                )
                excel_model.create_transactions_performance_excel_report(
                    writer,
                    dataset=period_data,
                    sheet_name=sheet_name,
                    currency=currency,
                )

        except ValueError as error:
            print(
                f"Error occurred while creating Transactions Performance sheets: {error}"
            )

        try:
            # Try to create and save Positions Overview
            self._positions_overview = self.get_positions_overview()
            excel_model.create_positions_overview_excel_report(
                writer,
                dataset=self._positions_overview,
                sheet_name="Positions Overview",
                currency=currency,
            )

        except ValueError as error:
            print(f"Error occurred while creating Positions Overview sheet: {error}")

        writer.close()
        print(f"Excel report saved as {excel_file_name}")
