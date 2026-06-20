"""Application models built on the mini ORM."""

from src.orm import BaseModel


class User(BaseModel):
    """A user of the system.

    Attributes:
        name: The user's full name.
        email: The user's email address.
        age: The user's age in years.
    """

    __tablename__ = "users"
    name: str
    email: str
    age: int
