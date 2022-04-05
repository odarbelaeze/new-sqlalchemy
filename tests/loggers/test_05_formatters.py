import logging
from pythonjsonlogger import jsonlogger
import io
import json


def test_json_formatter():
    stream = io.StringIO()
    logger = logging.getLogger("howdy")
    handler = logging.StreamHandler(stream)
    formatter = jsonlogger.JsonFormatter(reserved_attrs=())
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.info("hello", extra={"hello": "there"})

    stream.seek(0)
    data = json.load(stream)

    assert data["message"] == "hello"
    assert data["hello"] == "there"
    assert data["levelname"] == "INFO"


def test_json_and_console_formatters():
    logger = logging.getLogger("howdy")
    logger.setLevel(logging.INFO)

    structured = io.StringIO()
    handler = logging.StreamHandler(structured)
    formatter = jsonlogger.JsonFormatter(reserved_attrs=())
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console = io.StringIO()
    logger.addHandler(logging.StreamHandler(console))

    logger.info("hello", extra={"hello": "there"})

    structured.seek(0)
    console.seek(0)
    data = json.load(structured)

    assert console.read() == "hello\n"
    assert data["message"] == "hello"
    assert data["hello"] == "there"
    assert data["levelname"] == "INFO"
