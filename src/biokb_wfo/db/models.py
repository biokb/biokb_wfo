import enum
from typing import Optional

from sqlalchemy import BigInteger
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from biokb_wfo.constants import TABLE_PREFIX


class Base(DeclarativeBase):
    pass


class RoleEnums(enum.Enum):
    ROLE = "role"
    ACCEPTED = "accepted"
    UNPLACED = "unplaced"
    SYNONYM = "synonym"
    DEPRECATED = "deprecated"


class StatusEnums(enum.Enum):
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
    __tablename__ = TABLE_PREFIX + "code"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="code")


class Species(Base):
    __tablename__ = TABLE_PREFIX + "species"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="species")


class Genus(Base):
    __tablename__ = TABLE_PREFIX + "genus"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="genus")


class Tribe(Base):
    __tablename__ = TABLE_PREFIX + "tribe"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="tribe")


class Family(Base):
    __tablename__ = TABLE_PREFIX + "family"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="family")


class Order(Base):
    __tablename__ = TABLE_PREFIX + "order"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="order")


class Phylum(Base):
    __tablename__ = TABLE_PREFIX + "phylum"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="phylum")


class Subkingdom(Base):
    __tablename__ = TABLE_PREFIX + "subkingdom"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subkingdom")


class Kingdom(Base):
    __tablename__ = TABLE_PREFIX + "kingdom"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="kingdom")


class Section(Base):
    __tablename__ = TABLE_PREFIX + "section"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="section")


class Subgenus(Base):
    __tablename__ = TABLE_PREFIX + "subgenus"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subgenus")


class Subspecies(Base):
    __tablename__ = TABLE_PREFIX + "subspecies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subspecies")


class Variety(Base):
    __tablename__ = TABLE_PREFIX + "variety"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="variety")


class Subtribe(Base):
    __tablename__ = TABLE_PREFIX + "subtribe"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subtribe")


class Form(Base):
    __tablename__ = TABLE_PREFIX + "form"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="form")


class Suborder(Base):
    __tablename__ = TABLE_PREFIX + "suborder"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="suborder")


class Subclass(Base):
    __tablename__ = TABLE_PREFIX + "subclass"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subclass")


class Classification(Base):
    __tablename__ = TABLE_PREFIX + "classification"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="classification")


class Subfamily(Base):
    __tablename__ = TABLE_PREFIX + "subfamily"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subfamily")


class Superorder(Base):
    __tablename__ = TABLE_PREFIX + "superorder"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="superorder")


class Series(Base):
    __tablename__ = TABLE_PREFIX + "series"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="series")


class Subsection(Base):
    __tablename__ = TABLE_PREFIX + "subsection"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subsection")


class Supertribe(Base):
    __tablename__ = TABLE_PREFIX + "supertribe"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="supertribe")


class Subvariety(Base):
    __tablename__ = TABLE_PREFIX + "subvariety"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subvariety")


class Subseries(Base):
    __tablename__ = TABLE_PREFIX + "subseries"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subseries")


class Subform(Base):
    __tablename__ = TABLE_PREFIX + "subform"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="subform")


class Prole(Base):
    __tablename__ = TABLE_PREFIX + "prole"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    names: Mapped[list["Name"]] = relationship(back_populates="prole")
