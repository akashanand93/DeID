import asyncio
import sys
import json
from etl.utils.dfutils import LakeDB
from utils.constants import DataConstants
from models.model import AnnotatedClinicalNote, SingleAnnotation
from etls.DSETL import DSETL
from typing import List
from common.utils.log import ConfigureLogging
import xml.etree.ElementTree as ET
from pydantic.json import pydantic_encoder
from loguru import logger
import os
import tqdm

class AnnotatedI2B2ToClinicalNotes(DSETL[AnnotatedClinicalNote, AnnotatedClinicalNote]):

    # Default options for the output directory
    DEFAULT_OPTIONS = {
        "out-dir": DataConstants.DEID_PROCESSED_DIR,
        "inp-dir": DataConstants.I2B2_DATA_DIR,
    }

    def __init__(self, cli_tokens=None, options=None):
        # Initialize with default options and create necessary directories
        super().__init__(cli_tokens, options, self.DEFAULT_OPTIONS)
        self.root = self.options["root"]
        self.inp_dir = self.options["inp-dir"].format(root_dir=self.root)      
        self.inp_file_name = self.options["inp-file"]
        self.inp_file_path = self.inp_dir + "/" + self.inp_file_name
        self.out_dir = self.options["out-dir"].format(root_dir=self.root)
        self.out_file_name = self.options["out-file"].split(".")[0]
        self.out_db = LakeDB(self.out_dir)
        os.makedirs(self.out_dir, exist_ok=True)

    async def extract(self) -> List[AnnotatedClinicalNote]:
        # Step 1: Read XML file and convert to clinical notes
        cn = self._read_xml_file_and_return_clinicalnotes(self.inp_file_path)
        logger.success(f"Reading Done... from file {self.inp_file_path}")
        return cn

    async def transform(self, data: List[AnnotatedClinicalNote]) -> List[AnnotatedClinicalNote]:
        # Example transformation logic (currently no transformation)
        return data

    async def load(self, data: List[AnnotatedClinicalNote]):
        # Step 3: Write clinical notes to an NDJSON file
        file_saved = self._write_clinical_notes(data, self.out_file_name)
        logger.success(f"Loaded {len(data)} to file {file_saved}")

    def _write_clinical_notes(self, notes: List[AnnotatedClinicalNote], file_name: str, _type="ndjson") -> str:
        # Write clinical notes to an NDJSON file
        if _type != "ndjson":
            raise ValueError("Only 'ndjson' type is supported")
        with open(f"{self.out_db.db}/{file_name}.{_type}", "w") as f:
            for note in tqdm.tqdm(notes):
                f.write(json.dumps(note, default=pydantic_encoder) + "\n")
        return f"{self.out_db.db}/{file_name}.{_type}"

    def _read_xml_file_and_return_clinicalnotes(self, file_path: str) -> List[AnnotatedClinicalNote]:
        # Parse XML file and convert to a list of clinical notes with annotations
        tree = ET.parse(file_path)
        root = tree.getroot()
        notes = []
        for record in tqdm.tqdm(root.findall("RECORD")):
            text = ""
            tags = []
            start_index = 0
            for elem in record.find("TEXT").iter():
                if elem.tag == "PHI":
                    start_index = len(text)
                    text += elem.text if elem.text else ""
                    end_index = len(text)
                    tags.append(
                        SingleAnnotation(
                            token=elem.text,
                            start_index=start_index,
                            end_index=end_index,
                            type=elem.attrib.get("TYPE"),
                        )
                    )
                    text += elem.tail if elem.tail else ""
                else:
                    text += elem.text if elem.text else ""
            text = text.replace("\n", " ")
            notes.append(
                AnnotatedClinicalNote(
                    text=text,
                    note_type=str(type(text)),
                    date="",
                    patient_id="",
                    note_id=str(record.attrib["ID"]),
                    metadata={},
                    annotations=tags,
                )
            )
        return notes

if __name__ == "__main__":
    # Run the ETL process
    ConfigureLogging()
    etl1 = AnnotatedI2B2ToClinicalNotes(cli_tokens=sys.argv[1:])
    asyncio.run(etl1.run())
