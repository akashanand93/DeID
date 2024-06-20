from typing import Dict
import json
from pandas import DataFrame
import pandas as pd


class FileIO:
    """
    Convenience functions for interacting with files.
    """

    @staticmethod
    def load_json(file) -> Dict:
        """Read JSON file"""
        with open(file, "r") as f:
            return json.load(f)

    @staticmethod
    def load_ndjson_df(file) -> DataFrame:
        """Loads an ndjson file into a pandas DataFrame"""
        return pd.read_json(file, lines=True)

    @staticmethod
    def write_ndjson_df(file, df: DataFrame) -> None:
        """Writes a pandas DataFrame to an ndjson file"""
        df.to_json(file, orient="records", lines=True)

    @staticmethod
    def load_csv_df(file) -> DataFrame:
        """Loads a CSV file into a pandas DataFrame"""
        return pd.read_csv(file)
