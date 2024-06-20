import asyncio
from abc import ABC, abstractmethod
import json
from typing import Dict, Generic, List, Tuple, TypeVar, Any

from loguru import logger
from pandas import DataFrame

from etl.utils.dfutils import DFDict, DFUtils
from common.utils.base import CollectionUtils

# Create type variables to represent flexible data types
T_EXTRACTED = TypeVar("T_EXTRACTED")
T_TRANSFORMED = TypeVar("T_TRANSFORMED")


class ETL(ABC, Generic[T_EXTRACTED, T_TRANSFORMED]):

    def __init__(
        self,
        cli_tokens: List[str] = None,
        options: Dict[str, str] = None,
        default_options: Dict[str, str] = None,
    ):
        """
        Initializes self.options with the given cli_tokens & options.

        Argument Parsing:
        An ETL has two type of arguments:
        - Compile Time: These must be passed programmatically while building an ETL.
        - Run Time: These are passed at runtime.
        - Confusion arises when we need to have argruments which are a mix of both in different proportion, e.g:
            - Ability to set default values for compile time args.
            - Ability to set runtime args programmatically.

        Hence we have this simplified scheme of arguments in ETL subclasses:
        - All ETLs will be initialized with `Required Compile Time args`.
            - PHILOSOPHY: Must be passed programmatically, Defaults in rare cases.
            - Typically not overriden at run time, but possible.
        - Run Time args: cli_tokens + options + default_options dict.
            - PHILOSPHY: FAIL if not provided explicitly at runtime, but also allow programmatic way to override.
            - These can be passed via cli_tokens for dev / prod runs.
            - These can be overriden programmatically via the options dict.
            - Use a DEFAULT_OPTIONS dict in your class to specify default to fill in redundant options.
            - options dict will override cli_tokens.

        - It is the responsibility of ETL to raise Exceptions for missing/inconsistent runtime options.

        Options:
            - Passed via cli as --key value.
            - Stored in options dict as {key: value}. The `--` is stripped.
        """
        # override init to initialize your ETL,
        # always call super().__init__(cli_tokens, options, [default_options]) to parse cli tokens & dynamic options.
        self.options = {}
        if cli_tokens:
            self.options, _ = ETLUtils.parse_args(cli_tokens)

        # Override if passed programmatically.
        if options:
            self.options.update(options)

        # Add default options if not present.
        if default_options:
            CollectionUtils.add_missing(self.options, default_options)

        # Capture Initialiazation in Logs:
        logger.debug(
            f"ETL will be initialized with following args: {json.dumps(self.options, indent=2)}\n"
        )

    @abstractmethod
    async def extract(self) -> T_EXTRACTED:
        """
        Abstract method for extracting data.
        """
        pass

    async def transform(self, data: T_EXTRACTED) -> T_TRANSFORMED:
        """
        Default Transform Function: Identity

        Parameters:
        data (T_EXTRACTED): Data extracted from the extract method.
        """
        return data

    async def load(self, data: T_TRANSFORMED):
        """
        Default Load Function: No-op
        Parameters:
        transformed_data (T_TRANSFORMED): Data transformed from the transform method.
        """
        pass

    async def run(self):
        """
        Method to orchestrate the ETL process.
        """
        logger.info("Running ETL...")
        extracted_data: T_EXTRACTED = await self.extract()
        logger.success(f"Extract Done... {type(extracted_data)}")
        transformed_data: T_TRANSFORMED = await self.transform(extracted_data)
        logger.success(f"Transform Done... {type(transformed_data)}")
        await self.load(transformed_data)
        logger.success("Load Done.")


class DFDictETL(ETL[DFDict, DFDict]):
    """
    A convenience default ETL base class with override for run method for verbose logging.
    """

    async def run(self):
        logger.info("Running ETL...")

        extracted_data: Dict[str, DataFrame] = await self.extract()
        logger.success(f"Extract Done... {type(extracted_data)}")
        DFUtils.log_df_info(extracted_data)

        transformed_data: Dict[str, DataFrame] = await self.transform(extracted_data)
        logger.success(f"Transform Done... {type(transformed_data)}")
        DFUtils.log_df_info(transformed_data)

        await self.load(transformed_data)
        logger.success("--- Load Done ---")
        logger.info("")


class ETLRunner(ETL):
    """
    Configure a set of ETLs & use this class to trigger them sequentially / in parallel.
    This class is also an ETL itself to support complex DAG like ETL chains.
    """

    ETLType = TypeVar("ETLType", bound=ETL)

    def __init__(
        self,
        etls: List[ETLType],
        multi_processing=True,
        cli_tokens=None,
        options=None,
    ):
        # These options are for the Runner /- only. Currently not used.
        super().__init__(cli_tokens, options)

        # constituent ETLs are already initialized.
        self.etls = etls
        self.multi_processing = multi_processing

    async def run(self):
        if self.multi_processing:
            # This is multi-threading currently. Multi processing has some picking issues.
            tasks = [etl.run() for etl in self.etls]
            await asyncio.gather(*tasks)

            # with multiprocessing.Pool() as pool:
            #     results = [
            #         pool.apply_async(wrapper, (etl,)) for etl in self.etls
            #     ]
            #     results = [result.get() for result in results]
        else:
            for etl in self.etls:
                await etl.run()

    async def extract(self):
        raise NotImplementedError("ETLRunner only supports its composite RUN method")

    async def transform(self, data):
        raise NotImplementedError("ETLRunner only supports its composite RUN method")

    async def load(self, data):
        raise NotImplementedError("ETLRunner only supports its composite RUN method")


class ETLUtils:
    """A collection of utilities to compose operations in ETLs."""

    @staticmethod
    def parse_args(tokens: List[str]) -> Tuple[Dict[str, str], List[str]]:
        """
        Parse the given line string into a dict of kwargs & a list of args.
        NOTE:
        - Flags are not supported. Use `--flag-name true` to coerce flags as key-value pairs.
        - The tokens themselves are atomic strings and can have spaces.
        - Ordering: It is recommended to have options before args in the tokens list.

        Example: "--name raj --age 25 create-patient" will return:
            - options: {"name": "raj", "age": "25"}
            - args: ["create-patient"]
        """
        options = {}
        args = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.startswith("--"):
                if i + 1 >= len(tokens):
                    raise Exception("Missing value for option: {key}")
                key = token[2:]
                value = tokens[i + 1]
                options[key] = value
                i += 2
            else:
                args.append(token)
                i += 1

        return options, args
