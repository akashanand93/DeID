import asyncio
import sys
import json
from etl.utils.dfutils import LakeDB
from utils.constants import DataConstants
from models.model import (
    AnnotatedClinicalNote,
    AnnotatedSentence,
    Annotations,
)
from scripts.post_processing_of_tagged_sentences import (
    convert_human_readable_to_machine_readable_annotations,
)
from etls.DSETL import DSETL
from typing import List
from common.utils.log import ConfigureLogging
from pydantic.json import pydantic_encoder
from loguru import logger
import os
import tqdm

class AnnotatedClinicalNotesToSnetences(
    DSETL[AnnotatedClinicalNote, AnnotatedSentence]
):

    # Default options for output directory
    DEFAULT_OPTIONS = {
        "out-dir": DataConstants.PROCESSED_SENTENCES_DIR,
        "inp-dir": DataConstants.DEID_PROCESSED_DIR
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
        self.sentence_extractor = None

    def set_algo(self, algo):
        # Set algorithm for sentence extraction
        self.sentence_extractor = algo

    async def extract(self) -> List[AnnotatedClinicalNote]:
        # Step 1: Read ndjson file from input
        cn = self._read_ndjson_file_and_return_clinicalnotes(self.inp_file_path)
        logger.success(f"Reading Done...  from file {self.inp_file_path}")
        return cn

    async def transform(self, data: List[AnnotatedClinicalNote]) -> List[AnnotatedSentence]:
        # Step 2: Transform clinical notes to sentences
        cs = self._transform_clinical_notes_to_sentences(data)
        logger.success(f"Clinical Notes to Sentences Transformation Done...  from file {self.inp_file_path}")
        return cs

    async def load(self, data: List[AnnotatedSentence]):
        # Step 3: Load transformed sentences to output file
        file_saved = self._write_clinical_sentences(data, self.out_file_name)
        logger.success(f"Loaded {len(data)} to file {file_saved}")
        return

    def _write_clinical_sentences(self, sentences: List[AnnotatedSentence], file_name: str, _type="ndjson") -> None:
        # Write sentences to ndjson file
        if _type != "ndjson":
            raise ValueError("Only 'ndjson' type is supported")
        with open(f"{self.out_db.db}/{file_name}.{_type}", "w") as f:
            for sentence in tqdm.tqdm(sentences):
                f.write(json.dumps(sentence, default=pydantic_encoder) + "\n")
        return f"{self.out_db.db}/{file_name}.{_type}"

    def _transform_clinical_notes_to_sentences(self, notes: List[AnnotatedClinicalNote]) -> List[AnnotatedSentence]:
        # Transform clinical notes into sentences with annotations
        sentences = []
        maxlen = 0
        for note in tqdm.tqdm(notes):
            sentences_ = self.sentence_extractor.extract_sentences(note.text)
            id = 0
            tags = note.annotations
            for sentence in sentences_:
                sent = sentence
                presented_tags = []
                for i in range(len(tags)):
                    if tags[i].token in sent:
                        presented_tags.append(tags[i])
                        sent = sent.replace(tags[i].token, "{" * len(tags[i].token), 1)
                    else:
                        tags = tags[i:]
                        break
                annotations = convert_human_readable_to_machine_readable_annotations(
                    sentence=sentence, tags=presented_tags
                )
                sentences.append(
                    AnnotatedSentence(
                        text=sentence,
                        sentence_id_in_note=id,
                        major_section="",
                        associated_note_id=note.note_id,
                        note_type=note.note_type,
                        date=note.date,
                        patient_id=note.patient_id,
                        metadata=note.metadata,
                        annotations=Annotations(
                            annotation_source="Manual",
                            annotations=annotations,
                        ),
                    )
                )
                id += 1
                maxlen = max(maxlen, len(sentence.split(" ")))
        logger.info(f"Max length of sentence: {maxlen}")
        return sentences

    def _read_ndjson_file_and_return_clinicalnotes(self, file_path: str) -> List[AnnotatedClinicalNote]:
        # Read ndjson file and return list of clinical notes
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")
        notes = []
        with open(file_path, "r") as f:
            for line in tqdm.tqdm(f, desc="Processing lines"):
                note = AnnotatedClinicalNote.model_validate_json(line)
                notes.append(note)
        return notes

if __name__ == "__main__":
    # Run the ETL process
    ConfigureLogging()
    etl1 = AnnotatedClinicalNotesToSnetences(cli_tokens=sys.argv[1:])
    asyncio.run(etl1.run())