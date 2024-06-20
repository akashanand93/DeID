from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
import os


class TaggingSentenceByGPT:

    # constructure for a class which takes model name as input
    def __init__(self, model="gpt-4o"):
        self.model = model
        load_dotenv(dotenv_path="_secrets/.env")

    def tagging_sentence(self, sentence: str, prompt: str, object_info):
        # defining a program - OpenAIPydanticProgram, which takes output structure, LLM tpye and a prompt as an input.
        # output_cls - output structure of tagged sentence
        # llm - LLM type to be used for tagging sentence
        # prompt_template_str - prompt to be given to LLM for tagging sentence
        program = OpenAIPydanticProgram.from_defaults(
            output_cls=object_info,
            llm=OpenAI(
                temperature=0, model=self.model, api_key=os.getenv("OPENAI_API_KEY")
            ),
            prompt_template_str=(prompt),
            verbose=True,
        )

        # return response object of type output_cls
        return program(
            sentence=sentence,
            description="extract user information from given sentence",
        )
