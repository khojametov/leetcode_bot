from datetime import date

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    telegram_username = Column(String, unique=True, nullable=False)
    leetcode_profile = Column(String, unique=True, nullable=False)
    full_name = Column(String)

    statistics = relationship("Statistic", order_by="desc(Statistic.date)")

    def __repr__(self):
        return f"{self.leetcode_profile}"

    def get_solved(self):
        statistics = self.statistics
        return (
            self.telegram_username,
            statistics[0].total() - statistics[1].total(),
            statistics[0].hard - statistics[1].hard,
            statistics[0].medium - statistics[1].medium,
            statistics[0].total(),
        )


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    invite_link = Column(String, unique=True, nullable=False)
    expire_date = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"{self.link}"

    __mapper_args__ = {"eager_defaults": True}


class Statistic(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    hard = Column(Integer, default=0)
    medium = Column(Integer, default=0)
    easy = Column(Integer, default=0)
    date = Column(Date, default=date.today())

    def __repr__(self):
        return f"Statistic({self.user_id} - {self.date})"

    def total(self):
        return self.hard + self.medium + self.easy
