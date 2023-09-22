"""Portfolio Module"""

import pandas as pd

from personalfinance import helpers, portfolio_model

# pylint: disable=too-many-instance-attributes,abstract-class-instantiated,too-few-public-methods


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
        custom_dataset: pd.DataFrame = pd.DataFrame(),
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
        self._portfolio_dataset: pd.DataFrame = pd.DataFrame()
        self._custom_dataset = custom_dataset
        self._yearly_overview: pd.DataFrame = pd.DataFrame()
        self._quarterly_overview: pd.DataFrame = pd.DataFrame()
        self._monthly_overview: pd.DataFrame = pd.DataFrame()
        self._yearly_cash_flow_dataset: pd.DataFrame = pd.DataFrame()
        self._quarterly_cash_flow_dataset: pd.DataFrame = pd.DataFrame()
        self._monthly_cash_flow_dataset: pd.DataFrame = pd.DataFrame()
        self._highest_match_percentage: pd.Series = pd.Series()
        self._cost_or_income_criteria: dict = {}

        if self._configuration_file.endswith(".yaml"):
            self._cfg: dict[str, dict] = helpers.read_yaml_file(
                location=self._configuration_file
            )
        else:
            raise ValueError("File type not supported. Please use .yaml")

        self._date_column: str | None = self._cfg["general"]["date_columns"]
        self._name_column: list[str] | None = self._cfg["general"]["name_columns"]
        self._ticker_column: str | None = self._cfg["general"]["ticker_columns"]
        self._price_column: str | None = self._cfg["general"]["price_columns"]
        self._volume_column: str | None = self._cfg["general"]["volume_columns"]
        self._costs_column: str | None = self._cfg["general"]["costs_columns"]

    # def perform_analysis(self) -> pd.DataFrame:
    #     """
    #     Perform comprehensive cash flow analysis.

    #     This function orchestrates a series of data processing steps to perform a comprehensive cash
    #     flow analysis. It performs the following tasks:

    #         1. Reads the cash flow dataset using the 'read_cashflow_dataset' function.
    #         2. Applies cost or income indicators to transaction amounts if specified in the configuration
    #         using the 'apply_cost_or_income_indicator' function.
    #         3. Applies categorization rules to categorize transactions using the 'apply_categorization'
    #         function.
    #         4. Groups transactions by yearly, quarterly, and monthly time periods using the
    #         'group_transactions_by_periods' function.
    #         5. Creates yearly, quarterly, and monthly cash flow overviews using the 'create_period_overviews'
    #         function.

    #     Returns:
    #         pd.DataFrame: The processed cash flow dataset.

    #     Note:
    #         - Ensure that the necessary configuration and dataset have been loaded or specified before
    #         running this function.
    #         - The resulting cash flow dataset can be accessed via the 'self._cash_flow_dataset' attribute.
    #     """
    #     self.read_cashflow_dataset()

    #     if self._custom_dataset.empty:
    #         if self._cfg["general"]["cost_or_income_columns"]:
    #             self.apply_cost_or_income_indicator()

    #         self.apply_categorization()
    #     else:
    #         print("Categorized dataset provided. Skipping categorization.")
    #         self._cash_flow_dataset = self._custom_dataset

    #     self.group_transactions_by_periods()

    #     self._yearly_overview = self.create_period_overviews(period="year")
    #     self._quarterly_overview = self.create_period_overviews(period="quarter")
    #     self._monthly_overview = self.create_period_overviews(period="month")

    #     return self._cash_flow_dataset

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
        costs_columns: list[str] | None = None,
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
        excel_location = (
            excel_location if excel_location else self._cfg["general"]["file_location"]
        )

        adjust_duplicates = (
            adjust_duplicates
            if adjust_duplicates
            else self._cfg["general"]["adjust_duplicates"]
        )

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

        costs_columns = (
            costs_columns if costs_columns else self._cfg["general"]["costs_columns"]
        )

        if isinstance(excel_location, str):
            excel_location = [excel_location]

        if self._portfolio_dataset.empty:
            (
                self._portfolio_dataset,
                self._date_column,
                self._name_column,
                self._ticker_column,
                self._price_column,
                self._volume_column,
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
                costs_columns=costs_columns,
            )

        return self._portfolio_dataset
