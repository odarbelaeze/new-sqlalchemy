import logging


def test_loggers_are_hidden_globals():
    logger1 = logging.getLogger("hello")
    logger2 = logging.getLogger("hello")
    assert logger1 is logger2


def test_loggers_are_different_for_different_names():
    logger1 = logging.getLogger("hello")
    logger2 = logging.getLogger("there")
    assert logger1 is not logger2
