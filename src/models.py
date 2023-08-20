from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship


class BaseModel(SQLModel):
    id: int


class User(BaseModel, table=True):
    __tablename__ = "users"

    id: int = Field(default=None, primary_key=True)
    chat_id: str = Field(unique=True)
    telegram_username: str = Field(unique=True)
    leetcode_profile: str = Field(unique=True)
    full_name: str

    statistics: list["Statistic"] = Relationship(back_populates="user")

    def __repr__(self):
        return f"{self.leetcode_profile}"

    def get_solved(self):
        statistics = self.statistics
        return {
            "username": self.telegram_username,
            "total": statistics[0].total() - statistics[1].total(),
            "hard": statistics[0].hard - statistics[1].hard,
            "medium": statistics[0].medium - statistics[1].medium,
            "easy": statistics[0].easy - statistics[1].easy,
        }


class Link(BaseModel, table=True):
    __tablename__ = "links"

    id: int = Field(default=None, primary_key=True)
    chat_id: str = Field(unique=True)
    invite_link: str
    expire_date: datetime

    def __repr__(self):
        return f"{self.invite_link}"


class Statistic(BaseModel, table=True):
    __tablename__ = "statistics"

    id: int = Field(default=None, primary_key=True)
    hard: int
    medium: int
    easy: int
    date: date

    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="statistics")

    def __repr__(self):
        return f"Statistic({self.user_id} - {self.date})"

    def total(self):
        return self.hard + self.medium + self.easy
