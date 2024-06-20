import uuid
import pandas as pd


class FieldUtils:
    """Helper functions to extract fields from the mimic dataset."""

    @staticmethod
    def get_reference_uuid(subject: object) -> str:
        """
        Input: The referencing encounter / recorder / etc col in mimic: {'reference': 'Patient/<uuid>', ...}
        Output: <uuid>
        """
        return subject["reference"].split("/")[-1].strip()

    @staticmethod
    def get_mimic_id(identifier: object) -> str:
        """
        Input: The identifier column in mimic: [{'system': '...', 'value': '<uuid>'}]
        Output: <uuid>
        """
        return identifier[0]["value"]

    @staticmethod
    def get_deterministic_uuid(
        inp_string: str, fixed_uuid_namespace="00000000-0000-0000-0000-000000000000"
    ) -> str:
        """
        Generate a deterministic UUID for any given string
        """
        uuid_namespace = uuid.UUID(fixed_uuid_namespace)
        deterministic_uuid = uuid.uuid5(uuid_namespace, inp_string)

        return str(deterministic_uuid)

    @staticmethod
    def format_encounter(encounter_uuid: str) -> dict:
        if pd.isna(encounter_uuid):
            None
        else:
            return {"reference": f"Encounter/{encounter_uuid}", "type": "Encounter"}

    # --- helper functions for loading Conditions. --- #
    @staticmethod
    def get_condition_code_uuid(code_record: object) -> dict:
        """
        Extracting, transforming and formatting the code field,
        As expected and recognized by OpenMRS.
        Update the code inside in the same UUID format as in Condition Terminology.
        """
        if "icd10" in code_record["coding"][0]["system"].lower():
            system = "ICD-10"
        else:
            system = "ICD-9"

        icd_code = f"{system}:{code_record["coding"][0]["code"]}"

        icd_uuid = FieldUtils.get_deterministic_uuid(icd_code)

        return {
            "coding": [{"code": icd_uuid}],
        }

    @staticmethod
    def get_canonical_text(code_record: object) -> str:
        """
        Get the original display text for condition without code associated with it
        """
        return code_record["coding"][0]["display"]

    @staticmethod
    def get_canonical_code(code_record: object) -> str:
        """
        Get the original code with the system associated with it.
        Example: "ICD-10:Z8546" or "ICD-9:20500"
        """
        if "icd10" in code_record["coding"][0]["system"].lower():
            canonical_code = f"ICD-10:{code_record["coding"][0]["code"]}"
        else:
            canonical_code = f"ICD-9:{code_record["coding"][0]["code"]}"

        return canonical_code

    # --- helper functions for loading Lab Event Observations. --- #
    @staticmethod
    def get_lab_observation_code_uuid(record: object) -> dict:
        lab_observation_code = f"D-LABITEMS:{record["coding"][0]["code"]}"

        lab_observation_uuid = FieldUtils.get_deterministic_uuid(lab_observation_code)

        return {
            "coding": [{"code": lab_observation_uuid}],
        }

    @staticmethod
    def get_encounter_reference_uuid_or_none(subject: object) -> str:
        if not pd.isna(subject):
            return subject["reference"].split("/")[-1].strip()
        else:
            return None

    # --- helper functions for loading Date Time Event Observations. --- #
    @staticmethod
    def get_date_time_observation_code_uuid(record: object) -> dict:
        date_time_observation_code = f"D-ITEMS:{record["coding"][0]["code"]}"

        date_time_observation_uuid = FieldUtils.get_deterministic_uuid(
            date_time_observation_code
        )

        return {
            "coding": [{"code": date_time_observation_uuid}],
        }

    @staticmethod
    def get_date_time_observation_category_code_uuid(record: object) -> dict:
        date_time_observation_category_code = (
            f"OBSERVATION-CATEGORY:{record[0]["coding"][0]["code"]}"
        )

        date_time_observation_category_uuid = FieldUtils.get_deterministic_uuid(
            date_time_observation_category_code
        )

        return {
            "coding": [{"code": date_time_observation_category_uuid}],
        }

    @staticmethod
    def get_canonical_drug_name(name: str) -> str:
        """A simple helper function to get the canonical drug name to avoid duplicates."""
        return f"DRUG: {name.strip().lower()}"
