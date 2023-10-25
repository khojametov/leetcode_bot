from typing import TypeVar, Any

from src.models import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
DataDict = dict[str, Any]
