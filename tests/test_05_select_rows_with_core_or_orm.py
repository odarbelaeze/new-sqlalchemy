import pytest

from sqlalchemy import MetaData, create_engine
from sqlalchemy.future.engine import Engine
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.schema import ForeignKey, Table, Column
from sqlalchemy.sql.sqltypes import Integer, String


@pytest.fixture()
def metadata() -> MetaData:
    return MetaData()


@pytest.fixture()
def users(metadata: MetaData):
    return Table(
        "users",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(30)),
        Column("full_name", String),
    )


@pytest.fixture()
def addresses(metadata: MetaData, users):
    assert users is not None
    return Table(
        "addresses",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("user_id", ForeignKey("users.id"), nullable=False),
        Column("email", String, nullable=False),
    )


@pytest.fixture()
def engine(metadata: MetaData, users, addresses) -> Engine:
    assert users is not None
    assert addresses is not None
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
    metadata.create_all(engine)
    return engine


def test_select_with_table(users):
    statement = select(users).where(users.c.name == "Spongebob")
    assert str(statement) == "\n".join(
        [
            "SELECT users.id, users.name, users.full_name ",
            "FROM users ",
            "WHERE users.name = :name_1",
        ]
    )
