"""Cashflow Module"""

import os

import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from tqdm import tqdm

from personalfinance import helpers

# pylint: disable=too-many-locals


def read_cashflow_dataset(
    excel_location: list,
    adjust_duplicates: bool,
    date_column: list[str],
    date_format: str,
    description_columns: list[str],
    amount_column: list[str],
    cost_or_income_dict: dict,
    decimal_seperator: str,
) -> tuple[pd.DataFrame, str, list[str], str, str | None, dict | None]:
    """
    Read and preprocess a cash flow dataset from Excel files.

    This function reads one or more Excel files located at 'excel_location' and combines them into
    a single cash flow dataset. It performs formatting and preprocessing tasks on the dataset, including
    renaming columns to lowercase, handling duplicates, and parsing dates. The resulting dataset is returned,
    along with information about column names and processing.

    Parameters:
        excel_location (list): A list of file paths to Excel files containing cash flow data.
        adjust_duplicates (bool): A flag indicating whether to adjust for duplicate entries in the dataset.
        date_column (list[str]): A list of column names representing date information in the dataset.
        date_format (str): The format of date strings in the date column.
        description_columns (list[str]): A list of column names representing transaction descriptions.
        amount_column (list[str]): A list of column names representing transaction amounts.
        cost_or_income_dict (dict): A dictionary mapping cost or income indicators to multiplier values.
        decimal_separator (str): The character used as the decimal separator in numeric values.

    Returns:
        Tuple[pd.DataFrame, str, list[str], str, str | None, dict | None]: A tuple containing the
        processed cash flow dataset as the first element, and the following information:
        - date_column: The name of the selected date column.
        - description_columns: A list of formatted description column names.
        - amount_column: The name of the selected amount column.
        - cost_or_income_column: The name of the cost or income column (if processed).
        - cost_or_income_criteria: A dictionary of criteria for cost or income classification
          (if processed).

    Raises:
        ValueError: If no valid Excel files are found at the specified 'excel_location'.
        ValueError: If no date columns are found in the cash flow dataset. Ensure that date columns
            are defined either in the configuration or explicitly.
        ValueError: If no description columns are found in the cash flow dataset. Ensure that
            description columns are defined either in the configuration or explicitly.
        ValueError: If no amount columns are found in the cash flow dataset. Ensure that amount
            columns are defined either in the configuration or explicitly.
    """
    combined_cash_flow_dataset = pd.DataFrame()
    additional_files = []
    original_excel_location = excel_location.copy()

    for file in excel_location:
        if file.split(".")[-1] not in ["xlsx", "csv"]:
            excel_location.remove(file)

            for sub_file in os.listdir(file):
                if sub_file.endswith(("xlsx", "csv")):
                    additional_files.append(f"{file}/{sub_file}")

    excel_location = excel_location + additional_files

    for file in (
        tqdm(excel_location, desc="Reading Cash Flow Files")
        if len(excel_location) > 1
        else excel_location
    ):
        cash_flow_statement = helpers.read_excel(file)
        cash_flow_statement.columns = cash_flow_statement.columns.str.lower()

        (
            cash_flow_statement,
            selected_date_column,
            selected_description_columns,
            selected_amount_column,
            selected_cost_or_income_column,
            selected_cost_or_income_criteria,
        ) = format_cash_flow_dataset(  # type: ignore
            dataset=cash_flow_statement,
            date_column=date_column,
            date_format=date_format,
            description_columns=description_columns,
            amount_column=amount_column,
            cost_or_income_dict=cost_or_income_dict,
            decimal_seperator=decimal_seperator,
        )

        if cash_flow_statement.duplicated().any() and adjust_duplicates:
            print(f"Found duplicates in {file} These will be added together.")
            duplicates = cash_flow_statement[cash_flow_statement.duplicated()]
            originals = cash_flow_statement[
                cash_flow_statement.duplicated(keep="first")
            ]

            number_columns = duplicates.select_dtypes(np.number).columns.intersection(
                originals.select_dtypes(np.number).columns
            )
            duplicates.loc[:, number_columns] = duplicates.loc[:, number_columns].add(
                originals[number_columns], fill_value=0
            )

            cash_flow_statement = pd.concat(
                [cash_flow_statement, duplicates]
            ).drop_duplicates(keep=False)

        combined_cash_flow_dataset = pd.concat(
            [combined_cash_flow_dataset, cash_flow_statement], axis=0
        )

    if combined_cash_flow_dataset.duplicated().any() and adjust_duplicates:
        if adjust_duplicates:
            print(
                "Found duplicates in the combination of datasets. This is usually due to overlapping periods. "
                "The duplicates will be removed from the datasets to prevent counting the same transaction twice."
            )
            combined_cash_flow_dataset = combined_cash_flow_dataset.drop_duplicates()
        else:
            print(
                "Found duplicates in the combination of datasets. This is usually due to overlapping periods. "
                "Given that adjust_duplicates is set to False these won't be removed. This may result in double "
                "counting transactions."
            )

    if combined_cash_flow_dataset.empty:
        raise ValueError(
            f"No valid Excel files found within the location ({original_excel_location}).\n"
            "Ensure that there are .xlsx or .csv files in the location. Read more about how to do this"
            "in the documentation as found here: https://github.com/JerBouma/PersonalFinance"
        )

    combined_cash_flow_dataset.columns = combined_cash_flow_dataset.columns.str.lower()
    combined_cash_flow_dataset = combined_cash_flow_dataset.sort_index(ascending=False)
    combined_cash_flow_dataset.index = combined_cash_flow_dataset.index.to_period(
        freq="D"
    )

    return (
        combined_cash_flow_dataset,
        selected_date_column,
        selected_description_columns,
        selected_amount_column,
        selected_cost_or_income_column,
        selected_cost_or_income_criteria,
    )


def format_cash_flow_dataset(
    dataset: pd.DataFrame,
    date_column: list[str],
    date_format: str,
    description_columns: list[str],
    amount_column: list[str],
    cost_or_income_dict: dict | None = None,
    decimal_seperator: str | None = None,
) -> tuple[pd.DataFrame, str, list[str], str, str | None, dict]:
    """
    Format and preprocess a cash flow dataset.

    This function takes a raw cash flow dataset and performs formatting and preprocessing tasks
    to prepare it for analysis. It includes actions like setting the date column, converting
    date strings to datetime objects, formatting description columns as categories, and handling
    numeric values, including decimal separators. It also optionally handles cost or income columns
    based on the provided criteria.

    Parameters:
        dataset (pd.DataFrame): The raw cash flow dataset to be formatted.
        date_column (list): A list of column names representing date information in the dataset.
        date_format (str): The format of date strings in the date column.
        description_columns (list): A list of column names representing transaction descriptions.
        amount_column (list): A list of column names representing transaction amounts.
        cost_or_income_dict (dict | None): A dictionary mapping cost or income indicators to
            multiplier values. If None, cost or income columns are not processed.
        decimal_separator (str | None): The character used as the decimal separator in numeric
            values. If None, no decimal separator conversion is performed.

    Returns:
        Tuple[pd.DataFrame, str, list, str, str | None, dict | None]: A tuple containing the
        formatted cash flow dataset as the first element and the following information:
        - date_column: The name of the selected date column.
        - description_columns: A list of formatted description column names.
        - amount_column: The name of the selected amount column.
        - cost_or_income_column: The name of the cost or income column (if processed).
        - cost_or_income_criteria: A dictionary of criteria for cost or income classification
          (if processed).

    Raises:
        ValueError: If no date columns are found in the cash flow dataset. Ensure that date columns
            are defined either in the configuration or explicitly.
        ValueError: If no description columns are found in the cash flow dataset. Ensure that
            description columns are defined either in the configuration or explicitly.
        ValueError: If no amount columns are found in the cash flow dataset. Ensure that amount
            columns are defined either in the configuration or explicitly.
        ValueError: If cost or income columns are specified in the configuration, but none are found
            in the dataset. Ensure that cost or income columns are defined either in the configuration
            or keep the variable empty if not applicable.
    """
    date_column = [column.lower() for column in date_column]
    date_column_match = [column for column in date_column if column in dataset.columns]

    if not date_column_match:
        raise ValueError(
            "No date columns found in the cash flow dataset. Please specify the columns in the configuration file."
        )
    date_column_first = date_column_match[0]

    dataset = dataset.set_index(date_column_first)

    if not isinstance(dataset.index, pd.DatetimeIndex):
        dataset.index = pd.to_datetime(dataset.index, format=date_format)

    description_columns = [column.lower() for column in description_columns]
    description_columns_match = [
        column for column in description_columns if column in dataset.columns
    ]

    if not description_columns_match:
        raise ValueError(
            "No description columns found in the cash flow dataset. Please specify the columns in the configuration file."
        )
    description_columns = description_columns_match

    for column in description_columns:
        dataset[column] = dataset[column].astype("category")

    amount_column = [column.lower() for column in amount_column]
    amount_column_match = [
        column for column in amount_column if column in dataset.columns
    ]

    if not amount_column_match:
        raise ValueError(
            "No amount columns found in the cash flow dataset. Please specify the columns in the configuration file."
        )
    amount_column_first = amount_column_match[0]

    if decimal_seperator == "," and isinstance(
        dataset[amount_column_first].iloc[0], str
    ):
        dataset[amount_column_first] = dataset[amount_column_first].str.replace(".", "")
        dataset[amount_column_first] = dataset[amount_column_first].str.replace(
            ",", "."
        )
    if decimal_seperator == "." and isinstance(
        dataset[amount_column_first].iloc[0], str
    ):
        dataset[amount_column_first] = dataset[amount_column_first].str.replace(",", "")

    dataset[amount_column_first] = dataset[amount_column_first].astype("float")

    if cost_or_income_dict:
        cost_or_income_dict = {
            key.lower(): value for key, value in cost_or_income_dict.items()
        }
        cost_or_income_column = [column.lower() for column in cost_or_income_dict]
        cost_or_income_column_match = [
            column for column in cost_or_income_column if column in dataset.columns
        ]

        if not cost_or_income_column_match and cost_or_income_column:
            raise ValueError(
                "No cost or income columns found in the cash flow dataset. Please specify "
                "the columns in the configuration file or keep this variable empty if not applicable."
            )
    if cost_or_income_dict:
        cost_or_income_first = cost_or_income_column_match[0]
        cost_or_income_criteria = dict(
            cost_or_income_dict[cost_or_income_first].items()
        )

        dataset[cost_or_income_first] = dataset[cost_or_income_first].astype("category")
    else:
        cost_or_income_first = None
        cost_or_income_criteria = {}

    return (
        dataset,
        date_column_first,
        description_columns,
        amount_column_first,
        cost_or_income_first,
        cost_or_income_criteria,
    )


def apply_categorization(
    dataset: pd.DataFrame,
    categorization: dict,
    description_columns: list[str] | None,
    categorization_threshold: int,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    Apply categorization to transactions in a cash flow dataset based on provided rules.

    This function categorizes transactions in a cash flow dataset using a set of rules defined in the
    'categorization' parameter. It matches transaction descriptions with keywords and assigns categories
    accordingly. The categorized results are stored in a new 'category' column in the dataset.

    The calculations are done as follows:

        1. The function loops through each row in the dataset.
        2. It then loops through each category in the categorization rules.
        3. For each category, it looks at each defined description column and compares the description
            with each keyword in the category. It does so for EVERY keyword in the category.
        4. For each category it found a match (that is higher than the threshold), it adds the match
            value to a list of matches for that category. This uses the fuzzywuzzy library to calculate
            the match value.
        5. Once it has gone through all categories, it calculates the max match value for each
            category and assigns the category with the highest max match value to the transaction.
        6. If no category has a match value higher than the threshold, the transaction is assigned to
            the 'Other' category.

    This is a time consuming process (even though it still is just 2-3 minutes) but it is done to ensure
    that when you have a description that says "Apple Bandit" and you have the keyword "Apple" in the
    "Groceries" categorization and "Apple Bandit" in the "Drinks" categorization, it will be assigned
    to "Alcohol" because the match value is higher. This would not be achieved if the first match
    that crosses the Threshold is reached (which would be "Groceries" in this case).

    Parameters:
        dataset (pd.DataFrame): The cash flow dataset to categorize.
        categorization (dict | None): A dictionary of category names as keys and lists of keywords as
            values. If None, it defaults to the categorization rules specified in the configuration.
        description_columns (list[str] | None): A list of column names representing transaction
            descriptions in the dataset. If None, it defaults to the description columns specified in
            the configuration.
        categorization_threshold (int | None): A numeric threshold that determines the level of keyword
            match required for categorization. If None, it defaults to the threshold set in the configuration.
        direct_match (bool | None): A boolean flag indicating whether to consider direct keyword matches
            for categorization. If None, it defaults to the value specified in the configuration.

    Returns:
        Tuple[pd.DataFrame, Dict[str, int]]: A tuple containing the categorized cash flow dataset as the
        first element and a dictionary of total matches for each keyword as the second element.

    Raises:
        ValueError: If no description columns are found in the cash flow dataset. Ensure that description
            columns are defined either in the configuration or explicitly.
    """
    if not description_columns:
        raise ValueError(
            "No description columns found in the cash flow dataset. Please specify the columns in "
            "the configuration file. This needs to be defined within the section 'general' under "
            "'desciption_columns'."
        )

    categories = []
    keyword_matches = []
    certainty = []
    total_matches = {}

    for _, row in tqdm(
        dataset.iterrows(), total=dataset.shape[0], desc="Categorizing Transactions"
    ):
        category_decision = "Other"
        keyword_match = None
        result: dict[str, list[tuple[str, int]]] = {}

        for category, keywords in categorization.items():
            result[category] = []

            for column in description_columns:
                if row[column] != row[column]:
                    # In case the data is NaN
                    continue

                lowered_description = row[column].lower()

                for keyword in keywords:
                    if keyword not in total_matches:
                        total_matches[keyword] = 0

                    match = fuzz.partial_ratio(lowered_description, keyword.lower())
                    total_matches[keyword] = (
                        match
                        if match > total_matches[keyword]
                        else total_matches[keyword]
                    )

                    if match >= categorization_threshold:
                        result[category].append((keyword, match))

        highest_value = 0
        for key, values in result.items():
            # This is done to ensure you have the best fit for the transaction. If you have a description
            # that says "Apple Bandit" and you have the keyword "Apple" in the "Groceries" categorization
            # and "Apple Bandit" in the "Drinks" categorization, it will be assigned to "Drinks" because
            # the match value is higher. This would not be achieved if the first match that crosses the
            # Threshold is reached (which would be "Groceries" in this case).
            for keyword, value in values:
                if value > highest_value:
                    keyword_match = keyword
                    highest_value = value
                    category_decision = key

        categories.append(category_decision)
        keyword_matches.append(keyword_match)
        certainty.append(highest_value / 100)

    dataset["category"] = categories
    dataset["keyword"] = keyword_matches
    dataset["certainty"] = certainty

    return dataset, total_matches


def create_period_overview(
    dataset: pd.DataFrame,
    period_string: str,
    amount_column: str,
    categories: list,
    category_exclusions: list | None = None,
    include_totals: bool = False,
):
    """
    Create period overviews based on the cash flow dataset. It creates a DataFrame with the
    specified period as the index and the categories as the columns. The values in the DataFrame
    are the sum of the amounts for each category in the specified period.

    Parameters:
        dataset (pd.DataFrame): The cash flow dataset to create the period overview from.
        period_string (str): The period to create the overview for. This could be 'weekly', 'monthly',
            'quarterly', or 'yearly'.
        amount_column (str): The name of the column containing the transaction amounts.
        categories (list): A list of categories to include in the period overview.
        category_exclusions (list | None): A list of categories to exclude from the period overview.
            If None, no categories are excluded.
        include_totals (bool): A flag indicating whether to include a 'Totals' column in the period
            overview. If True, a 'Totals' column is included.

    Returns:
        pd.DataFrame: A DataFrame containing the period overview.
    """
    period_values = dataset.index.get_level_values(period_string.capitalize()).unique()

    period_cash_flows = pd.DataFrame(columns=period_values, index=categories)

    for period_value in period_values:
        period_data = (
            dataset.loc[period_value].groupby("category").agg({amount_column: "sum"})
        )
        period_data = period_data.reindex(categories).fillna(0)

        period_cash_flows.loc[:, period_value] = period_data.to_numpy()

    period_cash_flows = period_cash_flows.T

    if category_exclusions:
        period_cash_flows = period_cash_flows.drop(category_exclusions, axis=1)

    if include_totals:
        period_cash_flows.insert(0, "Totals", period_cash_flows.sum(axis=1))

    return period_cash_flows
