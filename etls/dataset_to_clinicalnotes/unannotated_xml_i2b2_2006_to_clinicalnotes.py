import asyncio
import sys
import json
from etl.utils.dfutils import LakeDB
from utils.constants import DataConstants
from models.model import ClinicalNote
from etls.DSETL import DSETL
from typing import List
from common.utils.log import ConfigureLogging
import xml.etree.ElementTree as ET
from pydantic.json import pydantic_encoder
from loguru import logger
import os
import tqdm


class UnannotatedI2B2ToClinicalNotes(DSETL[ClinicalNote, ClinicalNote]):

    # Default options for the output directory
    DEFAULT_OPTIONS = {
        "out-dir": DataConstants.DEID_PROCESSED_DIR,
    }

    def __init__(
        self,
        cli_tokens=None,
        options=None,
    ):
        # Initialize with default options and create necessary directories
        super().__init__(cli_tokens, options, self.DEFAULT_OPTIONS)
        self.inp_file_path = self.options["inp-file"]
        self.file_name = self.inp_file_path.split("/")[-1].split(".")[0]
        self.out_dir = self.options["out-dir"]
        self.out_db = LakeDB(self.out_dir)
        os.makedirs(self.out_dir, exist_ok=True)

    async def extract(self) -> List[ClinicalNote]:
        # step1: Read xml file from inp_db
        cn = self._read_xml_file_and_return_clinicalnotes(self.inp_file_path)
        logger.success(f"Reading Done...  from file {self.inp_file_path}")

        # step2: for all clinical notes make a List[ClinicalNote]
        return cn

    async def transform(self, data: List[ClinicalNote]) -> List[ClinicalNote]:
        # Example transformation logic
        return data

    async def load(self, data: List[ClinicalNote]):
        # dump in outfile.ndjson format
        file_saved = self._write_clinical_notes(data, self.file_name)
        logger.success(f"Loaded {len(data)} to file {file_saved}")
        return

    def _write_clinical_notes(
        self, notes: List[ClinicalNote], file_name: str, _type="ndjson"
    ) -> None:
        # Write clinical notes to an NDJSON file
        if _type != "ndjson":
            raise ValueError("Only 'ndjson' type is supported")
        with open(f"{self.out_db.db}/{file_name}.{_type}", "w") as f:
            for note in tqdm.tqdm(notes):
                f.write(json.dumps(note, default=pydantic_encoder) + "\n")
        return f"{self.out_db.db}/{file_name}.{_type}"

    def _read_xml_file_and_return_clinicalnotes(
        self, file_path: str
    ) -> List[ClinicalNote]:
        # Parse XML file and convert to a list of clinical notes
        notes = []
        root = ET.parse(f"{file_path}").getroot()
        for record in tqdm.tqdm(root.findall("RECORD")):
            note = record.find("TEXT").text
            note = note.replace("\n", " ")
            notes.append(
                ClinicalNote(
                    text=note,
                    note_type=str(type(note)),
                    date="",
                    patient_id="",
                    note_id=str(record.attrib["ID"]),
                    metadata={},
                )
            )
        return notes


if __name__ == "__main__":
    # Run the ETL process for the first type
    ConfigureLogging()
    etl1 = UnannotatedI2B2ToClinicalNotes(cli_tokens=sys.argv[1:])
    asyncio.run(etl1.run())
