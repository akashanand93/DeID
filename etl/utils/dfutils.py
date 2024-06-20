import os
from typing import Dict, List
from loguru import logger
import pandas as pd
from pandas import DataFrame
from common.utils.fileio import FileIO

# Some type definitions
DFDict = Dict[str, pd.DataFrame]


class DFUtils:
    @staticmethod
    def log_df_info(data: DFDict):
        """A convenience fn to log metrics about a given set of DFs"""
        for k, df in data.items():
            logger.debug(
                f"Dataframe: {k}: {len(df)} entries. {len(df.columns)} Columns. Names:"
            )
            logger.debug(f"{df.columns.to_list()}")
        logger.debug(f"---\n")

    @staticmethod
    def group_by_count(df: DataFrame, grouping_cols: List[str]) -> DataFrame:
        return (
            df.groupby(grouping_cols)
            .size()
            .to_frame(name="count")
            .reset_index()
            .sort_values(by="count", ascending=False)
        )

    @staticmethod
    def update_subject_fhir_uuid(
        df: DataFrame, p_meta_df: DataFrame, patient_uuid_col="mimic_patient_uuid"
    ) -> DataFrame:
        """
        Join with p_meta_df and update the subject field with the latest fhir_uuid of the patient.
        """
        df = df.merge(
            p_meta_df[["mimic_uuid", "fhir_uuid"]],
            left_on=patient_uuid_col,
            right_on="mimic_uuid",
            how="left",
        )

        # (Re-)write subject field.
        df["subject"] = df["fhir_uuid"].apply(
            lambda x: {"reference": f"Patient/{x}", "type": "Patient"}
        )

        return df.drop(columns=["mimic_uuid", "fhir_uuid"])

    @staticmethod
    def update_encounter_fhir_uuid(
        df: DataFrame, e_meta_df: DataFrame, encounter_uuid_col="mimic_encounter_uuid"
    ) -> DataFrame:
        """
        Join with e_meta_df and update the encounter field with the latest fhir_uuid of the encounter.
        """
        df = df.merge(
            e_meta_df[["mimic_uuid", "fhir_uuid"]],
            left_on=encounter_uuid_col,
            right_on="mimic_uuid",
            how="left",
        )

        # (Re-)write Encounter field.
        df["partOf"] = df["fhir_uuid"].apply(
            lambda x: {"reference": f"Encounter/{x}", "type": "Encounter"}
        )

        return df.drop(columns=["mimic_uuid", "fhir_uuid"])


class LakeDB:
    """
    Simulate a database backed by accessing ndjson files in the data lake.
    """

    def __init__(self, db: str):
        self.db = db

    def exists(self, table_path: str, _type="ndjson") -> bool:
        fpath = f"{self.db}/{table_path}.{_type}"
        return os.path.exists(fpath)

    def get_table(self, table_path: str, _type="ndjson") -> DataFrame:
        if _type == "csv":
            return pd.read_csv(f"{self.db}/{table_path}.{_type}")
        else:
            return FileIO.load_ndjson_df(f"{self.db}/{table_path}.{_type}")

    def write_table(self, df: DataFrame, table_path: str, _type="ndjson") -> None:
        if _type == "csv":
            df.to_csv(f"{self.db}/{table_path}.{_type}", index=False)
        else:
            FileIO.write_ndjson_df(f"{self.db}/{table_path}.{_type}", df)

    # Convenience method to avoid keeping a LakeDB object around.
    @staticmethod
    def get_dbtable(db: str, table_path: str, _type="ndjson") -> DataFrame:
        return LakeDB(db).get_table(table_path, _type)

    @staticmethod
    def write_dbtable(db: str, df: DataFrame, table_path: str, _type="ndjson") -> None:
        LakeDB(db).write_table(df, table_path, _type)
