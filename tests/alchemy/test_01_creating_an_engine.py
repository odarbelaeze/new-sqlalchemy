from sqlalchemy import create_engine


def test_create_engine():
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
    assert engine is not None
