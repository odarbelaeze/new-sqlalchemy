import pytest

from sqlalchemy import MetaData, create_engine
from sqlalchemy.future.engine import Engine
from sqlalchemy.sql.expression import insert, select, text
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


def test_insert_statement(users: Table):
    statement = insert(users).values(
        name="Spongebob", full_name="Spongebob Squarepants"
    )
    assert (
        str(statement)
        == "INSERT INTO users (name, full_name) VALUES (:name, :full_name)"
    )


def test_insert_statement_compiled(users: Table):
    statement = insert(users).values(
        name="Spongebob", full_name="Spongebob Squarepants"
    )
    compiled = statement.compile()
    assert compiled.params == {
        "name": "Spongebob",
        "full_name": "Spongebob Squarepants",
    }


def test_execute_insert_statement(engine: Engine, users: Table):
    statement = insert(users).values(
        name="Spongebob",
        full_name="Spongebob Squarepants",
    )
    with engine.connect() as connection:
        result = connection.execute(statement)
        connection.commit()
    assert result.inserted_primary_key == (1,)
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT count(*) FROM users WHERE users.full_name = :fn"),
            {"fn": "Spongebob Squarepants"},
        )
    assert result.all() == [(1,)]


def test_insert_generates_values_automatically(users):
    statement = insert(users)
    assert (
        str(statement)
        == "INSERT INTO users (id, name, full_name) VALUES (:id, :name, :full_name)"
    )


def test_insert_from_select(users: Table, addresses: Table):
    select_statement = select(users.c.id, users.c.name + "@aol.com")
    insert_statement = insert(addresses).from_select(
        ["user_id", "email"],
        select_statement,
    )
    sql = str(insert_statement)
    assert "INSERT INTO addresses" in sql
    assert "SELECT" in sql
    assert "FROM users" in sql
