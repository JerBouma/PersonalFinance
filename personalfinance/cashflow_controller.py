"""Cashflow Module"""

import pandas as pd

from personalfinance import cashflow_model, excel_model, helpers

# pylint: disable=too-many-instance-attributes,abstract-class-instantiated


class Cashflow:
    """
    A class for managing and analyzing cash flow data.

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
        self._cash_flow_dataset: pd.DataFrame = pd.DataFrame()
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
        self._description_columns: list[str] | None = self._cfg["general"][
            "description_columns"
        ]
        self._amount_column: str | None = self._cfg["general"]["amount_columns"]
        self._cost_or_income_column: str | None = self._cfg["general"][
            "cost_or_income_columns"
        ]

    def perform_analysis(self) -> pd.DataFrame:
        """
        Perform comprehensive cash flow analysis.

        This function orchestrates a series of data processing steps to perform a comprehensive cash
        flow analysis. It performs the following tasks:

            1. Reads the cash flow dataset using the 'read_cashflow_dataset' function.
            2. Applies cost or income indicators to transaction amounts if specified in the configuration
            using the 'apply_cost_or_income_indicator' function.
            3. Applies categorization rules to categorize transactions using the 'apply_categorization'
            function.
            4. Groups transactions by yearly, quarterly, and monthly time periods using the
            'group_transactions_by_periods' function.
            5. Creates yearly, quarterly, and monthly cash flow overviews using the 'create_period_overviews'
            function.

        Returns:
            pd.DataFrame: The processed cash flow dataset.

        Note:
            - Ensure that the necessary configuration and dataset have been loaded or specified before
            running this function.
            - The resulting cash flow dataset can be accessed via the 'self._cash_flow_dataset' attribute.
        """
        self.read_cashflow_dataset()

        if self._custom_dataset.empty:
            if self._cfg["general"]["cost_or_income_columns"]:
                self.apply_cost_or_income_indicator()

            self.apply_categorization()
        else:
            print("Categorized dataset provided. Skipping categorization.")
            self._cash_flow_dataset = self._custom_dataset

        self.group_transactions_by_periods()

        self._yearly_overview = self.create_period_overviews(period="year")
        self._quarterly_overview = self.create_period_overviews(period="quarter")
        self._monthly_overview = self.create_period_overviews(period="month")

        return self._cash_flow_dataset

    def read_cashflow_dataset(
        self,
        excel_location: str | list | None = None,
        adjust_duplicates: bool | None = None,
        date_column: list[str] | None = None,
        date_format: str | None = None,
        description_columns: list[str] | None = None,
        amount_column: list[str] | None = None,
        cost_or_income_dict: dict | None = None,
        decimal_seperator: str | None = None,
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
        description_columns = (
            description_columns
            if description_columns
            else self._cfg["general"]["description_columns"]
        )
        amount_column = (
            amount_column if amount_column else self._cfg["general"]["amount_columns"]
        )
        cost_or_income_dict = (
            cost_or_income_dict
            if cost_or_income_dict
            else self._cfg["general"]["cost_or_income_columns"]
        )
        decimal_seperator = (
            decimal_seperator
            if decimal_seperator
            else self._cfg["general"]["decimal_separator"]
        )

        if isinstance(excel_location, str):
            excel_location = [excel_location]

        if self._cash_flow_dataset.empty:
            (
                self._cash_flow_dataset,
                self._date_column,
                self._description_columns,
                self._amount_column,
                self._cost_or_income_column,
                self._cost_or_income_criteria,
            ) = cashflow_model.read_cashflow_dataset(  # type: ignore
                excel_location=excel_location,
                adjust_duplicates=adjust_duplicates,
                date_column=date_column,
                date_format=date_format,
                description_columns=description_columns,
                amount_column=amount_column,
                cost_or_income_dict=cost_or_income_dict,
                decimal_seperator=decimal_seperator,
            )

        return self._cash_flow_dataset

    def apply_categorization(
        self,
        categorization: dict[str, list] | None = None,
        description_columns: list[str] | None = None,
        categorization_threshold: int | None = None,
        direct_match: bool | None = None,
    ) -> None:
        """
        Apply categorization to transactions in the cash flow dataset based on provided rules.

        This function categorizes transactions in the cash flow dataset using a set of rules defined
        in the 'categorization' parameter. It matches transaction descriptions with keywords and assigns
        categories accordingly. The categorized results are stored in a new 'category' column in the
        dataset.

        Parameters:
            categorization (dict[str, list] | None): A dictionary of category names as keys and lists
                of keywords as values. If None, it defaults to the categorization rules specified in the
                configuration ('self._cfg["categories"]').

            description_columns (list[str] | None): A list of column names representing transaction
                descriptions in the dataset. If None, it defaults to the description columns specified
                during dataset formatting ('self._description_columns').

            categorization_threshold (int | None): A numeric threshold that determines the level of
                keyword match required for categorization. If None, it defaults to the threshold set in
                the configuration ('self._cfg["general"]["categorization_threshold"]').

        Returns:
            None

        Note:
            - The function iterates through each transaction and checks for keyword matches in the
            description columns.
            - The 'categorized_percentage' represents the percentage of transactions that have been
            successfully categorized.
            - The function also reports unmatched keywords below the threshold if any.

        Raises:
            ValueError: If no description columns are found in the cash flow dataset.
                - Ensure that description columns are defined either in the configuration or explicitly.
        """
        categorization = categorization if categorization else self._cfg["categories"]
        description_columns = (
            description_columns if description_columns else self._description_columns
        )
        categorization_threshold = (
            categorization_threshold
            if categorization_threshold
            else self._cfg["general"]["categorization_threshold"]
        )
        direct_match = (
            direct_match if direct_match else self._cfg["general"]["direct_match"]
        )

        self._cash_flow_dataset, total_matches = cashflow_model.apply_categorization(
            dataset=self._cash_flow_dataset,
            categorization=categorization,
            description_columns=description_columns,
            categorization_threshold=categorization_threshold,
        )

        categorized_percentage = (
            len(self._cash_flow_dataset[self._cash_flow_dataset["category"] != "Other"])
            / len(self._cash_flow_dataset["category"])
        ) * 100

        self._highest_match_percentage = pd.Series(total_matches)

        print(
            f"{categorized_percentage:.2f}% of the cash flow dataset has been categorized."
        )

        if (self._highest_match_percentage < categorization_threshold).any():
            print(
                "The following keywords have not led to any category matches. Please consider "
                "removing or updating these keyword to keep things compact:"
            )
            below_threshold = self._highest_match_percentage[
                self._highest_match_percentage < categorization_threshold
            ].sort_values()

            for keyword, match_percentage in below_threshold.items():
                print(f"{keyword}: {match_percentage:.2f}%")

    def apply_cost_or_income_indicator(
        self,
        cost_or_income_column: str | None = None,
        cost_or_income_criteria: dict[str, int] | None = None,
        amount_column: str | None = None,
    ) -> pd.DataFrame:
        """
        Apply cost or income indicators to transaction amounts based on provided criteria.

        This function applies cost or income indicators to transaction amounts in the cash flow dataset
        based on specified criteria. It multiplies the amounts by corresponding multipliers defined in
        'cost_or_income_criteria' and updates the dataset accordingly.

        Parameters:
            cost_or_income_column (str | None): The column name representing cost or income indicators
                in the cash flow dataset. If None, it defaults to the column specified during dataset
                formatting ('self._cost_or_income_column').

            cost_or_income_criteria (dict[str, int] | None): A dictionary mapping cost or income
                indicators to multiplier values. If None, it defaults to the criteria specified in the
                configuration ('self._cost_or_income_criteria').

            amount_column (str | None): The column name representing transaction amounts in the dataset.
                If None, it defaults to the column specified during dataset formatting ('self._amount_column').

        Returns:
            pd.DataFrame: The cash flow dataset with updated transaction amounts.

        Raises:
            ValueError: If either the cost or income indicator column or the amount column is not found
                in the cash flow dataset.
                - Ensure that these columns are defined either in the configuration or explicitly.
        """
        cost_or_income_column = (
            cost_or_income_column
            if cost_or_income_column
            else self._cost_or_income_column
        )
        cost_or_income_criteria = (
            cost_or_income_criteria
            if cost_or_income_criteria
            else self._cost_or_income_criteria
        )

        amount_column = amount_column if amount_column else self._amount_column

        if not cost_or_income_column:
            print(
                "No cost or income indicator columns found in the cash flow dataset. Please specify "
                "the columns in the configuration file."
            )
        elif not cost_or_income_criteria:
            print(
                "No amount columns found in the cash flow dataset. Please specify the columns in the configuration file."
            )
        else:
            for indicator, multiplier in cost_or_income_criteria.items():
                self._cash_flow_dataset.loc[
                    self._cash_flow_dataset[cost_or_income_column] == indicator,
                    amount_column,
                ] *= multiplier

        return self._cash_flow_dataset

    def group_transactions_by_periods(self) -> None:
        """
        Group transactions in the cash flow dataset by different time periods.

        This function groups transactions in the cash flow dataset by yearly, quarterly, and monthly time
        periods using pandas Grouper. It creates separate datasets for each period and assigns appropriate
        index names to the resulting DataFrames.

        Returns:
            None

        Raises:
            ValueError: If no cash flow dataset is found. You should run the 'read_cashflow_dataset' function
                first to load the dataset.
        """
        if self._cash_flow_dataset.empty:
            raise ValueError(
                "No cash flow dataset found. Please run the 'read_cashflow_dataset' function first."
            )

        self._yearly_cash_flow_dataset = self._cash_flow_dataset.groupby(
            pd.Grouper(freq="Y")
        ).apply(lambda x: x)
        self._quarterly_cash_flow_dataset = self._cash_flow_dataset.groupby(
            pd.Grouper(freq="Q")
        ).apply(lambda x: x)
        self._monthly_cash_flow_dataset = self._cash_flow_dataset.groupby(
            pd.Grouper(freq="M")
        ).apply(lambda x: x)

        self._yearly_cash_flow_dataset.index.names = ["year", "date"]
        self._quarterly_cash_flow_dataset.index.names = ["quarter", "date"]
        self._monthly_cash_flow_dataset.index.names = ["month", "date"]

    def create_period_overviews(self, period: str) -> pd.DataFrame:
        """
        Create periodical cash flow overviews based on the selected time period.

        This function generates cash flow overviews for a specified time period, such as yearly, quarterly,
        or monthly. It uses the grouped cash flow datasets created by the 'group_transactions_by_periods'
        function to calculate aggregated cash flow data for each category within the chosen period.

        Parameters:
            period (str): The time period for which the cash flow overview should be created. Supported
                options are 'year', 'quarter', or 'month'.
            transpose (bool): A boolean value indicating whether to transpose the resulting DataFrame.
                If True, the categories are displayed as columns and the periods as rows. If False, the
                categories are displayed as rows and the periods as columns. Defaults to True.

        Returns:
            pd.DataFrame: A DataFrame containing cash flow overviews for the specified period, with
                categories as rows and periods as columns.

        Raises:
            ValueError: If no period cash flow datasets are found. You should run the
                'group_transactions_by_periods' function first to group the transactions by periods.
            ValueError: If an unsupported 'period' value is provided. Supported values are 'year', 'quarter',
                or 'month'.
        """
        if (
            self._yearly_cash_flow_dataset.empty
            and self._quarterly_cash_flow_dataset.empty
            and self._monthly_cash_flow_dataset.empty
        ):
            raise ValueError(
                "No period cash flow datasets found. Please run the 'group_transactions_by_periods' function first."
            )

        if period == "year":
            period_dataset = self._yearly_cash_flow_dataset
        elif period == "quarter":
            period_dataset = self._quarterly_cash_flow_dataset
        elif period == "month":
            period_dataset = self._monthly_cash_flow_dataset
        else:
            raise ValueError(
                "Period not supported. Please use 'year', 'quarter' or 'month'."
            )

        period_values = period_dataset.index.get_level_values(period).unique()
        categories = self._cfg["categories"].keys()
        period_cash_flows = pd.DataFrame(columns=period_values, index=categories)

        category_exclusions = self._cfg["general"]["category_exclusions"]

        for period_value in period_values:
            period_data = (
                period_dataset.loc[period_value]
                .groupby("category")
                .agg({self._amount_column: "sum"})
            )
            period_data = period_data.reindex(categories).fillna(0)

            period_cash_flows.loc[:, period_value] = period_data.to_numpy()

        period_cash_flows = period_cash_flows.T

        period_cash_flows = period_cash_flows.drop(category_exclusions, axis=1)

        period_cash_flows.insert(0, "Totals", period_cash_flows.sum(axis=1))

        return period_cash_flows

    def create_excel_template(self, excel_file_name: str | None):
        """
        Create an Excel template file with specified data sheets.

        Args:
            excel_file_name (str | None): The name of the Excel file to be created. If None,
                the default file name specified in the configuration will be used.

        Returns:
            None

        Creates an Excel file with multiple data sheets including monthly, quarterly,
        and yearly overviews if the corresponding data is available. The data sheets are
        populated with dataframes provided by the class attributes _monthly_overview,
        _quarterly_overview, and _yearly_overview.

        The Excel file is saved with the specified name or the default name from the
        configuration. The date and datetime formats in the Excel file are set to
        "yyyy-mm-dd" for consistency.

        Example:
            To create an Excel template with a custom name:
            >>> my_instance.create_excel_template("custom_template.xlsx")

            To create an Excel template with the default name from the configuration:
            >>> my_instance.create_excel_template()
        """
        writer = pd.ExcelWriter(
            excel_file_name,
            engine="xlsxwriter",
            date_format="yyyy-mm-dd",
            datetime_format="yyyy-mm-dd",
        )

        if not self._monthly_overview.empty:
            excel_model.create_overview_excel_report(
                writer, dataset=self._monthly_overview, sheet_name="Monthly Overview"
            )
        if not self._quarterly_overview.empty:
            excel_model.create_overview_excel_report(
                writer,
                dataset=self._quarterly_overview,
                sheet_name="Quarterly Overview",
            )
        if not self._yearly_overview.empty:
            excel_model.create_overview_excel_report(
                writer, dataset=self._yearly_overview, sheet_name="Yearly Overview"
            )

        writer.close()
