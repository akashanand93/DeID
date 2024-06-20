import yaml
import argparse
from common.utils.log import ConfigureLogging
import asyncio
from factory.basicfactory import FactoryGenerator


def load_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def get_args():
    parser = argparse.ArgumentParser(description="Load and run YAML runner config file")
    parser.add_argument("--config_file", type=str, help="Path to the YAML config file")
    args = parser.parse_args()
    return args


"""
def get_etl_args(element):
    etl_args = []
    for key, value in element.items():
        # if key is not 'etl'
        if key != "etl":
            etl_args.append(f"--{key}")
            etl_args.append(value)
    return etl_args
"""


def processETL(element: dict):
    # etl_args = get_etl_args(element)
    etl1 = FactoryGenerator.generate_object(element)
    # etl1 = ClassMappings.get_etl_class(element["etl"])(cli_tokens=etl_args)
    asyncio.run(etl1.run())


if __name__ == "__main__":
    args = get_args()
    config = load_config(args.config_file)
    ConfigureLogging()

    if "serialize" in config.keys():
        # if 'serialize' is True
        if config["serialize"]:
            # for each elenemt and index in config['serialize']
            for index, element in enumerate(config["serialize"]):
                config["serialize"] = element
                print(f"Running ETL {index}")
                processETL(element)
                print(config)
                print("\n")
