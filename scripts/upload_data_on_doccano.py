from loguru import logger
from scripts.upload_doccano_functionalities import (
    login,
    create_project,
    process_dataset,
    upload_data,
)
from dotenv import load_dotenv
import os
import json
import argparse
from _secrets.headers import PROCESS_HEADERS, PROJECT_HEADERS, UPLOAD_HEADERS


def main(args):

    load_dotenv(dotenv_path="_secrets/.env")

    doccano_url = "https://doccano.prod.caresage.ai"
    username = os.getenv("DOCCANO_USER_NAME")
    password = os.getenv("DOCCANO_PASSWORD")

    response = login(doccano_url, username, password)
    logger.info("Login successfull........")
    print(response.json())

    project_payload = json.dumps(
        {
            "id": 0,
            "name": args.project_name,
            "description": args.project_desc,
            "guideline": "",
            "project_type": "SequenceLabeling",
            "random_order": False,
            "collaborative_annotation": False,
            "single_class_classification": False,
            "allow_overlapping": False,
            "grapheme_mode": False,
            "use_relation": False,
            "tags": [],
            "allow_member_to_create_label_type": True,
            "resourcetype": "SequenceLabelingProject",
        }
    )
    project_id = create_project(doccano_url, project_payload, PROJECT_HEADERS)
    logger.info(f"Project created with ID: {project_id}")

    process_payload = {"filepond": "{}"}
    process_id = process_dataset(
        doccano_url, process_payload, PROCESS_HEADERS, args.input_file, project_id
    )
    logger.info(f"Data processed with ID: {process_id}")

    upload_payload = json.dumps(
        {
            "format": "JSONL",
            "task": "SequenceLabeling",
            "uploadIds": [process_id],
            "column_data": "text",
            "column_label": "label",
            "delimiter": "",
            "encoding": "utf_8",
        }
    )
    task_id = upload_data(doccano_url, upload_payload, UPLOAD_HEADERS, project_id)
    logger.info(f"Data uploaded successfully........")
    print(task_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload Data on Doccano")
    parser.add_argument(
        "-i", "--input_file", type=str, help="Path to the input data file"
    )
    parser.add_argument("-p", "--project_name", type=str, help="Project Name")
    parser.add_argument("-d", "--project_desc", type=str, help="Project Description")
    args = parser.parse_args()
    main(args)
