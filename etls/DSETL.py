from abc import ABC
from typing import Generic, TypeVar, List
from pydantic import BaseModel
from typing import Generic, List, TypeVar

from etl.ETL import ETL


T_EXTRACTED = TypeVar("T_EXTRACTED", bound=BaseModel)
T_TRANSFORMED = TypeVar("T_TRANSFORMED", bound=BaseModel)


class DSETL(
    ETL[List[T_EXTRACTED], List[T_TRANSFORMED]],
    ABC,
    Generic[T_EXTRACTED, T_TRANSFORMED],
):
    """
    A wrapper over ETL class which takes Generic types: T_EXTRACTED, T_TRANSFORMED
    And creates an ETL of type ETL[List[T_EXTRACTED], List[T_TRANSFORMED]]
    """

    pass
