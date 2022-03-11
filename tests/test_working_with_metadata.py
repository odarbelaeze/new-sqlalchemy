import pytest

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import registry, declarative_base, relationship
from sqlalchemy.future.engine import Engine
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import ForeignKey, Table, Column
from sqlalchemy.sql.sqltypes import Integer, String


@pytest.fixture()
def engine() -> Engine:
    return create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)


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
@pytest.mark.usefixtures("users")
def addresses(metadata: MetaData):
    return Table(
        "addresses",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("user_id", ForeignKey("users.id"), nullable=False),
        Column("email", String, nullable=False),
    )


def test_medatata_mapping():
    metadata = MetaData()
    users = Table(
        "users",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(30)),
        Column("full_name", String),
    )
    assert users.c.name is not None
    assert users.c.keys() == ["id", "name", "full_name"]
    assert users.primary_key is not None


def test_basic_constrains():
    metadata = MetaData()
    users = Table(
        "users",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(30)),
        Column("full_name", String),
    )
    addresses = Table(
        "addresses",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("user_id", ForeignKey("users.id"), nullable=False),
        Column("email", String, nullable=False),
    )
    assert users.primary_key
    assert addresses.primary_key
    assert len(addresses.foreign_keys) == 1


@pytest.mark.usefixtures("users", "addresses")
def test_creating_tables_from_metadata(metadata: MetaData, engine: Engine):
    metadata.create_all(engine)
    with engine.connect() as connection:
        assert connection.execute(text("SELECT * from users")).all() == []
        assert connection.execute(text("SELECT * from addresses")).all() == []


def test_using_a_registry():
    mapper = registry()
    assert mapper.generate_base() is not None
    assert declarative_base() is not None
    assert type(mapper.generate_base()) == type(declarative_base())
    assert mapper.generate_base() is not declarative_base()
    assert declarative_base() is not declarative_base()
    assert mapper.generate_base() is not mapper.generate_base()


def test_declaring_mapped_classes():
    Base = declarative_base()

    class User(Base):
        __tablename__ = "users"

        id = Column(Integer, primary_key=True)
        name = Column(String(30))
        full_name = Column(String)

        addresses = relationship("Address", back_populates="user")

        def __repr__(self):
            return f"User(id={self.id!r}, name={self.name!r}, full_name={self.full_name!r})"

    class Address(Base):
        __tablename__ = "addresses"

        id = Column(Integer, primary_key=True)
        email = Column(String, nullable=False)
        user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

        user = relationship("User", back_populates="addresses")

        def __repr__(self):
            return f"Address(id={self.id!r}, email={self.email!r})"

    assert User.__table__.c.keys() == ["id", "name", "full_name"]
    assert Address.__table__.c.keys() == ["id", "email", "user_id"]
