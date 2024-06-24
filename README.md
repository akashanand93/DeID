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
    <img src="https://github.com/caresage/DeID/assets/91689859/00bde1c4-9233-4ddb-a2e2-96a264cfb01c" alt="Workflow architecture of DeID methodology">
    </p>
    <p align="center">
    <i>Figure 1: Workflow architecture of DeID methodology.</i>
    </p>


## Setup
1. Clone the repository
```bash
git clone https://github.com/caresage/DeID.git
```
2. Create a virtual environment using the following command:
```bash
python -m venv [env_name]
```
3. Activate it using the following command:
```bash
source ./[env_name]/bin/activate
```
4. Install the required packages using the following command:
```bash
pip install -r requirements.txt
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

 Here we have provided ETLS that are based on I2B2 datasets: 2006 DeID SmokingStatus and 2014 DeID heart disease   

> [!IMPORTANT]  
> *To run complete workflow, follow the below stepwise instructions:*


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
│   ├── I2B2Data
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
  
  - etl: 'annotated_raw_clinical_notes_i2b2_2006'
    root: 'data'
    factory: 'dataset_to_clinicalnotes'
    inp-file: '2006_annotated.xml'
    out-file: '2006_annotated_clinicalnote.ndjson'

  - etl: 'unannotated_raw_clinical_notes_i2b2_2006'
    root: 'data'
    factory: 'dataset_to_clinicalnotes'
    inp-file: '2006_unannotated.xml'
    out-file: '2006_unannotated_clinicalnote.ndjson'

  - etl: 'annotated_clinical_notes_i2b2_2014'
    root: 'data'
    factory: 'dataset_to_clinicalnotes'
    inp-file: '2014.xml'
    out-file: '2014_clinicalnote.ndjson'
```

Run the ETL using the following command:
```bash
python utils/yamlrunner.py --config_file configs/dataset_to_clinicalnotes.yaml
```

After runnig above command ```clnicalnotes``` directory will be created inside ```root``` directory and extracted clinical notes will be presented in ```{root}/clnicalnotes``` as ndjson format.  

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

  - etl: 'annotated_clinical_notes_to_sentences'
    root: 'data'
    factory: 'clinicalnotes_to_sentences'
    inp-file: '2006_annotated_clinicalnote.ndjson'
    out-file: '2006_annotated_clinicalsentences.ndjson'
    sentence-extractor: 'spacy_with_basic' 

  - etl: 'annotated_clinical_notes_to_sentences'
    root: 'data'
    factory: 'clinicalnotes_to_sentences'
    inp-file: '2014_clinicalnote.ndjson'
    out-file: '2014_clinicalsentences.ndjson'
    sentence-extractor: 'spacy_with_basic' 

  - etl: 'unannotated_clinical_notes_to_sentences'
    root: 'data'
    factory: 'clinicalnotes_to_sentences'
    inp-file: '2006_unannotated_clinicalnote.ndjson'
    out-file: '2006_unannotated_clinicalsentences.ndjson' 
    sentence-extractor: 'spacy_with_basic'
```

Run the ETL using the following command:
```bash
python utils/yamlrunner.py --config_file configs/clinicalnotes_to_sentences.yaml
```

After runnig above command ```clnicalsentences``` directory will be created inside ```root``` directory and extracted sentences from clinical notes will be presented in ```{root}/clnicalsentences``` as ndjson format.  


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

  - etl: 'unannotated_sentences_tagging_2006i2b2'
    root: 'data'
    factory: 'sentences_to_annotations'
    inp-file: '2006_unannotated_clinicalsentences.ndjson'
    out-file: '2006_unannotated_taggedsentences.ndjson'
    sentence-tagging: 'gpt'  
    model: "gpt-4o"   

  - etl: 'annotated_sentences_tagging_2006i2b2'
    root: 'data'
    factory: 'sentences_to_annotations'
    inp-file: '2006_annotated_clinicalsentences.ndjson'
    out-file: '2006_annotated_taggedsentences.ndjson'
    sentence-tagging: 'gpt' 
    model: "gpt-4o"  

  - etl: 'annotated_sentences_tagging_2014i2b2'
    root: 'data'
    factory: 'sentences_to_annotations'
    inp-file: '2014_clinicalsentences.ndjson'
    out-file: '2014_taggedsentences.ndjson'
    sentence-tagging: 'gpt'  
    model: "gpt-4o"  
```
For runnig the ETLs first put your OPENAI_API_KEY inside _secrets/.env file
```bash
OPENAI_API_KEY=your_openai_api_key
```
Then run the following command:
```bash
python utils/yamlrunner.py --config_file configs/sentences_to_annotations.yaml
```

After runnig above command ```taggedsentences(machine_readable)``` directory will be created inside ```root``` directory and tagged sentences in **machine readable** format will be presented in ```{root}/taggedsentences(machine_readable)``` as ndjson format.  
> [!NOTE]  
> **machine readable** format: machine readable format is BI tagging format.   
> - This is the simplest form of tagging where each token from a sentence is assigned one of two tags: Beging tag (B) or Intermediate tag (I).  
> - If a token is an entity, it is tagged as B or else as I. For example:
> ![image](https://github.com/caresage/DeID/assets/91689859/2f0a4d34-341d-43bc-938f-bf0205ade26e)


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
You will have to pass input file path for which you want to find accuracy. It will be out-file from tagging process. Run the following command to evaluate the GPT annotation with respect to ground truth annotations:
```bash
python scripts/accuracy_on_tagged_data.py -r "path/to/root/directory" -i "path/to/tagged/sentences/file/of/type/ndjson" -d "dataset/type/write/only/2006/or/2014"
```

After runnig above command ```metrics``` directory will be created inside ```root``` directory mismatched tags with their sentences presented in ```{root}/metrics```  as ndjson format. This ndjson format will be readable format. You will also see the bar plot of each categories.
> [!NOTE]  
> **doccano readable** format:   
> ![Screenshot from 2024-06-24 13-21-00](https://github.com/caresage/DeID/assets/91689859/7eb3e128-9d28-4d09-9238-c0cef650984b)

### 5. Visulization of GPT annotation and ground truth annotation on doccano server
- You can visulize two types of data on doccano:
    - Complete dataset with LLM based annotations and ground truth annotations (need to convert into doccano format)
    - Only missmatched annotations between LLM based annotations and ground annotations (already in doccano format)

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

  - etl: 'annotated_sentences_to_doccano_annotations'
    root: 'data'
    factory: "annotations_to_doccano_annotations"
    inp-file: '2006_unannotated_taggedsentences.ndjson'
    out-file: '2006_unannotated_taggedsentences.ndjson'

  - etl: 'compare_sentence_annotations_to_doccano_annotations'
    root: 'data'
    factory: "annotations_to_doccano_annotations"
    inp-file: '2006_annotated_taggedsentences.ndjson'
    out-file: '2006_annotated_taggedsentences.ndjson'

  - etl: 'compare_sentence_annotations_to_doccano_annotations'
    root: 'data'
    factory: "annotations_to_doccano_annotations"
    inp-file: '2014_taggedsentences.ndjson'
    out-file: '2014_taggedsentences.ndjson'
```

Run the ETL using the following command:
```bash
python utils/yamlrunner.py --config_file configs/annotations_to_doccano.yaml
```

After runnig above command ```taggedsentences(human_readable)``` and ```taggedsentences(doccano_readable)``` directories will be created inside ```root``` directory. Tagged sentences in **human readable** will be present in ```{root}/taggedsentences(human_readable)``` as ndjson format. Tagged sentences in **doccano readable** will be present in ```{root}/taggedsentences(doccano_readable)``` as ndjson format.   
> [!NOTE]  
> **human readable** format:   
> ![image](https://github.com/caresage/DeID/assets/91689859/0ae002e7-7b94-4946-a00f-e260b2afacb4)


You can upload data on doccano using doccano API. For that first you have to put your DOCCANO_URL, DOCCANO_USER_NAME and DOCCANO_PASSWORD into _secrets.env file. 
> [!WARNING]  
> Don't paste your local host doccano url in DOCCANO_URL, insted put deployed doccano url.  

Then you can run the following command:  
```bash
python scripts/upload_data_on_doccano.py -i "path/to/visulized/data/of/type/ndjson" -p "project_name" -d "project_description"
```  
> [!NOTE]  
> If you don't have deployed link of your doccano then you can also upload data on doccano. For that you don't need to run above python command. You can manually import dataset on doccano. You can go through below tutorial:  
> - *Here is the  github link to setup a doccano on your local machine :  [doccano-setup](https://github.com/doccano/doccano/)*
> - *Here is the tutorial for visulizing data on doccano : [doccano-tutorial](https://doccano.github.io/doccano/tutorial/)*

> [!TIP]  
> Now open doccano and visulize the sentence annotation and mismatches also! After then you can refine the prompt, model, algorithm etc. according to mismatches/errors to increase accuracy.

