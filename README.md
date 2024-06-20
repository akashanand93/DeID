# DeID
## LLM based DeID algorithm
This is a simple implementation of a DeID algorithm using a Language Model (LLM) to identify Protected Health Information (PHI) in clinical text. The algorithm uses a pre-trained LLM (in this case, GPT-4) to identify PHI entities. 
Our primary approach is to utilize API access and manual testing to evaluate ChatGPT (powered by GPT-3.5) and GPT-4’s (through OpenAI’s web interface that is shared with ChatGPT) performance on anonymizing clinical notes. We will describe our entire workflow in detail, from the data preprocessing to evaluation. Below figure represents the complete workfow architecture of our methodology. This workflow consist of,
1. Extraction of clinical notes from raw xml files.
2. Sentences Extraction from parsed clinical notes.
3. Using GPT, annotate the extracted sentences.
4. Evaluation of the GPT annotation with respect to ground truth annotations.
5. Visulization of GPT annotation and ground truth annotation on doccano server.

    ![image](https://github.com/caresage/DeID/assets/91689859/66bee7d0-ef7f-47e9-852b-b5f94d994a62)

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
