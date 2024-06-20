# DeID
## LLM based DeID algorithm
This is a simple implementation of a DeID algorithm using a Language Model (LLM) to identify Protected Health Information (PHI) in clinical text. The algorithm uses a pre-trained LLM (in this case, GPT-4) to identify PHI entities. 
Our primary approach is to utilize API access and manual testing to evaluate ChatGPT (powered by GPT-3.5) and GPT-4’s (through OpenAI’s web interface that is shared with ChatGPT) performance on anonymizing clinical notes. We will describe our entire workflow in detail, from the data preprocessing to evaluation. Below figure represents the complete workfow architecture of our methodology. This workflow consist of,
1. Extraction of clinical notes from raw xml files.
2. Sentences Extraction from parsed clinical notes.
3. Using GPT, annotate the extracted sentences.
4. Evaluation of the GPT annotation with respect to ground truth annotations.
5. Visulization of GPT annotation and ground truth annotation on doccano server.

    <p align="center">
    <img src="https://github.com/caresage/DeID/assets/91689859/66bee7d0-ef7f-47e9-852b-b5f94d994a62" alt="Workflow architecture of DeID methodology">
    </p>
    <p align="center">
    <i>Figure 1: Workflow architecture of DeID methodology.</i>
    </p>


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
4. Setup some paths into constants.py   
```bash  
DeID  
├── ...  
├── models  
├── scripts  
├── utils
│   ├── constants.py  # setup paths in this file
│   ├── prompt.py                           
│   └── yamlrunner.py  
└── ...  
```

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

# Path to the directory containing the mismatched tages with sentences, plots, accuracy etc.
METRICS_DIR = ""
```

## Usage (Workflow)
There are different ETLs written for processing differnt types of datasets availabe for each process mentioned above in workflow architecture. Use ETL corresponds to your datset and your process. you can also make your own ETL for your dataset or process. Don't forget to map your ETLs in basicfactory.py and classmaps.py 
```bash  
DeID  
├── ...  
├── etls
├── factory
│   ├── basicfactory.py   # factory mappings (like algorithmns, models that we want to use..)
│   └── classmaps.py      # etl mappings 
├── models
└── ...  
```

 Here we have provided ETLS that are based on I2B2 datasets: **2006 DeID SmokingStatus** and **2014 DeID heart disease**   

*To run complete workflow, follow the below stepwise instructions:*

### 1. Extraction of clinical notes from raw xml files
- There will be two types of clinical notes present in xml files of I2B2 dataset: 
    - Only clinical notes (Present in only 2006 DeID SmokingStatus)
    - Clinical notes with ground truth annotations (Present in both 2006 DeID SmokingStatus and 2014 DeID heart disease) 
- There are also different ETLs for each of the above types for a perticular dataset. 
- Update dataset_to_clinicalnotes.yaml file with your raw dataset paths.
```bash  
DeID  
├── ...  
├── configs
│   ├── annotations_to_doccano.yaml
│   ├── clinicalnotes_to_sentences.yaml
│   ├── dataset_to_clinicalnotes.yaml     # change paths in this file
│   └── sentences_to_annotations.yaml
├── data
│   ├── SampleI2B2Data
│   │   ├── 2006_annotated.xml       # 2006 DeID SmokingStatus - clinical notes with groundtruth annotations
│   │   ├── 2006_unannotated.xml     # 2006 DeID SmokingStatus - only clinical notes
│   │   └── 2014.xml                 # 2014 DeID heart disease - clinical notes with groundtruth annotations    
├── etl 
├── etls
│   ├── annotations_to_doccano_annotations
│   ├── clinicalnotes_to_sentences
│   ├── dataset_to_clinicalnotes
│   │   ├── annotated_xml_i2b2_2006_to_clinicalnotes.py        # mapped with annotated_raw_clinical_notes_i2b2_2006 
│   │   ├── unannotated_xml_i2b2_2006_to_clinicalnotes.py.py   # mapped with unannotated_raw_clinical_notes_i2b2_2006
│   │   └── xml_i2b2_2014_to_clinicalnotes.py                  # mapped with annotated_clinical_notes_i2b2_2014
│   └── sentences_to_annotations
├── factory
└── ...  
```
you can set up as many as ETLs that you want to run for extracting clinical notes from xml file in *dataset_to_clinicalnotes.yaml:*
```yaml
serialize:

# for extracting clinical notes from any 2006 DeID SmokingStatus (clinical notes with groundtruth annotations) datasets
  - etl: 'annotated_raw_clinical_notes_i2b2_2006'
    factory: 'dataset_to_clinicalnotes'
    inp-file: 'data/SampleI2B2Data/2006_annotated.xml'
    out-file: 'copy_DEID_PROCESSED_DIR_name_from_constant.py/2006_annotated.ndjson'

# for extracting clinical notes from any 2006 DeID SmokingStatus (only clinical notes) datasets
  - etl: 'unannotated_raw_clinical_notes_i2b2_2006'
    factory: 'dataset_to_clinicalnotes'
    inp-file: 'data/SampleI2B2Data/2006_unannotated.xml'
    out-file: 'copy_DEID_PROCESSED_DIR_name_from_constant.py/2006_unannotated.ndjson'

# for extracting clinical notes from any 2014 DeID heart disease dataets
  - etl: 'annotated_clinical_notes_i2b2_2014'
    factory: 'dataset_to_clinicalnotes'
    inp-file: 'data/SampleI2B2Data/2014.xml'
    out-file: 'copy_DEID_PROCESSED_DIR_name_from_constant.py
```

Run the ETL using the following command:
```bash
python utils/yamlrunner.py --config_file configs/dataset_to_clinicalnotes.yaml
```

After runnig above command you will have extracted clinical notes presented in **DEID_PROCESSED_DIR** as ndjson formate.  
(Basically extracted clinical notes will present in **out-file** paths from *dataset_to_clinicalnotes.yaml*)

### 2. Sentences Extraction from parsed clinical notes
- There are too many algorithms to perform sentence tokenization from clinical notes. We have implemented 3 different algorithmns to extract sentence. You can also implement your own sentence tokenization algorithm and put it into algos/sentence_extractor and chnage the code in ETLs that pointing the specific algorithm. Don't forget to map your algorithms in basicfactory.py and classmaps.py
- There are also different ETLs for extracting sentences from:
    - Clinical notes - with ground annotation present
    - Only clinical notes
- Update clinicalnotes_to_sentences.yaml file with your clinical notes dataset paths.
```bash
DeID
├── ...
├── algos
│   ├── sentence_extractor   # put your algorithms here
│   │   ├── basic.py  
│   │   ├── spacy_with_basic.py
│   │   └── spacy_with_basic.py    
│   └── sentence_tagging
├── configs
│   ├── annotations_to_doccano.yaml
│   ├── clinicalnotes_to_sentences.yaml   # change paths in this file
│   ├── dataset_to_clinicalnotes.yaml
│   └── sentences_to_annotations.yaml
├── data   
├── etl 
├── etls
│   ├── annotations_to_doccano_annotations
│   ├── clinicalnotes_to_sentences
│   │   ├── annotated_clinicalnotes_to_sentences.py     # mapped with annotated_clinicalnotes_to_sentences
│   │   ├── unannotated_clinicalnotes_to_sentences.py   # mapped eith unannotated_clinicalnotes_to_sentences
│   ├── dataset_to_clinicalnotes
│   └── sentences_to_annotations
├── factory
│   ├── basicfactory.py   # factory mappings (like algorithmns, models that we want to use..)
│   └── classmaps.py      # etl mappings 
├── models
└── ...
```
you can set up as many as ETLs that you want to run for extracting sentences from clinical notes in *clinicalnotes_to_sentences.yaml:*
```yaml
serialize:

# for extracting sentences from any clinical notes - with ground annotation datasets
- etl: 'annotated_clinicalnotes_to_sentences'
    factory: 'clinicalnotes_to_sentences'
    inp-file: 'copy_DEID_PROCESSED_DIR_name_from_constant.py/2006_annotated.ndjson'
    out-file: 'copy_PROCESSED_SENTENCES_DIR_name_from_constant.py/2006_annotated.ndjson'
    sentence-extractor: 'spacy_with_basic'  # you can replace it with your(any) algoritm

- etl: 'annotated_clinicalnotes_to_sentences'
    factory: 'clinicalnotes_to_sentences'
    inp-file: 'copy_DEID_PROCESSED_DIR_name_from_constant.py/2014.ndjson'
    out-file: 'copy_PROCESSED_SENTENCES_DIR_name_from_constant.py/2014.ndjson'
    sentence-extractor: 'spacy_with_basic'  # you can replace it with your(any) algoritm

# for extracting sentences from any clinical notes - only clinical notes datasets
- etl: 'unannotated_clinicalnotes_to_sentences'
    factory: 'clinicalnotes_to_sentences'
    inp-file: 'copy_DEID_PROCESSED_DIR_name_from_constant.py/2006_unannotated.ndjson'
    out-file: 'copy_PROCESSED_SENTENCES_DIR_name_from_constant.py/2006_unannotated.ndjson' 
    sentence-extractor: 'spacy_with_basic'  # you can replace it with your(any) algoritm
```

Run the ETL using the following command:
```bash
python utils/yamlrunner.py --config_file configs/clinicalnotes_to_sentences.yaml
```

After runnig above command you will have extracted sentences from clinical notes presented in **PROCESSED_SENTENCES_DIR** as ndjson formate.  
(Basically extracted sentences will present in **out-file** paths from *clinicalnotes_to_sentences.yaml*)


### 3. Using GPT, annotate the extracted sentences
- There are too many algorithms to perform sentence tagging. We have implemented algorithmns to tag sentence based on GPT models. You can also implement your own sentence tagging algorithm and put it into algos/sentence_tagging and chnage the code in ETLs that pointing the specific algorithm. Don't forget to map your algorithms in basicfactory.py and classmaps.py
- Here We are using "gpt-4o" model. You can use other models like "gpt-4", "gpt-3.5-turbo", "gpt-3" etc. Don't forget to map your models in basicfactory.py and classmaps.py
- Since we are using GPT based algorithm to tag sentence, there will be also a requirement of prompt. Prompts are present in utils/prompt.py. You can modified prompt according to your dataset and process. But Don't forget to import it in neccesary places.
- There are also different ETLs for tagging sentences from:
    - Sentences - with ground annotation present
    - Only Sentences
- There are also different ETLs for each of the above types for a perticular dataset. 
- Since we are extracting structured information from clinical sentences, you can change your model(structure) in models/model.py for different datasets.
- Update sentences_to_annotations.yaml file with your sentences dataset paths.
```bash
DeID
├── ...
├── algos
│   ├── sentence_extractor
│   └── sentence_tagging   # put your algorithms here
│       └── gpt.py
├── configs
│   ├── annotations_to_doccano.yaml
│   ├── clinicalnotes_to_sentences.yaml
│   ├── dataset_to_clinicalnotes.yaml
│   └── sentences_to_annotations.yaml   # change paths in this file
├── data
├── etl
├── etls
│   ├── annotations_to_doccano_annotations
│   ├── clinicalnotes_to_sentences
│   ├── dataset_to_clinicalnotes
│   ├── sentences_to_annotations
│   │   ├── annotated_sentences_to_annotations_2006i2b2.py    # mapped with annotated_sentences_tagging_2006i2b2
│   │   ├── annotated_sentences_to_annotations_2014i2b2.py    # mapped with annotated_sentences_tagging_2014i2b2
│   │   └── unannotated_sentences_to_annotations_2006i2b2.py  # mapped with unannotated_sentences_tagging_2006i2b2
├── factory
│   ├── basicfactory.py   # factory mappings (like algorithmns, models that we want to use..)
│   └── classmaps.py      # etl mappings
├── models
│   └── model.py   # change your model(structure)
├── scripts
└── ...
```

you can set up as many as ETLs that you want to run for tagging sentences from clinical notes in *sentences_to_annotations.yaml:*
```yaml
serialize:

# for tagging sentences from any 2006 DeID SmokingStatus only clinical sentences
  - etl: 'unannotated_sentences_tagging_2006i2b2'
    factory: 'sentences_to_annotations'
    inp-file: 'copy_PROCESSED_SENTENCES_DIR_name_from_constant.py/2006_unannotateds.ndjson'
    out-file: 'copy_TAGGED_SENTECNES_MACHINE_DIR_name_from_constant.py/2006_unannotated.ndjson'
    sentence-tagging: 'gpt'  # you can replace it with your(any) algorithm
    model: "gpt-4o"   # you can replace it with any model_name

# for tagging sentences from any 2006 DeID SmokingStatus clinical sentences with ground annotation
  - etl: 'annotated_sentences_tagging_2006i2b2'
    factory: 'sentences_to_annotations'
    inp-file: 'copy_PROCESSED_SENTENCES_DIR_name_from_constant.py/2006_annotated.ndjson'
    out-file: 'copy_TAGGED_SENTECNES_MACHINE_DIR_name_from_constant.py/2006_annotated.ndjson'
    sentence-tagging: 'gpt'  # you can replace it with your(any) algorithm
    model: "gpt-4o"  # you can replace it with any model_name

# for tagging sentences from any 2014 DeID heart disease clinical sentences with ground annotation
  - etl: 'annotated_sentences_tagging_2014i2b2'
    factory: 'sentences_to_annotations'
    inp-file: 'copy_PROCESSED_SENTENCES_DIR_name_from_constant.py/2014.ndjson'
    out-file: 'copy_TAGGED_SENTECNES_MACHINE_DIR_name_from_constant.py/2014.ndjson'
    sentence-tagging: 'gpt'  # you can replace it with your(any) algorithm
    model: "gpt-4o"  # you can replace it with any model_name
```
For runnig the ETLs first put your *OPENAI_API_KEY* inside _secrets/.env file
```bash
OPENAI_API_KEY=your_openai_api_key
```
Then run the following command:
```bash
python utils/yamlrunner.py --config_file configs/sentences_to_annotations.yaml
```

After runnig above command you will have tagged sentences presented in **TAGGED_SENTECNES_MACHINE_DIR** as ndjson formate.  
(Basically tagged sentences will present in **out-file** paths from *sentences_to_annotations.yaml*)

### 4. Evaluation of the GPT annotation with respect to ground truth annotations
- Evaluation script will be different for 2006 DeID SmokingStatus and 2014 DeID heart disease, because there are different PHI categories present in both dataset. So you just have to replace raw_categories array according to unique PHIs present in your dataset in the file scripts/accuracy_on_tagged_data.py.
> [!IMPORTANT]  
> This process will run only on the datasets, which have their ground truth annotations present.
```bash
DeID
├── ...
├── models
├── scripts
│   │   ├── accuracy_on_tagged_data.py    # change in this file
│   │   ├── pdf_to_text_convertor.py
│   │   ├── post_processing_of_tagged_sentences.py
│   │   ├── upload_data_on_doccano.py
│   │   ├── upload_doccano_functionalities.py
│   │   └── webscraper.py
├── utils
└── ...
```
*accuracy_on_tagged_data.py*
- For any 2006 DeID SmokingStatus datasets
```python 
raw_categories = ['NAME', 'AGE', 'DATE', 'ID', 'LOCATION', 'HOSPITAL', 'DOCTOR', 'PHONE']
```
- For any 2014 DeID heart disease datasets
```python
raw_categories = ["NAME", "LOCATION", "AGE", "ID", "DATE", "CONTACT", "PROFESSION"]
```
You will have to pass input file path for which you want to find accuracy. It will be out-file from tagging process. Run the following command to evaluate the GPT annotation with respect to ground truth annotations:
```bash
python scripts/accuracy_on_tagged_data.py -i "path/to/tagged/sentences/file/of/type/ndjson"
```

After runnig above command you will have mismatched tags with their sentences presented in **METRICS_DIR** as ndjson formate. This ndjson formate will be directly doccano visulization formate.

### 5. Visulization of GPT annotation and ground truth annotation on doccano server
- You can visulize two types of data on doccano:
    - Complete dataset with LLM based annotations and ground truth annotations (need to convert into doccano formate)
    - Only missmatched annotations between LLM based annotations and ground annotations (already in doccano formate)

- To visulize complete dataset with LLM based annotations and ground truth annotations, you will need to convert tagged sentences into doccano visulize format. So, you have to run ETLs. For that you have two ETLs:
    - Sentences with only LLM based annotations
    - Sentences with LLM based annotations and ground truth annotations present

- Update annotations_to_doccano.yaml file with your tagged sentences dataset paths.
```bash
DeID
├── ...
├── algos
├── configs
│   ├── annotations_to_doccano.yaml      # change paths in this file
│   ├── clinicalnotes_to_sentences.yaml
│   ├── dataset_to_clinicalnotes.yaml
│   └── sentences_to_annotations.yaml   
├── data
├── etl
├── etls
│   ├── annotations_to_doccano_annotations
│   │   ├── annotated_sentences_to_doccano_annotations.py             # annotated_sentences_to_doccano_annotations
│   │   └── compare_sentence_annotations_to_doccano_annotations.py    # compare_sentence_annotations_to_doccano_annotations
│   ├── clinicalnotes_to_sentences
│   ├── dataset_to_clinicalnotes
│   └── sentences_to_annotations
├── factory
└── ...
```
you can set up as many as ETLs that you want to run for visulizing data on doccano in *annotations_to_doccano.yaml:*
```yaml
serialize:

# for visulizing data on doccano with only LLM based annotations
  - etl: 'annotated_sentences_to_doccano_annotations'
    factory: "annotations_to_doccano_annotations"
    inp-file: 'copy_TAGGED_SENTECNES_MACHINE_DIR_name_from_constant.py/2006_unannotated.ndjson'
    out-file: 'copy_TAGGED_SENTECNES_DOCCANO_DIR_name_from_constant.py/2006_unannotated.ndjson'

# for visulizing data on doccano with LLM based annotations and ground truth annotations
  - etl: 'compare_sentence_annotations_to_doccano_annotations'
    factory: "annotations_to_doccano_annotations"
    inp-file: 'copy_TAGGED_SENTECNES_MACHINE_DIR_name_from_constant.py/2006_annotated.ndjson'
    out-file: 'copy_TAGGED_SENTECNES_DOCCANO_DIR_name_from_constant.py/2006_annotated.ndjson'

  - etl: 'compare_sentence_annotations_to_doccano_annotations'
    factory: "annotations_to_doccano_annotations"
    inp-file: 'copy_TAGGED_SENTECNES_MACHINE_DIR_name_from_constant.py/2014.ndjson'
    out-file: 'copy_TAGGED_SENTECNES_DOCCANO_DIR_name_from_constant.py/2014.ndjson'

```

Run the ETL using the following command:
```bash
python utils/yamlrunner.py --config_file configs/annotations_to_doccano.yaml
```

After runnig above command you will have visulized data on doccano presented in **TAGGED_SENTECNES_DOCCANO_DIR** as ndjson formate. 
(Basically visulized data will present in **out-file** paths from *annotations_to_doccano.yaml*)

- Upload data on doccano:
    - You can upload data on doccano using doccano API. For that first you have to put your DOCCANO_URL, DOCCANO_USER_NAME and DOCCANO_PASSWORD into _secrets.env file. 
        > [!WARNING]  
        > Don't paste your local host doccano url in DOCCANO_URL, insted put deployed doccano url.
    - Then you can run the following command:
        ```bash
        python scripts/upload_data_on_doccano.py -i "path/to/visulized/data/of/type/ndjson" -p "project_name" -d "project_description"
        ```
    - If you don't have deployed link of your doccano then you can also ipload data on doccano. For that you don't need to run above python command. You can manually import dataset on doccano. You can go through below tutorial:
        - Here is the  github link to setup a doccano on your local machine :  [doccano-setup](https://github.com/doccano/doccano/)
        - Here is the tutorial for visulizing data on doccano : [doccano-tutorial](https://doccano.github.io/doccano/tutorial/)

Now open doccano and visulize the sentence annotation and mismatches also! After then you can reformate the prompt, model, algorithm etc. according to mismatches/errors.

