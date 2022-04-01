import logging
import io


def test_loggers_can_write_to_multiple_handlers():
    stream1 = io.StringIO()
    stream2 = io.StringIO()
    logger = logging.getLogger("hello")
    logger.addHandler(logging.StreamHandler(stream1))
    logger.addHandler(logging.StreamHandler(stream2))
    logger.critical("something")
    stream1.seek(0)
    stream2.seek(0)
    assert stream1.read() == "something\n"
    assert stream2.read() == "something\n"
