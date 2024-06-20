from pydantic import BaseModel
from typing import List


class SingleAnnotation(BaseModel):
    token: str
    start_index: int
    end_index: int
    type: str


class Annotations(BaseModel):
    annotation_source: str
    annotations: List[SingleAnnotation]


class ClinicalNote(BaseModel):
    text: str
    note_type: str
    date: str
    patient_id: str
    note_id: str
    metadata: dict


class AnnotatedClinicalNote(ClinicalNote):
    annotations: List[SingleAnnotation]


class Sentence(BaseModel):
    text: str
    sentence_id_in_note: int
    major_section: str
    associated_note_id: str
    note_type: str
    date: str
    patient_id: str
    metadata: dict


class AnnotatedSentence(Sentence):
    annotations: Annotations


class CompareSentenceAnnotations(AnnotatedSentence):
    secondary_annotations: Annotations


class UserInfo2006i2b2(BaseModel):
    patients: list[str]
    doctors: list[str]
    hospitals: list[str]
    ids: list[str]
    dates: list[str]
    locations: list[str]
    phone_numbers: list[str]
    ages: list[str]

class UserInfo2014i2b2(BaseModel):
    names: list[str]
    locations: list[str]
    ages: list[str]
    ids: list[str]
    dates: list[str]
    contacts: list[str]
    professions: list[str]