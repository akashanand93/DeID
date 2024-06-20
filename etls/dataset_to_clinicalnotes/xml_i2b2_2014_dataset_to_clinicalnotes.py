import asyncio
import sys
import json
import glob
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


class I2B22014ToClinicalNotes(DSETL[AnnotatedClinicalNote, AnnotatedClinicalNote]):

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
        self.file_names = []
        self.out_dir = self.options["out-dir"]
        self.out_db = LakeDB(self.out_dir)
        os.makedirs(self.out_dir, exist_ok=True)

    async def extract(self) -> List[AnnotatedClinicalNote]:
        # step1: Read xml file from inp_db
        file_pattern = "*.xml"
        files = glob.glob(os.path.join(self.inp_file_path, file_pattern))
        cn = []
        id = 1
        for file in tqdm.tqdm(files):
            base_name = os.path.basename(file).replace(".xml", "")
            self.file_names.append(base_name)
            cn.append(self._read_xml_file_and_return_clinicalnotes(file))
            cn[-1].note_id = str(id)
            id += 1
        logger.success(f"Reading Done...  from folder {self.inp_file_path}")

        # step2: for all clinical notes make a List[ClinicalNote]
        return cn

    async def transform(
        self, data: List[AnnotatedClinicalNote]
    ) -> List[AnnotatedClinicalNote]:
        # Example transformation logic
        return data

    async def load(self, data: List[AnnotatedClinicalNote]):
        # dump in outfile.ndjson format
        file_saved = self._write_clinical_notes(
            data, file_name="2014_I2B2_annotated_data"
        )
        logger.success(f"Loaded {len(data)} to file {file_saved}")
        return

    def _write_clinical_notes(
        self, notes: List[AnnotatedClinicalNote], file_name: str, _type="ndjson"
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
    ) -> AnnotatedClinicalNote:
        # Parse XML file and convert to a list of clinical notes
        tree = ET.parse(file_path)
        root = tree.getroot()
        note = root.find("TEXT").text.strip()
        note = note.replace("\n", " ")
        note = note.replace("\t", " ")
        note = " ".join(note.split())
        annotations = []
        tags = root.findall("TAGS")
        for tag in tags:
            for child in tag:
                if child.tag != "PHI":
                    token = child.attrib["text"]
                    token = " ".join(token.split())
                    annotations.append(
                        SingleAnnotation(
                            token=token,
                            start_index=int(child.attrib["start"]),
                            end_index=int(child.attrib["end"]),
                            type=child.tag,
                        )
                    )     
        return AnnotatedClinicalNote(
            text=note,
            note_type=str(type(note)),
            date="",
            patient_id="",
            note_id="",
            metadata={},
            annotations=annotations,
        )


if __name__ == "__main__":
    # Run the ETL process for the first type
    ConfigureLogging()
    etl1 = I2B22014ToClinicalNotes(cli_tokens=sys.argv[1:])
    asyncio.run(etl1.run())
