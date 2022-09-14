import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def create_tables(engine):
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


class Users(Base):
    __tablename__ = "user"
    id = sq.Column(sq.Integer, primary_key=True)
    token = sq.Column(sq.String(length=300), unique=True)


class Filters(Base):
    __tablename__ = "filter"

    id = sq.Column(sq.Integer, primary_key=True)
    code_filter = sq.Column(sq.String(length=50), unique=True)


class Lists(Base):
    __tablename__ = "list"
    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=15), unique=True)
    desc = sq.Column(sq.String(length=100), unique=True)


class ElectedUsers(Base):
    __tablename__ = "elected_user"
    id = sq.Column(sq.Integer, primary_key=True)
    id_elected_user = sq.Column(sq.Integer)
    id_user = sq.Column(sq.Integer, sq.ForeignKey("user.id"), nullable=False)
    id_list = sq.Column(sq.Integer, sq.ForeignKey("list.id"), nullable=False)

    users = relationship(Users, backref="elected_users")
    lists = relationship(Lists, backref="elected_users")


class SearchValues(Base):
    __tablename__ = "search_value"
    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.Integer, sq.ForeignKey("user.id"), nullable=False)
    id_filter = sq.Column(sq.Integer,
                          sq.ForeignKey("filter.id"), nullable=False)
    value = sq.Column(sq.String(length=5), unique=False)

    users = relationship(Users, backref="search_values")
    filters = relationship(Filters, backref="search_values")


class LastMessages(Base):
    __tablename__ = "last_message"
    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.Integer, sq.ForeignKey("user.id"), nullable=False)
    id_message = sq.Column(sq.Integer)
    offset = sq.Column(sq.Integer)

    users = relationship(Users, backref="last_messages")
