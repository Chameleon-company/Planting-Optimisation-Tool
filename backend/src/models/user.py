# User table model
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import String
from ..database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

# For type hinting only, not runtime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .farm import Farm


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    # Relates a farm to the user responsible for it.
    farms: Mapped[List["Farm"]] = relationship(back_populates="owner")

    def __repr__(self) -> str:
        return f"<User (id={self.id!r}, email='{self.email!r}'"
