import spacy
from algos.sentence_extractor.basic import BasicSentanceExtractor
from typing import List

class SpacyWithBasicSentenceExtractor(BasicSentanceExtractor):
    def __init__(self):
        super().__init__()
        self.nlp = spacy.load("en_core_web_sm")

    def extract_sentences(self, note: str) -> List[str]:
        # Split the input note into potential sentences using " . " as the delimiter
        sents = note.split(" . ")
        sentences = []

        for s in sents:
            # If the potential sentence is longer than 100 words, use spaCy to split it further
            if len(s.split()) > 100:
                doc = self.nlp(s)
                sentences.extend([st.text for st in doc.sents])
            else:
                sentences.append(s)
        
        # Combine very short sentences (likely artifacts of the initial split) with the preceding sentence
        refined_sentences = []
        for sentence in sentences:
            if refined_sentences and len(sentence.split()) == 1:
                refined_sentences[-1] += " " + sentence
            else:
                refined_sentences.append(sentence)

        return refined_sentences
