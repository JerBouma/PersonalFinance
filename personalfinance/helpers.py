"""Helpers Module"""

import os

import pandas as pd
import requests
import yaml

# pylint: disable=too-few-public-methods

BASE_URL = "https://raw.githubusercontent.com/JerBouma/PersonalFinance/main/"
VALID_CODE = 200


class Style:
    """
    This class is meant for easier styling throughout the application where it
    adds value (e.g. to create a distinction between an error and warning).
    """

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"


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


def download_example_datasets(base_url: str | None = None):
    """
    Download example datasets from the GitHub repository. These are used to test the application.

    Returns:
        The directory where the files are downloaded to.

    Notes:
        The files are downloaded to the following directory:
            - examples/portfolio/Transactions 1.csv
            - examples/portfolio/Transactions 2.csv
            - examples/portfolio/Transactions 3.csv
            - examples/cashflows/cashflow_example.csv
    """
    base_url = base_url if base_url else BASE_URL

    directory = "examples/cashflows/"
    urls = [f"{base_url}examples/cashflows/cashflow_example.csv"]

    for url in urls:
        response = requests.get(url, timeout=60)

        previous_location = None
        for location in directory.split("/"):
            if location:
                if previous_location and location not in os.listdir(previous_location):
                    os.mkdir(directory)
                elif location not in os.listdir():
                    os.mkdir(location)

            previous_location = location

        if response.status_code == VALID_CODE:
            with open(directory + url.split("/")[-1], "wb") as f:
                f.write(response.content)
        else:
            print(
                "Failed to download the file. HTTP status code:", response.status_code
            )


def download_yaml_configuration(example: bool = False, name: str | None = None):
    """
    Download the YAML configuration files from the GitHub repository. It is both possible to download the
    default configuration files or the example configuration files.

    Parameters:
        example (bool): Whether to download the example YAML configuration files or the default YAML
            configuration files. Defaults to False (default).
        name (str): The name of the YAML configuration file to download. Defaults to None (default).
            If None, the default name is used.

    Returns:
        The directory where the files are downloaded to.

    Notes:
        The files are downloaded to the following directory:
            - configurations/portfolio.yaml
            - configurations/cashflow.yaml
            - examples/configurations/portfolio_example.yaml
            - examples/configurations/cashflow_example.yaml
    """
    if name and not name.endswith(".yaml"):
        raise ValueError("Please include the .yaml extension type.")

    if example:
        directory = "examples/configurations/"
        if not name:
            name = "cashflow_example.yaml"
        url = BASE_URL + "examples/configurations/cashflow_example.yaml"
    else:
        directory = "configurations/"
        if not name:
            name = "cashflow.yaml"
        url = BASE_URL + "configurations/cashflow.yaml"

    response = requests.get(url, timeout=60)

    previous_location = None
    for location in directory.split("/"):
        if location:
            if previous_location and location not in os.listdir(previous_location):
                os.mkdir(directory)
            elif location not in os.listdir():
                os.mkdir(location)

        previous_location = location

    if response.status_code == VALID_CODE:
        with open(str(directory) + str(name), "wb") as f:
            f.write(response.content)
    else:
        print("Failed to download the file. HTTP status code:", response.status_code)

    return str(directory) + str(name)
