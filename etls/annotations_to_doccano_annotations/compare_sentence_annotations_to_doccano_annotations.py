import asyncio
import sys
import json
from etl.utils.dfutils import LakeDB
from utils.constants import DataConstants
from models.model import (
    Annotations,
    CompareSentenceAnnotations,
)
from etls.DSETL import DSETL
from typing import List
from common.utils.log import ConfigureLogging
from pydantic.json import pydantic_encoder
from loguru import logger
import os
from scripts.post_processing_of_tagged_sentences import (
    convert_machine_readable_to_human_readable_annotations,
    convert_human_readable_to_doccano_annotations_in_ndjson,
    write_doccano_tagged_sentences,
)
import tqdm


class CompareSentenceAnnotationsToDoccano(
    DSETL[CompareSentenceAnnotations, CompareSentenceAnnotations]
):
    # Default output directories for human-readable and Doccano formats
    DEFAULT_OPTIONS = {
        "out-dir-human": DataConstants.TAGGED_SENTECNES_HUMAN_DIR,
        "out-dir-doccano": DataConstants.TAGGED_SENTECNES_DOCCANO_DIR,
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
        self.out_dir_human = self.options["out-dir-human"]
        self.out_dir_doccano = self.options["out-dir-doccano"]
        self.out_db = LakeDB(self.out_dir_human)
        os.makedirs(self.out_dir_human, exist_ok=True)
        os.makedirs(self.out_dir_doccano, exist_ok=True)

    async def extract(self) -> List[CompareSentenceAnnotations]:
        # step1: Read ndjson file from inp_db
        ts = self._read_ndjson_file_and_return_sentences(self.inp_file_path)
        logger.success(f"Reading Done...  from file {self.inp_file_path}")
        return ts

    async def transform(
        self, data: List[CompareSentenceAnnotations]
    ) -> List[CompareSentenceAnnotations]:
        # Transform clinical notes to sentences
        ts = self._transform_tagged_sentences_to_humman_readable_tagged_sentences(data)
        logger.success(f"Sentences Tagging Done...  from file {self.inp_file_path}")
        return ts

    async def load(self, data: List[CompareSentenceAnnotations]):
        # dump in outfile.ndjson format
        file_saved = self._write_tagged_sentences(data, self.file_name)
        logger.success(f"Loaded {len(data)} to file {file_saved}")
        return

    def _write_tagged_sentences(
        self,
        sentences: List[CompareSentenceAnnotations],
        file_name: str,
        _type="ndjson",
    ) -> None:
         # Write sentences to an NDJSON file
        if _type != "ndjson":
            raise ValueError("Only 'ndjson' type is supported")
        with open(f"{self.out_db.db}/{file_name}.{_type}", "w") as f:
            for sentence in tqdm.tqdm(sentences):
                f.write(json.dumps(sentence, default=pydantic_encoder) + "\n")
        return f"{self.out_db.db}/{file_name}.{_type}"

    def _transform_tagged_sentences_to_humman_readable_tagged_sentences(
        self, sentences: List[CompareSentenceAnnotations]
    ) -> List[CompareSentenceAnnotations]:
        # Convert machine-readable annotations to human-readable format and save
        human_annotated_snetences = []
        doccano_manual_annotated_sentences = []
        doccano_gpt_annotated_sentences = []

        for sentence in tqdm.tqdm(sentences):
            manual_annotations = convert_machine_readable_to_human_readable_annotations(
                sentence=sentence.text, tags=sentence.annotations.annotations
            )
            gpt_annotations = convert_machine_readable_to_human_readable_annotations(
                sentence=sentence.text, tags=sentence.secondary_annotations.annotations
            )
            doccano_manual_annotated_sentences.append(
                convert_human_readable_to_doccano_annotations_in_ndjson(
                    sentence=sentence.text,
                    tags=manual_annotations,
                    _tag_source=sentence.annotations.annotation_source,
                    id=sentence.sentence_id_in_note,
                )
            )
            doccano_gpt_annotated_sentences.append(
                convert_human_readable_to_doccano_annotations_in_ndjson(
                    sentence=sentence.text,
                    tags=gpt_annotations,
                    _tag_source=sentence.secondary_annotations.annotation_source,
                    id=sentence.sentence_id_in_note,
                )
            )
            human_annotated_snetences.append(
                CompareSentenceAnnotations(
                    text=sentence.text,
                    sentence_id_in_note=sentence.sentence_id_in_note,
                    major_section=sentence.major_section,
                    associated_note_id=sentence.associated_note_id,
                    note_type=sentence.note_type,
                    date=sentence.date,
                    patient_id=sentence.patient_id,
                    metadata=sentence.metadata,
                    annotations=Annotations(
                        annotation_source=sentence.annotations.annotation_source,
                        annotations=manual_annotations,
                    ),
                    secondary_annotations=Annotations(
                        annotation_source=sentence.secondary_annotations.annotation_source,
                        annotations=gpt_annotations,
                    ),
                )
            )
        write_doccano_tagged_sentences(
            sentences1=doccano_manual_annotated_sentences,
            file_path=self.out_dir_doccano,
            file_name=self.file_name,
            _type="ndjson",
            sentences2=doccano_gpt_annotated_sentences,
        )
        return human_annotated_snetences

    def _read_ndjson_file_and_return_sentences(
        self, file_path: str
    ) -> List[CompareSentenceAnnotations]:
        # Read NDJSON file and return list of sentences
        sentences = []
        with open(file_path, "r") as f:
            for line in tqdm.tqdm(f, desc="Processing lines"):
                sentence = CompareSentenceAnnotations.model_validate_json(line)
                sentences.append(sentence)
        return sentences


if __name__ == "__main__":
    # Run the ETL process for the first type
    ConfigureLogging()
    etl1 = CompareSentenceAnnotationsToDoccano(cli_tokens=sys.argv[1:])
    asyncio.run(etl1.run())
