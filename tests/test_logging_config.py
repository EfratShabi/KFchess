import logging

from server.logging_config import setup_logging, get_logger, LOGGER_NAME


def test_setup_logging_returns_named_logger(tmp_path):
    logger = setup_logging(log_file=str(tmp_path / 'server.log'))
    assert logger.name == LOGGER_NAME


def test_setup_logging_is_idempotent(tmp_path):
    log_file = str(tmp_path / 'server.log')
    first = setup_logging(log_file=log_file)
    second = setup_logging(log_file=log_file)
    assert first is second
    assert len(first.handlers) == 2  # console + file, not duplicated


def test_get_logger_returns_same_instance_as_setup(tmp_path):
    configured = setup_logging(log_file=str(tmp_path / 'server.log'))
    assert get_logger() is configured


def test_logger_writes_to_file(tmp_path):
    log_file = tmp_path / 'server.log'
    logger = logging.getLogger(LOGGER_NAME)
    logger.handlers.clear()  # isolate from other tests in this module
    setup_logging(log_file=str(log_file))
    get_logger().info('hello server')
    assert 'hello server' in log_file.read_text(encoding='utf-8')
