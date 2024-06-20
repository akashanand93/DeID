# DeID
## LLM based DeID algorithm
This is a simple implementation of a DeID algorithm using a Language Model (LLM) to identify Protected Health Information (PHI) in clinical text. The algorithm uses a pre-trained LLM (in this case, GPT-4) to identify PHI entities. 
The algorithm consists of the following steps:
1. Parsing clinical notes from xml files
2. Extract sentences from clinical notes
3. Annotate each extracted sentences using LLMs
4. Visulize annotation on doccano server

## Setup
1. Clone the repository
<!-- cloning code -->
```bash
git clone https://github.com/caresage/DeID.git
```
2. Create a virtual environment using the following command:
```bash
python -m venv [env_name]
```
3. Install the required packages using the following command:
```bash
pip install -r requirements.txt
```
4. Setup some paths into utils/constants.py
```python
# Path to the directory containing the clinical notes after parsing from xml file
DEID_PROCESSED_DIR = ""
# Path to the directory containing the extracted sentences from the clinical notes
PROCESSED_SENTENCES_DIR = ""
# Path to the directory containing the tagged sentences in machine readable (CoNLL)formate 
# For example: B-NAME, I-NAME, B-ORG....
TAGGED_SENTECNES_MACHINE_DIR = ""
# Path to the directory containing the tagged sentences in human readable formate
# For example: NAME, ORG, DATE....
TAGGED_SENTECNES_HUMAN_DIR = ""
# Path to the directory containing the tagged sentences to be uploaded in doccano server
TAGGED_SENTECNES_DOCCANO_DIR = ""
# Path to the directory containing the metrics of the model like accuracy, plots, confusion matrix etc.
METRICS_DIR = ""
```
