import logging
import io


def test_logger_writest_to_parent_handlers():
    stream = io.StringIO()
    logger1 = logging.getLogger("hello")
    logger1.addHandler(logging.StreamHandler(stream))
    logger2 = logging.getLogger("hello.there")
    logger2.critical("howdy")
    stream.seek(0)
    assert stream.read() == "howdy\n"


def test_logger_doesnt_write_to_child_handlers():
    stream = io.StringIO()
    logger1 = logging.getLogger("hello")
    logger2 = logging.getLogger("hello.there")
    logger2.addHandler(logging.StreamHandler(stream))
    logger1.critical("howdy")
    stream.seek(0)
    assert stream.read() == ""
