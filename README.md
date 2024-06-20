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
git clone
```
2. Create a virtual environment using the following command:
```bash
python -m venv [env_name]
```
3. Install the required packages using the following command:
```bash
pip install -r requirements.txt
```
