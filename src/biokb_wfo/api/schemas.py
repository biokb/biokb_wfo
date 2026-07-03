from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from biokb_wfo.db import models

# ============================================
# Taxonomy Rank Schemas
# ============================================


class TaxonomyRankBase(BaseModel):
    """Base schema for taxonomy ranks"""

    name: str

    model_config = ConfigDict(from_attributes=True)


class TaxonomyRank(TaxonomyRankBase):
    """Schema for taxonomy rank responses"""

    id: int


# Specific taxonomy rank schemas
class CodeBase(TaxonomyRankBase):
    pass


class Code(CodeBase):
    id: int


class SpeciesBase(TaxonomyRankBase):
    pass


class Species(SpeciesBase):
    id: int


class GenusBase(TaxonomyRankBase):
    pass


class Genus(GenusBase):
    id: int


class TribeBase(TaxonomyRankBase):
    pass


class Tribe(TribeBase):
    id: int


class FamilyBase(TaxonomyRankBase):
    pass


class Family(FamilyBase):
    id: int


class OrderBase(TaxonomyRankBase):
    pass


class Order(OrderBase):
    id: int


class PhylumBase(TaxonomyRankBase):
    pass


class Phylum(PhylumBase):
    id: int


class SubkingdomBase(TaxonomyRankBase):
    pass


class Subkingdom(SubkingdomBase):
    id: int


class KingdomBase(TaxonomyRankBase):
    pass


class Kingdom(KingdomBase):
    id: int


class SectionBase(TaxonomyRankBase):
    pass


class Section(SectionBase):
    id: int


class SubgenusBase(TaxonomyRankBase):
    pass


class Subgenus(SubgenusBase):
    id: int


class SubspeciesBase(TaxonomyRankBase):
    pass


class Subspecies(SubspeciesBase):
    id: int


class VarietyBase(TaxonomyRankBase):
    pass


class Variety(VarietyBase):
    id: int


class SubtribeBase(TaxonomyRankBase):
    pass


class Subtribe(SubtribeBase):
    id: int


class FormBase(TaxonomyRankBase):
    pass


class Form(FormBase):
    id: int


class SuborderBase(TaxonomyRankBase):
    pass


class Suborder(SuborderBase):
    id: int


class SubclassBase(TaxonomyRankBase):
    pass


class Subclass(SubclassBase):
    id: int


class ClassificationBase(TaxonomyRankBase):
    pass


class Classification(ClassificationBase):
    id: int


class SubfamilyBase(TaxonomyRankBase):
    pass


class Subfamily(SubfamilyBase):
    id: int


class SuperorderBase(TaxonomyRankBase):
    pass


class Superorder(SuperorderBase):
    id: int


class SeriesBase(TaxonomyRankBase):
    pass


class Series(SeriesBase):
    id: int


class SubsectionBase(TaxonomyRankBase):
    pass


class Subsection(SubsectionBase):
    id: int


class SupertribeBase(TaxonomyRankBase):
    pass


class Supertribe(SupertribeBase):
    id: int


class SubvarietyBase(TaxonomyRankBase):
    pass


class Subvariety(SubvarietyBase):
    id: int


class SubseriesBase(TaxonomyRankBase):
    pass


class Subseries(SubseriesBase):
    id: int


class SubformBase(TaxonomyRankBase):
    pass


class Subform(SubformBase):
    id: int


class ProleBase(TaxonomyRankBase):
    pass


class Prole(ProleBase):
    id: int


# ============================================
# Name Schemas
# ============================================


class NameBase(BaseModel):
    """Base schema for Name model"""

    citation: Optional[str] = None
    full_name: str
    full_name_no_authors: str
    full_name_plain: Optional[str] = None
    genus_string: Optional[str] = None
    hybrid_taxon: Optional[bool] = None
    ipni: Optional[str] = None
    name: Optional[str] = None
    status: str
    parent_id: Optional[str] = None
    year: Optional[int] = None
    rank: str
    role: str
    species_string: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NameSearch(BaseModel):
    """Schema for updating a Name (all fields optional)"""

    id: Optional[int] = None
    citation: Optional[str] = None
    full_name: Optional[str] = None
    full_name_no_authors: Optional[str] = None
    full_name_plain: Optional[str] = None
    genus_string: Optional[str] = None
    hybrid_taxon: Optional[bool] = None
    ipni: Optional[str] = None
    name: Optional[str] = None
    status: Optional[models.StatusEnums] = Field(
        None,
        description="status",
    )
    parent_id: Optional[str] = None
    year: Optional[int] = None
    rank: Optional[models.RankEnums] = Field(
        None,
        description="rank",
    )
    role: Optional[models.RoleEnums] = Field(
        None,
        description="role",
    )
    species_string: Optional[str] = None
    code_id: Optional[int] = None
    species_id: Optional[int] = None
    genus_id: Optional[int] = None
    tribe_id: Optional[int] = None
    family_id: Optional[int] = None
    order_id: Optional[int] = None
    phylum_id: Optional[int] = None
    subkingdom_id: Optional[int] = None
    kingdom_id: Optional[int] = None
    section_id: Optional[int] = None
    subgenus_id: Optional[int] = None
    subspecies_id: Optional[int] = None
    variety_id: Optional[int] = None
    subtribe_id: Optional[int] = None
    form_id: Optional[int] = None
    suborder_id: Optional[int] = None
    subclass_id: Optional[int] = None
    classification_id: Optional[int] = None
    subfamily_id: Optional[int] = None
    superorder_id: Optional[int] = None
    series_id: Optional[int] = None
    subsection_id: Optional[int] = None
    supertribe_id: Optional[int] = None
    subvariety_id: Optional[int] = None
    subseries_id: Optional[int] = None
    subform_id: Optional[int] = None
    prole_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class Name(NameBase):
    """Schema for Name responses with id and relationships"""

    id: int
    # Optional foreign keys
    code_id: Optional[int] = None
    species_id: Optional[int] = None
    genus_id: Optional[int] = None
    tribe_id: Optional[int] = None
    family_id: Optional[int] = None
    order_id: Optional[int] = None
    phylum_id: Optional[int] = None
    subkingdom_id: Optional[int] = None
    kingdom_id: Optional[int] = None
    section_id: Optional[int] = None
    subgenus_id: Optional[int] = None
    subspecies_id: Optional[int] = None
    variety_id: Optional[int] = None
    subtribe_id: Optional[int] = None
    form_id: Optional[int] = None
    suborder_id: Optional[int] = None
    subclass_id: Optional[int] = None
    classification_id: Optional[int] = None
    subfamily_id: Optional[int] = None
    superorder_id: Optional[int] = None
    series_id: Optional[int] = None
    subsection_id: Optional[int] = None
    supertribe_id: Optional[int] = None
    subvariety_id: Optional[int] = None
    subseries_id: Optional[int] = None
    subform_id: Optional[int] = None
    prole_id: Optional[int] = None


class NameWithRelationships(NameBase):
    """Schema for Name with nested taxonomy relationships"""

    id: int
    code: Optional[Code] = None
    species: Optional[Species] = None
    genus: Optional[Genus] = None
    tribe: Optional[Tribe] = None
    family: Optional[Family] = None
    order: Optional[Order] = None
    phylum: Optional[Phylum] = None
    subkingdom: Optional[Subkingdom] = None
    kingdom: Optional[Kingdom] = None
    section: Optional[Section] = None
    subgenus: Optional[Subgenus] = None
    subspecies: Optional[Subspecies] = None
    variety: Optional[Variety] = None
    subtribe: Optional[Subtribe] = None
    form: Optional[Form] = None
    suborder: Optional[Suborder] = None
    subclass: Optional[Subclass] = None
    classification: Optional[Classification] = None
    subfamily: Optional[Subfamily] = None
    superorder: Optional[Superorder] = None
    series: Optional[Series] = None
    subsection: Optional[Subsection] = None
    supertribe: Optional[Supertribe] = None
    subvariety: Optional[Subvariety] = None
    subseries: Optional[Subseries] = None
    subform: Optional[Subform] = None
    prole: Optional[Prole] = None


class NameSearchResults(BaseModel):
    """Schema for paginated search results"""

    count: int
    offset: int
    limit: int
    results: list[NameWithRelationships]


class NameFoundResult(BaseModel):
    """Schema for Name responses"""

    wfo_id: int
    found_in: str
    found_with_name: str
    full_name: str
    full_name_no_authors: str
    full_name_plain: str
    genus: Optional[str] = None
    family: Optional[str] = None
    status: str
    rank: str
    role: Optional[str] = None
    year: Optional[int] = None
    ipni: Optional[str] = None
    url: str


class Taxon(BaseModel):
    """Schema for Taxon responses with id and relationships"""

    id: int
    name: str


class TaxonSearch(BaseModel):
    """Schema for Taxon responses with id and relationships"""

    id: Optional[int] = None
    name: Optional[str] = None


class TaxonSearchResults(BaseModel):
    """Schema for paginated search results"""

    count: int
    offset: int
    limit: int
    results: list[Taxon]


# ============================================
# Search and Filter Schemas
# ============================================


class SimilarNameSearchResult(BaseModel):
    """Schema for similarity search results"""

    wfo_id: int
    full_name: str
    full_name_no_authors: str
    full_name_plain: str
    genus: Optional[str] = None
    family: Optional[str] = None
    status: str
    rank: str
    role: Optional[str] = None
    year: Optional[int] = None
    ipni: Optional[str] = None
    status: str
    url: str
    calculate_with: Literal[
        "exact", "levenshtein", "metaphone_jaro", "sequence_matcher"
    ]
    similarity: float = Field(ge=0.0, le=1.0)
    model_config = ConfigDict(from_attributes=True)

    def __lt__(self, other: "SimilarNameSearchResult") -> bool:
        """Define less-than for sorting by similarity"""
        if not isinstance(other, SimilarNameSearchResult):
            return NotImplemented
        return self.similarity < other.similarity
