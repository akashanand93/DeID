import asyncio
import sys
import json
from etl.utils.dfutils import LakeDB
from utils.constants import DataConstants
from models.model import ClinicalNote, Sentence
from etls.DSETL import DSETL
from typing import List
from common.utils.log import ConfigureLogging
from pydantic.json import pydantic_encoder
from loguru import logger
import os
import tqdm


class UnannotatedClinicalNotesToSnetences(DSETL[ClinicalNote, Sentence]):
    
    # Default options for output directory
    DEFAULT_OPTIONS = {
        "out-dir": DataConstants.PROCESSED_SENTENCES_DIR,
        "inp-dir": DataConstants.DEID_PROCESSED_DIR
    }

    def __init__(
        self,
        cli_tokens=None,
        options=None,
    ):
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
        self.sentence_extractor = None

    def set_algo(self, algo):
        # Set algorithm for sentence extraction
        self.sentence_extractor = algo

    async def extract(self) -> List[ClinicalNote]:
        # step1: Read ndjson file from inp_db
        cn = self._read_ndjson_file_and_return_clinicalnotes(self.inp_file_path)
        logger.success(f"Reading Done...  from file {self.inp_file_path}")

        # step2: for all clinical notes make a List[ClinicalNote]
        return cn

    async def transform(self, data: List[ClinicalNote]) -> List[Sentence]:
        # Transform clinical notes to sentences
        cs = self._transform_clinical_notes_to_sentences(data)
        logger.success(
            f"Clinical Notes to Sentences Tranformation Done...  from file {self.inp_file_path}"
        )
        return cs

    async def load(self, data: List[Sentence]):
        # dump in outfile.ndjson format
        file_saved = self._write_clinical_sentences(data, self.out_file_name)
        logger.success(f"Loaded {len(data)} to file {file_saved}")
        return

    def _write_clinical_sentences(
        self, sentences: List[Sentence], file_name: str, _type="ndjson"
    ) -> None:
        # Write sentences to ndjson file
        if _type != "ndjson":
            raise ValueError("Only 'ndjson' type is supported")
        with open(f"{self.out_db.db}/{file_name}.{_type}", "w") as f:
            for sentence in tqdm.tqdm(sentences):
                f.write(json.dumps(sentence, default=pydantic_encoder) + "\n")
        return f"{self.out_db.db}/{file_name}.{_type}"

    def _transform_clinical_notes_to_sentences(
        self, notes: List[ClinicalNote]
    ) -> List[Sentence]:
        # Transform clinical notes into sentences with annotations
        snetences = []

        for note in tqdm.tqdm(notes):
            sentences_ = self.sentence_extractor.extract_sentences(note.text)
            id = 0
            for sentence in sentences_:
                snetences.append(
                    Sentence(
                        text=sentence,
                        sentence_id_in_note=id,
                        major_section="",
                        associated_note_id=note.note_id,
                        note_type=note.note_type,
                        date=note.date,
                        patient_id=note.patient_id,
                        metadata=note.metadata,
                    )
                )
                id += 1

        return snetences

    def _read_ndjson_file_and_return_clinicalnotes(
        self, file_path: str
    ) -> List[ClinicalNote]:
        # Read ndjson file and return list of clinical notes
        notes = []
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")
        with open(file_path, "r") as f:
            for line in tqdm.tqdm(f, desc="Processing lines"):
                note = ClinicalNote.model_validate_json(line)
                notes.append(note)
        return notes


if __name__ == "__main__":
    # Run the ETL process for the first type
    ConfigureLogging()
    etl1 = UnannotatedClinicalNotesToSnetences(cli_tokens=sys.argv[1:])
    asyncio.run(etl1.run())
