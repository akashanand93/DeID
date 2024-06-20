from factory.classmaps import ClassMappings
from abc import ABC, abstractmethod
from loguru import logger


class BaseFactory(ABC):
    @abstractmethod
    def create(self, *args, **kwargs):
        pass


# create a class named DatasetToClinicalNotes that inherits from the BaseFactory class
class DatasetToClinicalNotes(BaseFactory):
    def create(self, config, *args, **kwargs):
        etl_args = FactoryGenerator.get_etl_args(config)
        etl = ClassMappings.get_etl_class(config["etl"])(cli_tokens=etl_args)
        return etl


# create a class named ClinicalNotesToSentences that inherits from the BaseFactory class
class ClinicalNotesToSentences(BaseFactory):
    def create(self, config, *args, **kwargs):
        # create an object of etl
        etl_args = FactoryGenerator.get_etl_args(config)
        etl = ClassMappings.get_etl_class(config["etl"])(cli_tokens=etl_args)

        # generate algo class and set it to the etl object
        algo = config["sentence-extractor"]

        logger.info(f"Using Sentence Extractor: {algo}")

        algo_class = ClassMappings.algo_sentence_extractor_map[algo]
        etl.set_algo(algo_class())

        return etl


# create a class named SentencesToAnnotations that inherits from the BaseFactory class
class SentencesToAnnotations(BaseFactory):
    def create(self, config, *args, **kwargs):
        # create an object of etl
        etl_args = FactoryGenerator.get_etl_args(config)
        etl = ClassMappings.get_etl_class(config["etl"])(cli_tokens=etl_args)

        # generate algo class and set it to the etl object
        algo = config["sentence-tagging"]
        model = config["model"]

        logger.info(f"Using Sentence Tagging: {algo}")

        algo_class = ClassMappings.algo_sentence_tagging_map[algo]
        algo_model = ClassMappings.models_map[model]
        etl.set_algo(algo_class(model=algo_model))

        return etl


# create a class named AnnotationsToDoccano that inherits from the BaseFactory class
class AnnotationsToDoccano(BaseFactory):
    def create(self, config, *args, **kwargs):
        # create an object of etl
        etl_args = FactoryGenerator.get_etl_args(config)
        etl = ClassMappings.get_etl_class(config["etl"])(cli_tokens=etl_args)
        return etl


# create a static class with static method which genetrates the object of the class based on the input
class FactoryGenerator:

    @staticmethod
    def get_factory(factory_name):
        if factory_name == "dataset_to_clinicalnotes":
            return DatasetToClinicalNotes()
        elif factory_name == "clinicalnotes_to_sentences":
            return ClinicalNotesToSentences()
        elif factory_name == "sentences_to_annotations":
            return SentencesToAnnotations()
        elif factory_name == "annotations_to_doccano_annotations":
            return AnnotationsToDoccano()
        else:
            raise ValueError(f"Factory {factory_name} not found")

    @staticmethod
    def generate_object(config, *args, **kwargs):
        factory_name = config["factory"]
        factory = FactoryGenerator.get_factory(factory_name)
        return factory.create(config, *args, **kwargs)

    @staticmethod
    def get_etl_args(config, skip_args=["etl", "factory"]):
        etl_args = []
        for key, value in config.items():
            # if key is not 'etl'
            if key not in skip_args:
                etl_args.append(f"--{key}")
                etl_args.append(value)
        return etl_args
