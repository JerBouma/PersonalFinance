"""Helpers Module"""

import pandas as pd
import yaml


def read_excel(location: str):
    """
    Read an Excel (.xlsx) or CSV (.csv) file into a Pandas DataFrame.

    This function reads and loads data from an Excel or CSV file located at the specified 'location'
    into a Pandas DataFrame.

    Parameters:
        location (str): The file path of the Excel or CSV file to read.

    Returns:
        pandas.DataFrame: A DataFrame containing the data from the file.

    Raises:
        ValueError: If the specified file does not have a '.xlsx' or '.csv' extension.
    """
    if location.endswith(".xlsx"):
        return pd.read_excel(location)
    if location.endswith(".csv"):
        return pd.read_csv(location)

    raise ValueError("File type not supported. Please use .xlsx or .csv")


def read_yaml_file(location: str):
    """
    Read and parse a YAML file.

    This function reads a YAML file located at the specified 'location' and parses its contents into
    a Python dictionary. It handles exceptions for file not found, YAML parsing errors, and other
    general exceptions.

    Parameters:
        location (str): The file path of the YAML file to read and parse.

    Returns:
        dict: A dictionary containing the parsed YAML data.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        yaml.YAMLError: If there is an error in parsing the YAML content.
        Exception: For any other general exceptions that may occur during file reading or parsing.
    """
    try:
        with open(location) as yaml_file:
            data = yaml.safe_load(yaml_file)
        return data
    except FileNotFoundError as exc:
        raise ValueError(f"The file '{location}' does not exist.") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"Error parsing '{location}': {exc}") from exc
    except KeyError as exc:
        raise ValueError(f"An error occurred: {exc}") from exc
    except ValueError as exc:
        raise ValueError(f"An error occurred: {exc}") from exc
