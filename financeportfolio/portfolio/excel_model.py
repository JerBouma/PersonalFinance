"""Excel Model"""

import numpy as np
import pandas as pd

# pylint: disable=too-many-locals


def create_portfolio_performance_excel_report(
    writer: pd.ExcelWriter, dataset: pd.DataFrame, sheet_name: str, currency: str = "$"
):
    """
    Create an Excel sheet with overview data from a DataFrame.

    Args:
        writer (pd.ExcelWriter): The Excel writer object to which the sheet will be added.
        dataset (pd.DataFrame): The DataFrame containing the data to be added to the sheet.
        sheet_name (str): The name of the sheet in the Excel file.

    Returns:
        None

    Creates an Excel sheet with formatted data from the given DataFrame and adds it to the
    specified Excel writer object. The function performs the following tasks:

    1. Formats the first row (header) with a bold style, centered alignment, and a gray background.
    2. Writes column names and their respective sums in the first and last rows of the sheet.
    3. Applies number formatting to columns with a currency format.
    4. Applies conditional formatting, such as color scales and data bars, to the data cells.
    5. Freezes the header row and first column for easy navigation.

    Example:
        To create an Excel sheet with an overview of a DataFrame 'overview_data' and add it
        to an Excel writer 'my_writer' with the sheet name 'OverviewSheet':

        >>> create_overview_excel_report(my_writer, overview_data, "OverviewSheet")
    """
    formatting = {
        "Costs": {"num_format": f"{currency}#,##0.00"},
        "Invested Amount": {"num_format": f"{currency}#,##0.00"},
        "Current Value": {"num_format": f"{currency}#,##0.00"},
        "Invested Weight": {"num_format": "0.00%"},
        "Current Weight": {"num_format": "0.00%"},
        "Return": {"num_format": "0.00%"},
    }

    dataset = dataset.reset_index()
    dataset[dataset.columns[0]] = dataset[dataset.columns[0]].astype(str)

    dataset.to_excel(writer, sheet_name=sheet_name, index=False)

    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    # Format first row
    column_format = workbook.add_format(
        {
            "bold": True,
            "align": "center",
            "bg_color": "#D3D3D3",
        }
    )

    for col, val in enumerate(dataset.columns):
        worksheet.write(0, col, val, column_format)

    # worksheet.write(len(dataset) + 1, 0, "Totals", column_format)

    # Apply number formatting
    date_format = workbook.add_format({"font_color": "white", "align": "center"})

    previous_value = None
    for index, value in dataset[dataset.columns[0]].items():
        worksheet.write(
            index + 1, 0, str(value), date_format if value == previous_value else None
        )
        previous_value = value

    for i, col in enumerate(dataset.columns[1:]):
        width = max(dataset[col].apply(lambda x: len(str(x))).max(), len(col)) + 5  # type: ignore
        worksheet.set_column(
            i + 1,
            i + 1,
            width,
            workbook.add_format(formatting[col]) if col in formatting else None,  # type: ignore
        )

    worksheet.freeze_panes(1, 2)


def create_transactions_performance_excel_report(
    writer: pd.ExcelWriter, dataset: pd.DataFrame, sheet_name: str, currency: str = "$"
):
    """
    Create an Excel sheet with overview data from a DataFrame.

    Args:
        writer (pd.ExcelWriter): The Excel writer object to which the sheet will be added.
        dataset (pd.DataFrame): The DataFrame containing the data to be added to the sheet.
        sheet_name (str): The name of the sheet in the Excel file.

    Returns:
        None

    Creates an Excel sheet with formatted data from the given DataFrame and adds it to the
    specified Excel writer object. The function performs the following tasks:

    1. Formats the first row (header) with a bold style, centered alignment, and a gray background.
    2. Writes column names and their respective sums in the first and last rows of the sheet.
    3. Applies number formatting to columns with a currency format.
    4. Applies conditional formatting, such as color scales and data bars, to the data cells.
    5. Freezes the header row and first column for easy navigation.

    Example:
        To create an Excel sheet with an overview of a DataFrame 'overview_data' and add it
        to an Excel writer 'my_writer' with the sheet name 'OverviewSheet':

        >>> create_overview_excel_report(my_writer, overview_data, "OverviewSheet")
    """
    formatting = {
        "Price": {"num_format": f"{currency}#,##0.00"},
        "Costs": {"num_format": f"{currency}#,##0.00"},
        "Benchmark Prices": {"num_format": f"{currency}#,##0.00"},
        "Total Invested": {"num_format": f"{currency}#,##0.00"},
        "End Of Period Price": {"num_format": f"{currency}#,##0.00"},
        "End Of Period Value": {"num_format": f"{currency}#,##0.00"},
        "Period Return": {"num_format": "0.00%"},
        "Period Return Value": {"num_format": f"{currency}#,##0.00"},
        "Total Benchmark Invested": {"num_format": f"{currency}#,##0.00"},
        "End Of Period Benchmark Price": {"num_format": f"{currency}#,##0.00"},
        "End Of Period Benchmark Value": {"num_format": f"{currency}#,##0.00"},
        "Period Benchmark Return": {"num_format": "0.00%"},
        "Alpha": {"num_format": "0.00%"},
    }

    dataset = dataset.reset_index()
    dataset[dataset.columns[0]] = dataset[dataset.columns[0]].astype(str)

    dataset.to_excel(writer, sheet_name=sheet_name, index=False)

    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    # Format first row
    column_format = workbook.add_format(
        {
            "bold": True,
            "align": "center",
            "bg_color": "#D3D3D3",
        }
    )

    for col, val in enumerate(dataset.columns):
        worksheet.write(0, col, val, column_format)

    # Apply number formatting
    date_format = workbook.add_format({"font_color": "white", "align": "center"})

    previous_value = None
    for index, value in dataset[dataset.columns[0]].items():
        worksheet.write(
            index + 1, 0, str(value), date_format if value == previous_value else None
        )
        previous_value = value

    for i, col in enumerate(dataset.columns[1:]):
        width = max(dataset[col].apply(lambda x: len(str(x))).max(), len(col)) + 5  # type: ignore
        worksheet.set_column(
            i + 1,
            i + 1,
            width,
            workbook.add_format(formatting[col]) if col in formatting else None,  # type: ignore
        )

    worksheet.freeze_panes(1, 2)


def create_portfolio_overview_excel_report(
    writer: pd.ExcelWriter, dataset: pd.DataFrame, sheet_name: str, currency: str = "$"
):
    """
    Create an Excel sheet with overview data from a DataFrame.

    Args:
        writer (pd.ExcelWriter): The Excel writer object to which the sheet will be added.
        dataset (pd.DataFrame): The DataFrame containing the data to be added to the sheet.
        sheet_name (str): The name of the sheet in the Excel file.

    Returns:
        None

    Creates an Excel sheet with formatted data from the given DataFrame and adds it to the
    specified Excel writer object. The function performs the following tasks:

    1. Formats the first row (header) with a bold style, centered alignment, and a gray background.
    2. Writes column names and their respective sums in the first and last rows of the sheet.
    3. Applies number formatting to columns with a currency format.
    4. Applies conditional formatting, such as color scales and data bars, to the data cells.
    5. Freezes the header row and first column for easy navigation.

    Example:
        To create an Excel sheet with an overview of a DataFrame 'overview_data' and add it
        to an Excel writer 'my_writer' with the sheet name 'OverviewSheet':

        >>> create_overview_excel_report(my_writer, overview_data, "OverviewSheet")
    """
    formatting = {
        "Price": {"num_format": f"{currency}#,##0.00"},
        "Costs": {"num_format": f"{currency}#,##0.00"},
        "Invested": {"num_format": f"{currency}#,##0.00"},
        "Latest Price": {"num_format": f"{currency}#,##0.00"},
        "Latest Value": {"num_format": f"{currency}#,##0.00"},
        "Return": {"num_format": "0.00%"},
        "Return Value": {"num_format": f"{currency}#,##0.00"},
        "Benchmark Return": {"num_format": "0.00%"},
        "Alpha": {"num_format": "0.00%"},
        "Weight": {"num_format": "0.00%"},
    }

    dataset = dataset.reset_index()
    dataset = dataset.replace([np.inf, -np.inf], 0)

    dataset.to_excel(writer, sheet_name=sheet_name, index=False)

    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    # Format first row
    column_format = workbook.add_format(
        {
            "bold": True,
            "align": "center",
            "bg_color": "#D3D3D3",
        }
    )

    for col, val in enumerate(dataset.columns):
        worksheet.write(0, col, val, column_format)

    for i, col in enumerate(dataset.columns):
        width = max(dataset[col].apply(lambda x: len(str(x))).max(), len(col)) + 5  # type: ignore
        worksheet.set_column(
            i,
            i,
            width,
            workbook.add_format(formatting[col]) if col in formatting else None,  # type: ignore
        )


def create_positions_overview_excel_report(
    writer: pd.ExcelWriter, dataset: pd.DataFrame, sheet_name: str, currency: str = "$"
):
    """
    Create an Excel sheet with overview data from a DataFrame.

    Args:
        writer (pd.ExcelWriter): The Excel writer object to which the sheet will be added.
        dataset (pd.DataFrame): The DataFrame containing the data to be added to the sheet.
        sheet_name (str): The name of the sheet in the Excel file.

    Returns:
        None

    Creates an Excel sheet with formatted data from the given DataFrame and adds it to the
    specified Excel writer object. The function performs the following tasks:

    1. Formats the first row (header) with a bold style, centered alignment, and a gray background.
    2. Writes column names and their respective sums in the first and last rows of the sheet.
    3. Applies number formatting to columns with a currency format.
    4. Applies conditional formatting, such as color scales and data bars, to the data cells.
    5. Freezes the header row and first column for easy navigation.

    Example:
        To create an Excel sheet with an overview of a DataFrame 'overview_data' and add it
        to an Excel writer 'my_writer' with the sheet name 'OverviewSheet':

        >>> create_overview_excel_report(my_writer, overview_data, "OverviewSheet")
    """
    formatting = {
        "Price": {"num_format": f"{currency}#,##0.00"},
        "Costs": {"num_format": f"{currency}#,##0.00"},
        "Benchmark Prices": {"num_format": f"{currency}#,##0.00"},
        "Total Invested": {"num_format": f"{currency}#,##0.00"},
        "End Of Period Price": {"num_format": f"{currency}#,##0.00"},
        "End Of Period Value": {"num_format": f"{currency}#,##0.00"},
        "Period Return": {"num_format": "0.00%"},
        "Period Return Value": {"num_format": f"{currency}#,##0.00"},
        "Total Benchmark Invested": {"num_format": f"{currency}#,##0.00"},
        "End Of Period Benchmark Price": {"num_format": f"{currency}#,##0.00"},
        "End Of Period Benchmark Value": {"num_format": f"{currency}#,##0.00"},
        "Period Benchmark Return": {"num_format": "0.00%"},
        "Alpha": {"num_format": "0.00%"},
    }

    dataset.to_excel(writer, sheet_name=sheet_name, index=True)

    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    # Format first row
    column_format = workbook.add_format(
        {
            "bold": True,
            "align": "center",
            "bg_color": "#D3D3D3",
        }
    )

    for col, val in enumerate(dataset.columns.get_level_values(0)):
        worksheet.write(0, col + 1, val, column_format)
    for col, val in enumerate(dataset.columns.get_level_values(1)):
        worksheet.write(1, col + 1, val, column_format)

    for i, col in enumerate(dataset.columns):
        width = max(dataset[col].apply(lambda x: len(str(x))).max(), len(col)) + 5  # type: ignore
        worksheet.set_column(
            i + 1,
            i + 1,
            width,
            workbook.add_format(formatting[col]) if col in formatting else None,  # type: ignore
        )

    worksheet.freeze_panes(2, 1)
