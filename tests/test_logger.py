"""
test_logger.py - 日志管理器测试
"""

import pytest
import sys
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestLoggerSingleton:
    """测试 Logger 单例模式。"""
    def test_singleton_returns_same_instance(self):
        from florr_assistant.core.logger import Logger
        l1 = Logger(name='TestLogger1')
        l2 = Logger(name='TestLogger1')
        assert l1 is l2


class TestLoggerLevel:
    """测试日志级别。"""
    def test_default_level_is_info(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestLoggerLevel', console_output=False, file_output=False)
        assert l.level == 'INFO'

    def test_set_level_changes_level(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestLoggerSetLevel', console_output=False, file_output=False)
        l.set_level('DEBUG')
        assert l.level == 'DEBUG'

    def test_set_level_debug_string(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestLoggerDebug', console_output=False, file_output=False)
        l.set_level('debug')
        assert l.level == 'DEBUG'

    def test_invalid_level_defaults_to_info(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestLoggerInvalid', console_output=False, file_output=False)
        l.set_level('NOT_A_LEVEL')
        assert l.level == 'INFO'


class TestLoggerHistory:
    """测试日志历史记录。"""
    def test_history_stores_debug_messages(self, caplog):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestHistoryDebug', console_output=False, file_output=False)
        l._logger.setLevel(logging.DEBUG)
        l._level = logging.DEBUG
        l.debug('debug message', module='Test')
        history = l.get_history(level='DEBUG')
        # History stores raw message (no [module] prefix)
        assert any(r.message == 'debug message' for r in history)

    def test_history_stores_info_messages(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestHistoryInfo', console_output=False, file_output=False)
        l.info('info message', module='Test')
        history = l.get_history(level='INFO')
        assert any('info message' in r.message for r in history)

    def test_history_stores_warning_messages(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestHistoryWarn', console_output=False, file_output=False)
        l.warning('warning message', module='Test')
        history = l.get_history(level='WARNING')
        assert any('warning message' in r.message for r in history)

    def test_history_stores_error_messages(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestHistoryError', console_output=False, file_output=False)
        l.error('error message', module='Test')
        history = l.get_history(level='ERROR')
        assert any('error message' in r.message for r in history)

    def test_history_limit_returns_last_n(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestHistoryLimit', console_output=False, file_output=False)
        l.info('msg1', module='Test')
        l.info('msg2', module='Test')
        l.info('msg3', module='Test')
        history = l.get_history(limit=2)
        assert len(history) == 2

    def test_history_filter_by_level(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestHistoryFilter', console_output=False, file_output=False)
        l.info('info msg', module='Test')
        l.warning('warn msg', module='Test')
        history = l.get_history(level='WARNING')
        assert all(r.level == 'WARNING' for r in history)

    def test_clear_history(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestClearHistory', console_output=False, file_output=False)
        l.info('msg', module='Test')
        l.clear_history()
        assert len(l.get_history()) == 0


class TestLoggerCallbacks:
    """测试日志回调。"""
    def test_add_callback(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestAddCallback', console_output=False, file_output=False)
        cb = MagicMock()
        l.add_callback(cb)
        assert cb in l._callbacks

    def test_remove_callback(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestRemoveCallback', console_output=False, file_output=False)
        cb = MagicMock()
        l.add_callback(cb)
        l.remove_callback(cb)
        assert cb not in l._callbacks

    def test_callback_invoked_on_log(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestCallbackInvoked', console_output=False, file_output=False)
        cb = MagicMock()
        l.add_callback(cb)
        l.info('test message', module='Test')
        assert cb.called


class TestLoggerOutput:
    """测试日志输出。"""
    def test_debug_method_exists(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestDebugMethod', console_output=False, file_output=False)
        assert hasattr(l, 'debug')
        assert callable(l.debug)

    def test_info_method_exists(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestInfoMethod', console_output=False, file_output=False)
        assert hasattr(l, 'info')
        assert callable(l.info)

    def test_warning_method_exists(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestWarnMethod', console_output=False, file_output=False)
        assert hasattr(l, 'warning')
        assert callable(l.warning)

    def test_error_method_exists(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestErrorMethod', console_output=False, file_output=False)
        assert hasattr(l, 'error')
        assert callable(l.error)

    def test_critical_method_exists(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestCriticalMethod', console_output=False, file_output=False)
        assert hasattr(l, 'critical')
        assert callable(l.critical)

    def test_exception_method_exists(self):
        from florr_assistant.core.logger import Logger
        l = Logger(name='TestExceptionMethod', console_output=False, file_output=False)
        assert hasattr(l, 'exception')
        assert callable(l.exception)


class TestLogRecord:
    """测试 LogRecord 数据类。"""
    def test_log_record_has_required_fields(self):
        from florr_assistant.core.logger import LogRecord
        from datetime import datetime
        record = LogRecord(
            timestamp=datetime.now(),
            level='INFO',
            module='Test',
            message='test message'
        )
        assert record.level == 'INFO'
        assert record.module == 'Test'
        assert record.message == 'test message'

    def test_log_record_extra_field(self):
        from florr_assistant.core.logger import LogRecord
        from datetime import datetime
        record = LogRecord(
            timestamp=datetime.now(),
            level='INFO',
            module='Test',
            message='test',
            extra={'key': 'value'}
        )
        assert record.extra == {'key': 'value'}


class TestLoggerLevelsMapping:
    """测试日志级别映射。"""
    def test_levels_contains_all_standard_levels(self):
        from florr_assistant.core.logger import Logger
        assert 'DEBUG' in Logger.LEVELS
        assert 'INFO' in Logger.LEVELS
        assert 'WARNING' in Logger.LEVELS
        assert 'ERROR' in Logger.LEVELS
        assert 'CRITICAL' in Logger.LEVELS

    def test_levels_map_to_correct_logging_values(self):
        from florr_assistant.core.logger import Logger
        assert Logger.LEVELS['DEBUG'] == logging.DEBUG
        assert Logger.LEVELS['INFO'] == logging.INFO
        assert Logger.LEVELS['WARNING'] == logging.WARNING
        assert Logger.LEVELS['ERROR'] == logging.ERROR
        assert Logger.LEVELS['CRITICAL'] == logging.CRITICAL
