import sqlalchemy


def test_check_version():
    assert sqlalchemy.__version__.startswith("1.4")
