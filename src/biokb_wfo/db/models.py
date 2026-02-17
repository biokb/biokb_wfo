import enum
from typing import Optional

from sqlalchemy import BigInteger
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from biokb_wfo.constants import TABLE_PREFIX


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models in the biokb_wfo database."""

    pass


class RoleEnums(enum.Enum):
    """Enumeration of possible taxonomic name roles.

    Attributes:
        ROLE: Generic role designation
        ACCEPTED: Name is the accepted taxonomic name
        UNPLACED: Name has not been placed in the taxonomy
        SYNONYM: Name is a synonym of another name
        DEPRECATED: Name is deprecated and should not be used
    """

    ROLE = "role"
    ACCEPTED = "accepted"
    UNPLACED = "unplaced"
    SYNONYM = "synonym"
    DEPRECATED = "deprecated"


class StatusEnums(enum.Enum):
    """Enumeration of nomenclatural status values for taxonomic names.

    Attributes:
        VALID: Name is nomenclaturally valid
        UNKNOWN: Status is unknown
        INVALID: Name is nomenclaturally invalid
        DEPRECATED: Name is deprecated
        ILLEGITIMATE: Name is illegitimate under nomenclatural rules
        REJECTED: Name has been formally rejected
        ORTHOVAR: Orthographic variant
        CONSERVED: Name has been formally conserved
        SUPERFLUOUS: Name is superfluous (has a nomenclatural synonym)
        SANCTIONED: Name has been sanctioned
    """

    VALID = "valid"
    UNKNOWN = "unknown"
    INVALID = "invalid"
    DEPRECATED = "deprecated"
    ILLEGITIMATE = "illegitimate"
    REJECTED = "rejected"
    ORTHOVAR = "orthovar"
    CONSERVED = "conserved"
    SUPERFLUOUS = "superfluous"
    SANCTIONED = "sanctioned"


class RankEnums(enum.Enum):
    """Enumeration of taxonomic ranks.

    Defines all possible taxonomic ranks from kingdom level down to
    infraspecific ranks like variety and form.

    Attributes:
        CODE: Nomenclatural code designation
        VARIETY: Botanical variety (var.)
        SPECIES: Species rank
        FORM: Botanical form (f.)
        SUBSPECIES: Subspecies rank (subsp.)
        UNRANKED: Unranked taxon
        PROLE: Prole (botanical subgroup)
        SUBVARIETY: Subvariety (subvar.)
        LUSUS: Lusus (sport or aberrant form)
        SUBFORM: Subform (subf.)
        SECTION: Section (sect.)
        SUBSERIES: Subseries
        SERIES: Series (ser.)
        SUBSECTION: Subsection (subsect.)
        SUBGENUS: Subgenus (subg.)
        GENUS: Genus rank
        FAMILY: Family rank (ends in -aceae)
        TRIBE: Tribe (ends in -eae)
        SUBTRIBE: Subtribe (ends in -inae)
        SUPERTRIBE: Supertribe
        SUBFAMILY: Subfamily (ends in -oideae)
        ORDER: Order rank (ends in -ales)
        SUPERORDER: Superorder
        SUBCLASS: Subclass (ends in -idae)
        CLASS: Class rank
        PHYLUM: Phylum/Division rank
        KINGDOM: Kingdom rank
        SUBORDER: Suborder
        SUBKINGDOM: Subkingdom
    """

    CODE = "code"
    VARIETY = "variety"
    SPECIES = "species"
    FORM = "form"
    SUBSPECIES = "subspecies"
    UNRANKED = "unranked"
    PROLE = "prole"
    SUBVARIETY = "subvariety"
    LUSUS = "lusus"
    SUBFORM = "subform"
    SECTION = "section"
    SUBSERIES = "subseries"
    SERIES = "series"
    SUBSECTION = "subsection"
    SUBGENUS = "subgenus"
    GENUS = "genus"
    FAMILY = "family"
    TRIBE = "tribe"
    SUBTRIBE = "subtribe"
    SUPERTRIBE = "supertribe"
    SUBFAMILY = "subfamily"
    ORDER = "order"
    SUPERORDER = "superorder"
    SUBCLASS = "subclass"
    CLASS = "class"
    PHYLUM = "phylum"
    KINGDOM = "kingdom"
    SUBORDER = "suborder"
    SUBKINGDOM = "subkingdom"


class Name(Base):
    """Central model representing a taxonomic name in the World Flora Online.

    This model stores all information about a taxonomic name, including its
    nomenclatural details, taxonomic placement, and relationships to taxonomic
    hierarchy levels. Each name can be linked to various taxonomic ranks from
    kingdom down to infraspecific levels.

    Attributes:
        id: Primary key, auto-incrementing integer
        citation: Full citation of the name including author and publication
        full_name: Complete formatted name with authors
        full_name_no_authors: Name without author citations
        full_name_plain: Plain text version without formatting
        genus_string: Genus portion of the name
        hybrid_taxon: Whether this represents a hybrid taxon
        ipni: International Plant Names Index identifier
        name: The name string itself
        status: Nomenclatural status (from StatusEnums)
        parent_id: Reference to parent taxon
        year: Year of publication
        rank: Taxonomic rank (from RankEnums)
        role: Taxonomic role (from RoleEnums)
        species_string: Species portion of the name

        Foreign key relationships to taxonomic ranks:
        code_id, species_id, genus_id, tribe_id, family_id, order_id,
        phylum_id, subkingdom_id, kingdom_id, section_id, subgenus_id,
        subspecies_id, variety_id, subtribe_id, form_id, suborder_id,
        subclass_id, classification_id, subfamily_id, superorder_id,
        series_id, subsection_id, supertribe_id, subvariety_id,
        subseries_id, subform_id, prole_id
    """

    __tablename__ = TABLE_PREFIX + "name"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    citation: Mapped[Optional[str]] = mapped_column(Text)
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    full_name_no_authors: Mapped[str] = mapped_column(String(255))
    full_name_plain: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    genus_string: Mapped[Optional[str]] = mapped_column(String(255))
    hybrid_taxon: Mapped[Optional[bool]]
    ipni: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        SQLEnum(*[e.value for e in StatusEnums]), index=True
    )
    parent_id: Mapped[Optional[str]] = mapped_column(String(50))
    year: Mapped[Optional[int]]
    rank: Mapped[str] = mapped_column(
        SQLEnum(*[e.value for e in RankEnums]), index=True
    )
    role: Mapped[str] = mapped_column(
        SQLEnum(*[e.value for e in RoleEnums]), index=True
    )
    species_string: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys to taxonomic ranks
    code_id: Mapped[Optional[int]] = mapped_column(ForeignKey(TABLE_PREFIX + "code.id"))
    species_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "species.id")
    )
    genus_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "genus.id")
    )
    tribe_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "tribe.id")
    )
    family_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "family.id")
    )
    order_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "order.id")
    )
    phylum_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "phylum.id")
    )
    subkingdom_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "subkingdom.id")
    )
    kingdom_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "kingdom.id")
    )
    section_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "section.id")
    )
    subgenus_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "subgenus.id")
    )
    subspecies_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "subspecies.id")
    )
    variety_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "variety.id")
    )
    subtribe_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "subtribe.id")
    )
    form_id: Mapped[Optional[int]] = mapped_column(ForeignKey(TABLE_PREFIX + "form.id"))
    suborder_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "suborder.id")
    )
    subclass_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "subclass.id")
    )
    classification_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "classification.id")
    )
    subfamily_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "subfamily.id")
    )
    superorder_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "superorder.id")
    )
    series_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "series.id")
    )
    subsection_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "subsection.id")
    )
    supertribe_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "supertribe.id")
    )
    subvariety_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "subvariety.id")
    )
    subseries_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "subseries.id")
    )
    subform_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "subform.id")
    )
    prole_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(TABLE_PREFIX + "prole.id")
    )

    # relationships can be added here if needed
    code: Mapped[Optional["Code"]] = relationship(back_populates="names")
    species: Mapped[Optional["Species"]] = relationship(back_populates="names")
    genus: Mapped[Optional["Genus"]] = relationship(back_populates="names")
    tribe: Mapped[Optional["Tribe"]] = relationship(back_populates="names")
    family: Mapped[Optional["Family"]] = relationship(back_populates="names")
    order: Mapped[Optional["Order"]] = relationship(back_populates="names")
    phylum: Mapped[Optional["Phylum"]] = relationship(back_populates="names")
    subkingdom: Mapped[Optional["Subkingdom"]] = relationship(back_populates="names")
    kingdom: Mapped[Optional["Kingdom"]] = relationship(back_populates="names")
    section: Mapped[Optional["Section"]] = relationship(back_populates="names")
    subgenus: Mapped[Optional["Subgenus"]] = relationship(back_populates="names")
    subspecies: Mapped[Optional["Subspecies"]] = relationship(back_populates="names")
    variety: Mapped[Optional["Variety"]] = relationship(back_populates="names")
    subtribe: Mapped[Optional["Subtribe"]] = relationship(back_populates="names")
    form: Mapped[Optional["Form"]] = relationship(back_populates="names")
    suborder: Mapped[Optional["Suborder"]] = relationship(back_populates="names")
    subclass: Mapped[Optional["Subclass"]] = relationship(back_populates="names")
    classification: Mapped[Optional["Classification"]] = relationship(
        back_populates="names"
    )
    subfamily: Mapped[Optional["Subfamily"]] = relationship(back_populates="names")
    superorder: Mapped[Optional["Superorder"]] = relationship(back_populates="names")
    series: Mapped[Optional["Series"]] = relationship(back_populates="names")
    subsection: Mapped[Optional["Subsection"]] = relationship(back_populates="names")
    supertribe: Mapped[Optional["Supertribe"]] = relationship(back_populates="names")
    subvariety: Mapped[Optional["Subvariety"]] = relationship(back_populates="names")
    subseries: Mapped[Optional["Subseries"]] = relationship(back_populates="names")
    subform: Mapped[Optional["Subform"]] = relationship(back_populates="names")
    prole: Mapped[Optional["Prole"]] = relationship(back_populates="names")


class Code(Base):
    """Nomenclatural code classification model.

    Represents nomenclatural codes (e.g., ICN for plants, ICZN for animals).

    Attributes:
        id: Primary key
        name: Name of the nomenclatural code
        names: List of Name objects associated with this code
    """

    __tablename__ = TABLE_PREFIX + "code"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="code")


class Species(Base):
    """Species-rank taxonomic classification model.

    Represents species-level taxa in the taxonomic hierarchy.

    Attributes:
        id: Primary key
        name: Species name
        names: List of Name objects associated with this species
    """

    __tablename__ = TABLE_PREFIX + "species"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="species")


class Genus(Base):
    """Genus-rank taxonomic classification model.

    Represents genus-level taxa in the taxonomic hierarchy.

    Attributes:
        id: Primary key
        name: Genus name
        names: List of Name objects associated with this genus
    """

    __tablename__ = TABLE_PREFIX + "genus"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="genus")


class Tribe(Base):
    """Tribe-rank taxonomic classification model.

    Represents tribe-level taxa in the taxonomic hierarchy.

    Attributes:
        id: Primary key
        name: Tribe name (typically ends in -eae)
        names: List of Name objects associated with this tribe
    """

    __tablename__ = TABLE_PREFIX + "tribe"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="tribe")


class Family(Base):
    """Family-rank taxonomic classification model.

    Represents family-level taxa in the taxonomic hierarchy.

    Attributes:
        id: Primary key
        name: Family name (typically ends in -aceae)
        names: List of Name objects associated with this family
    """

    __tablename__ = TABLE_PREFIX + "family"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="family")


class Order(Base):
    """Order-rank taxonomic classification model.

    Represents order-level taxa in the taxonomic hierarchy.

    Attributes:
        id: Primary key
        name: Order name (typically ends in -ales)
        names: List of Name objects associated with this order
    """

    __tablename__ = TABLE_PREFIX + "order"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="order")


class Phylum(Base):
    """Phylum/Division-rank taxonomic classification model.

    Represents phylum or division-level taxa in the taxonomic hierarchy.

    Attributes:
        id: Primary key
        name: Phylum/division name
        names: List of Name objects associated with this phylum
    """

    __tablename__ = TABLE_PREFIX + "phylum"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="phylum")


class Subkingdom(Base):
    """Subkingdom-rank taxonomic classification model.

    Represents subkingdom-level taxa in the taxonomic hierarchy.

    Attributes:
        id: Primary key
        name: Subkingdom name
        names: List of Name objects associated with this subkingdom
    """

    __tablename__ = TABLE_PREFIX + "subkingdom"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subkingdom")


class Kingdom(Base):
    """Kingdom-rank taxonomic classification model.

    Represents kingdom-level taxa in the taxonomic hierarchy.

    Attributes:
        id: Primary key
        name: Kingdom name
        names: List of Name objects associated with this kingdom
    """

    __tablename__ = TABLE_PREFIX + "kingdom"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="kingdom")


class Section(Base):
    """Section-rank taxonomic classification model.

    Represents section-level taxa within a genus.

    Attributes:
        id: Primary key
        name: Section name
        names: List of Name objects associated with this section
    """

    __tablename__ = TABLE_PREFIX + "section"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="section")


class Subgenus(Base):
    """Subgenus-rank taxonomic classification model.

    Represents subgenus-level taxa within a genus.

    Attributes:
        id: Primary key
        name: Subgenus name
        names: List of Name objects associated with this subgenus
    """

    __tablename__ = TABLE_PREFIX + "subgenus"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subgenus")


class Subspecies(Base):
    """Subspecies-rank taxonomic classification model.

    Represents subspecies-level infraspecific taxa.

    Attributes:
        id: Primary key
        name: Subspecies name
        names: List of Name objects associated with this subspecies
    """

    __tablename__ = TABLE_PREFIX + "subspecies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subspecies")


class Variety(Base):
    """Variety-rank taxonomic classification model.

    Represents variety-level infraspecific taxa.

    Attributes:
        id: Primary key
        name: Variety name
        names: List of Name objects associated with this variety
    """

    __tablename__ = TABLE_PREFIX + "variety"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="variety")


class Subtribe(Base):
    """Subtribe-rank taxonomic classification model.

    Represents subtribe-level taxa below tribe.

    Attributes:
        id: Primary key
        name: Subtribe name (typically ends in -inae)
        names: List of Name objects associated with this subtribe
    """

    __tablename__ = TABLE_PREFIX + "subtribe"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subtribe")


class Form(Base):
    """Form-rank taxonomic classification model.

    Represents form-level infraspecific taxa.

    Attributes:
        id: Primary key
        name: Form name
        names: List of Name objects associated with this form
    """

    __tablename__ = TABLE_PREFIX + "form"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="form")


class Suborder(Base):
    """Suborder-rank taxonomic classification model.

    Represents suborder-level taxa below order.

    Attributes:
        id: Primary key
        name: Suborder name
        names: List of Name objects associated with this suborder
    """

    __tablename__ = TABLE_PREFIX + "suborder"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="suborder")


class Subclass(Base):
    """Subclass-rank taxonomic classification model.

    Represents subclass-level taxa below class.

    Attributes:
        id: Primary key
        name: Subclass name (typically ends in -idae)
        names: List of Name objects associated with this subclass
    """

    __tablename__ = TABLE_PREFIX + "subclass"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subclass")


class Classification(Base):
    """Classification system model.

    Represents different classification systems or schemes used in taxonomy.

    Attributes:
        id: Primary key
        name: Classification system name
        names: List of Name objects associated with this classification
    """

    __tablename__ = TABLE_PREFIX + "classification"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="classification")


class Subfamily(Base):
    """Subfamily-rank taxonomic classification model.

    Represents subfamily-level taxa below family.

    Attributes:
        id: Primary key
        name: Subfamily name (typically ends in -oideae)
        names: List of Name objects associated with this subfamily
    """

    __tablename__ = TABLE_PREFIX + "subfamily"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subfamily")


class Superorder(Base):
    """Superorder-rank taxonomic classification model.

    Represents superorder-level taxa above order.

    Attributes:
        id: Primary key
        name: Superorder name
        names: List of Name objects associated with this superorder
    """

    __tablename__ = TABLE_PREFIX + "superorder"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="superorder")


class Series(Base):
    """Series-rank taxonomic classification model.

    Represents series-level taxa within a genus.

    Attributes:
        id: Primary key
        name: Series name
        names: List of Name objects associated with this series
    """

    __tablename__ = TABLE_PREFIX + "series"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="series")


class Subsection(Base):
    """Subsection-rank taxonomic classification model.

    Represents subsection-level taxa below section.

    Attributes:
        id: Primary key
        name: Subsection name
        names: List of Name objects associated with this subsection
    """

    __tablename__ = TABLE_PREFIX + "subsection"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subsection")


class Supertribe(Base):
    """Supertribe-rank taxonomic classification model.

    Represents supertribe-level taxa above tribe.

    Attributes:
        id: Primary key
        name: Supertribe name
        names: List of Name objects associated with this supertribe
    """

    __tablename__ = TABLE_PREFIX + "supertribe"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="supertribe")


class Subvariety(Base):
    """Subvariety-rank taxonomic classification model.

    Represents subvariety-level infraspecific taxa below variety.

    Attributes:
        id: Primary key
        name: Subvariety name
        names: List of Name objects associated with this subvariety
    """

    __tablename__ = TABLE_PREFIX + "subvariety"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subvariety")


class Subseries(Base):
    """Subseries-rank taxonomic classification model.

    Represents subseries-level taxa below series.

    Attributes:
        id: Primary key
        name: Subseries name
        names: List of Name objects associated with this subseries
    """

    __tablename__ = TABLE_PREFIX + "subseries"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subseries")


class Subform(Base):
    """Subform-rank taxonomic classification model.

    Represents subform-level infraspecific taxa below form.

    Attributes:
        id: Primary key
        name: Subform name
        names: List of Name objects associated with this subform
    """

    __tablename__ = TABLE_PREFIX + "subform"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subform")


class Prole(Base):
    """Prole-rank taxonomic classification model.

    Represents prole-level infraspecific botanical taxa.

    Attributes:
        id: Primary key
        name: Prole name
        names: List of Name objects associated with this prole
    """

    __tablename__ = TABLE_PREFIX + "prole"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="prole")
