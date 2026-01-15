from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

prefix = "wfo_"


class Base(DeclarativeBase):
    pass


class Name(Base):
    __tablename__ = prefix + "name"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[Optional[str]] = mapped_column(Text)
    name_alpha: Mapped[Optional[str]] = mapped_column(Text)
    name_plain: Mapped[Optional[str]] = mapped_column(Text)
    genus: Mapped[Optional[str]] = mapped_column(Text)
    family: Mapped[Optional[str]] = mapped_column(Text)
    placed_in_genus: Mapped[Optional[str]] = mapped_column(Text)
    wfo_id: Mapped[Optional[str]] = mapped_column(
        String(32), unique=True, nullable=False
    )
