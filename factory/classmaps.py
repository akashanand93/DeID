from etls.dataset_to_clinicalnotes.unannotated_xml_i2b2_2006_to_clinicalnotes import (
    UnannotatedI2B2ToClinicalNotes,
)
from etls.dataset_to_clinicalnotes.annotated_xml_i2b2_2006_to_clinicalnotes import (
    AnnotatedI2B2ToClinicalNotes,
)
from etls.dataset_to_clinicalnotes.xml_i2b2_2014_dataset_to_clinicalnotes import (
    I2B22014ToClinicalNotes,
)
from etls.clinicalnotes_to_sentences.unannotated_clinicalnotes_to_sentences import (
    UnannotatedClinicalNotesToSnetences,
)
from etls.clinicalnotes_to_sentences.annotated_clinicalnotes_to_sentences import (
    AnnotatedClinicalNotesToSnetences,
)
from etls.sentences_to_annotations.unannotated_sentences_to_annotations_2006i2b2 import (
    UnannotatedSnetencesTagging2006i2b2,
)
from etls.sentences_to_annotations.annotated_sentences_to_annotations_2006i2b2 import (
    AnnotatedSnetencesTagging2006i2b2,
)
from etls.annotations_to_doccano_annotations.annotated_sentences_to_doccano_annotations import (
    AnnotatedSnetencesToDoccano,
)
from etls.annotations_to_doccano_annotations.compare_sentence_annotations_to_doccano_annotations import (
    CompareSentenceAnnotationsToDoccano,
)
from etls.sentences_to_annotations.annotated_sentences_to_annotations_2014i2b2 import (
    AnnotatedSnetencesTagging2014i2b2
)

# import the sentence extractors
from algos.sentence_extractor.basic import BasicSentanceExtractor
from algos.sentence_extractor.spacy_with_basic import (
    SpacyWithBasicSentenceExtractor,
)
from algos.sentence_extractor.spacy import SpacySentenceExtractor

# import the sentence tagging
from algos.sentence_tagging.gpt import TaggingSentenceByGPT


class ClassMappings:
    # make static maps
    etl_class_map = {
        "unannotated_raw_clinical_notes_i2b2_2006": UnannotatedI2B2ToClinicalNotes,
        "annotated_raw_clinical_notes_i2b2_2006": AnnotatedI2B2ToClinicalNotes,
        "annotated_clinical_notes_i2b2_2014": I2B22014ToClinicalNotes,
        "unannotated_clinical_notes_to_sentences": UnannotatedClinicalNotesToSnetences,
        "annotated_clinical_notes_to_sentences": AnnotatedClinicalNotesToSnetences,
        "unannotated_sentences_tagging_2006i2b2": UnannotatedSnetencesTagging2006i2b2,
        "annotated_sentences_tagging_2006i2b2": AnnotatedSnetencesTagging2006i2b2,
        "annotated_sentences_to_doccano_annotations": AnnotatedSnetencesToDoccano,
        "compare_sentence_annotations_to_doccano_annotations": CompareSentenceAnnotationsToDoccano,
        "annotated_sentences_tagging_2014i2b2": AnnotatedSnetencesTagging2014i2b2,
    }

    algo_sentence_extractor_map = {
        "basic": BasicSentanceExtractor,
        "spacy_with_basic": SpacyWithBasicSentenceExtractor,
        "spacy": SpacySentenceExtractor,
    }

    algo_sentence_tagging_map = {
        "gpt": TaggingSentenceByGPT,
    }

    models_map = {
        "gpt-4o": "gpt-4o",
        "gpt-3.5-turbo": "gpt-3.5-turbo",
    }

    # Function that takes a key and returns the class from class_map
    @staticmethod
    def get_etl_class(etl: str):
        # exit with error if etl not in class_map
        if etl not in ClassMappings.etl_class_map:
            raise ValueError(f"ETL {etl} not found in class_map")
        return ClassMappings.etl_class_map[etl]
