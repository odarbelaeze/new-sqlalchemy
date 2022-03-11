import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.future.engine import Engine
from sqlalchemy.future import Connection
from sqlalchemy.orm import Session


@pytest.fixture()
def engine() -> Engine:
    return create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)


@pytest.fixture()
def connection(engine: Engine):
    with engine.connect() as connection:
        yield connection


@pytest.fixture()
def add_rows(connection):
    connection.execute(text("CREATE TABLE some_table (x int, y int)"))
    # NOTE: The create table seems to be "auto-committed"
    connection.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 1, "y": 1}, {"x": 2, "y": 2}],
    )
    connection.commit()


def test_basic_text_execution(engine: Engine):
    connection: Connection
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 'hello world'"))
        assert result.all() == [("hello world",)]


def test_commiting_changes(engine: Engine):
    connection: Connection
    with engine.connect() as connection:
        connection.execute(text("CREATE TABLE some_table (x int, y int)"))
        # NOTE: The create table seems to be "auto-committed"
        connection.execute(
            text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
            [{"x": 1, "y": 1}, {"x": 2, "y": 2}],
        )
        connection.commit()
    with engine.connect() as connection:
        result = connection.execute(text("SELECT x, y FROM some_table"))
        assert result.all() == [(1, 1), (2, 2)]


def test_auto_commit_with_begin(engine: Engine):
    connection: Connection
    with engine.begin() as connection:  # type: ignore -- An implementation detail has this returning None some times
        connection.execute(text("CREATE TABLE some_table (x int, y int)"))
        connection.execute(
            text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
            [{"x": 1, "y": 1}, {"x": 2, "y": 2}],
        )
    with engine.connect() as connection:
        result = connection.execute(text("SELECT x, y FROM some_table"))
        assert result.all() == [(1, 1), (2, 2)]


@pytest.mark.usefixtures("add_rows")
def test_access_rows_by_tuple(connection: Connection):
    result = connection.execute(text("SELECT x, y FROM some_table"))
    for x, y in result:
        assert x == y


@pytest.mark.usefixtures("add_rows")
def test_access_rows_by_index(connection: Connection):
    result = connection.execute(text("SELECT x, y FROM some_table"))
    for row in result:
        assert row[0] == row[1]


@pytest.mark.usefixtures("add_rows")
def test_access_rows_by_attribute_name(connection: Connection):
    result = connection.execute(text("SELECT x, y FROM some_table"))
    for row in result:
        assert row.x == row.y


@pytest.mark.usefixtures("add_rows")
def test_access_rows_with_dict(connection: Connection):
    result = connection.execute(text("SELECT x, y FROM some_table"))
    for dict_row in result.mappings():
        assert dict_row["x"] == dict_row["y"]


@pytest.mark.usefixtures("add_rows")
def test_sending_parameters(connection: Connection):
    result = connection.execute(
        text("SELECT x, y FROM some_table where y > :max"),
        {"max": 1},
    )
    assert result.all() == [(2, 2)]


def test_sending_multiple_parameters(engine: Engine):
    with engine.connect() as connection:
        connection.execute(text("CREATE TABLE some_table (x int, y int)"))
        connection.execute(
            text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
            [{"x": 1, "y": 1}, {"x": 2, "y": 2}],
        )
        connection.commit()
    with engine.connect() as connection:
        result = connection.execute(text("SELECT count(*) FROM some_table"))
        assert result.all() == [(2,)]


@pytest.mark.usefixtures("add_rows")
def test_bundling_parameters_with_statement(connection: Connection):
    statement = text("SELECT x, y FROM some_table where y > :max").bindparams(max=1)
    result = connection.execute(statement)
    assert result.all() == [(2, 2)]


@pytest.mark.usefixtures("add_rows")
def test_executing_with_an_orm_session(engine: Engine):
    statement = text("SELECT x, y FROM some_table where y > :max").bindparams(max=1)
    session: Session
    with Session(engine) as session:
        result = session.execute(statement)
        assert result.all() == [(2, 2)]


@pytest.mark.usefixtures("add_rows")
def test_executing_with_an_orm_session_and_passing_params(engine: Engine):
    statement = text("SELECT x, y FROM some_table where y > :max").bindparams(max=1)
    session: Session
    with Session(engine) as session:
        update_y = text("UPDATE some_table SET y = :new_y WHERE x = :affected_x")
        session.execute(
            update_y,
            [
                {"new_y": 10, "affected_x": 1},
                {"new_y": 12, "affected_x": 2},
            ],
        )
        session.commit()
    with Session(engine) as session:
        result = session.execute(statement)
        assert result.all() == [(1, 10), (2, 12)]
