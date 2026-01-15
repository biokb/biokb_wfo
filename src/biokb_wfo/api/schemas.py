from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class NameBase(BaseModel):
    name: Optional[str] = None
    name_alpha: Optional[str] = None
    name_plain: Optional[str] = None
    genus: Optional[str] = None
    family: Optional[str] = None
    placed_in_genus: Optional[str] = None
    wfo_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NameSearch(NameBase):
    pass


class NameSearchResults(BaseModel):
    count: int
    offset: int
    limit: int
    results: list[NameSearch]


class SimilarNameSearchResult(NameBase):
    calculate_with: Literal["exact", "levenshtein", "metaphone_jaro", "pattern_match"]
    similarity: float = Field(le=1.0)
