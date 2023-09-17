

import os
from tqdm import tqdm
import pandas as pd
import numpy as np

from personal_finance import helpers
from fuzzywuzzy import fuzz

import xlsxwriter
from openpyxl.styles import Font, Alignment, PatternFill

def create_overview_excel_report(writer: pd.ExcelWriter, dataset: pd.DataFrame, sheet_name: str):
    
    dates = dataset.index.astype(str)
    dataset.index = dates
    dataset = dataset.reset_index()

    dataset.to_excel(writer, sheet_name=sheet_name, index=False)
    
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    
    # Format first row
    column_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'num_format': '$#,##0.00'})
    
    for col, val in enumerate(dataset.columns):
        worksheet.write(0, col, val, column_format)
        worksheet.write(len(dataset) + 1, col, dataset[val].sum(), column_format)
        
    worksheet.write(len(dataset) + 1, 0, "Totals", column_format)

    # Apply number formatting
    format = workbook.add_format({'num_format': '$#,##0.00', 'align': 'center'})
    
    for i, col in enumerate(dataset.columns):
        width = max(dataset[col].apply(lambda x: len(str(x))).max(), len(col)) + 1
        worksheet.set_column(i, i, width, format)
        
    # Apply conditional formatting
    for i, _ in enumerate(dataset.index):
        worksheet.conditional_format(i + 1, 2, i + 1, len(dataset.columns) - 1, {'type': '3_color_scale'})
        
    worksheet.conditional_format(f"B2:B{len(dataset)}", {'type': 'data_bar', 'data_bar_2010': True})
        
    worksheet.freeze_panes(1, 1)
        

    # worksheet.set_column('A:A', 20, bold_format)

    
