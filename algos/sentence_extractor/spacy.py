import spacy
from algos.sentence_extractor.basic import BasicSentanceExtractor
from typing import List

# Define a class SpacySentenceExtractor inheriting from BasicSentanceExtractor
class SpacySentenceExtractor(BasicSentanceExtractor):
    # Initialize the Spacy model
    def __init__(self):
        super().__init__()
        self.nlp = spacy.load("en_core_web_sm")

    # Method to extract sentences from a given note
    def extract_sentences(self, note: str) -> List[str]:
        sentences_doc = self.nlp(note)
        # Extract sentences from the processed note
        sentences = [sentence.text for sentence in sentences_doc.sents]
        return sentences
