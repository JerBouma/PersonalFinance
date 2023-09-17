"""Excel Model"""

import pandas as pd


def create_overview_excel_report(
    writer: pd.ExcelWriter, dataset: pd.DataFrame, sheet_name: str
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
    dates = dataset.index.astype(str)
    dataset.index = dates
    dataset = dataset.reset_index()

    dataset.to_excel(writer, sheet_name=sheet_name, index=False)

    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    # Format first row
    column_format = workbook.add_format(
        {
            "bold": True,
            "align": "center",
            "bg_color": "#D3D3D3",
            "num_format": "$#,##0.00",
        }
    )

    for col, val in enumerate(dataset.columns):
        worksheet.write(0, col, val, column_format)
        worksheet.write(len(dataset) + 1, col, dataset[val].sum(), column_format)

    worksheet.write(len(dataset) + 1, 0, "Totals", column_format)

    # Apply number formatting
    number_format = workbook.add_format({"num_format": "$#,##0.00", "align": "center"})

    for i, col in enumerate(dataset.columns):
        width = max(dataset[col].apply(lambda x: len(str(x))).max(), len(col)) + 1  # type: ignore
        worksheet.set_column(i, i, width, number_format)

    # Apply conditional formatting
    for i, _ in enumerate(dataset.index):
        worksheet.conditional_format(
            i + 1, 2, i + 1, len(dataset.columns) - 1, {"type": "3_color_scale"}
        )

    worksheet.conditional_format(
        f"B2:B{len(dataset)}", {"type": "data_bar", "data_bar_2010": True}
    )

    worksheet.freeze_panes(1, 1)

    # worksheet.set_column('A:A', 20, bold_format)
