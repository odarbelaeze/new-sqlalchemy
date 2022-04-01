import logging

factory = logging.getLogRecordFactory()


def test_special_factories():
    records = []

    def new_factory(*args, **kwargs):
        record = factory(*args, **kwargs)
        if record.name == "cats4gold.something":
            record.tags = {"subsystem": "something"}  # type: ignore
        records.append(record)
        return record

    logging.setLogRecordFactory(new_factory)

    logger = logging.getLogger("cats4gold")
    specific_logger = logging.getLogger("cats4gold.something")
    logger.critical("howdy")
    specific_logger.critical("hello")

    assert len(records) == 2
    assert sum(hasattr(r, "tags") for r in records) == 1
