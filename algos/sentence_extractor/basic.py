from typing import List
from abc import ABC, abstractmethod

# Define an abstract base class for sentence extraction
class BasicSentanceExtractor(ABC):

    # Abstract method for extracting sentences from a note
    @abstractmethod
    def extract_sentences(self, note: str) -> List[str]:
        # Split the note into sentences based on ' . ' delimiter
        sentences = note.split(" . ")
        sentences_ = []
        
        # Iterate through each sentence fragment
        for i in range(len(sentences)):
            # Check if the fragment is a single word
            if len(sentences[i].split()) == 1:
                # Append single-word fragment to the previous sentence
                sentences_[-1] = sentences_[-1] + " " + sentences[i]
            else:
                # Add the fragment as a new sentence
                sentences_.append(sentences[i])
                
        # Return the list of processed sentences
        return sentences_
