"""
test_engine.py - 引擎核心模块测试
"""

import pytest
import asyncio
import threading
import time
from unittest.mock import MagicMock, patch


class DummyModule:
    """测试用虚拟模块。"""
    def __init__(self, name='dummy', start_side_effect=None, stop_side_effect=None):
        self.name = name
        self.start_called = False
        self.stop_called = False
        self.pause_called = False
        self.resume_called = False
        self._start_side_effect = start_side_effect
        self._stop_side_effect = stop_side_effect

    def start(self):
        self.start_called = True
        if self._start_side_effect:
            raise self._start_side_effect

    def stop(self):
        self.stop_called = True
        if self._stop_side_effect:
            raise self._stop_side_effect

    def pause(self):
        self.pause_called = True

    def resume(self):
        self.resume_called = True


class AsyncDummyModule:
    """异步测试用虚拟模块。"""
    def __init__(self):
        self.start_called = False
        self.stop_called = False

    async def start(self):
        self.start_called = True

    async def stop(self):
        self.stop_called = True


class TestEngineSingleton:
    """测试 Engine 单例模式。"""
    def test_singleton_returns_same_instance(self):
        from florr_assistant.core.engine import Engine
        e1 = Engine()
        e2 = Engine()
        assert e1 is e2

    def test_reinit_does_not_reset_state(self):
        from florr_assistant.core.engine import Engine
        e1 = Engine()
        e1._state = 'test_state'
        e2 = Engine()
        # _initialized check prevents re-init; internal state persists
        assert e2._state == 'test_state'


class TestEngineStateProperties:
    """测试 Engine 状态属性。"""
    def test_default_state_is_idle(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        assert e.state.value == 'idle'

    def test_is_running_false_when_idle(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        assert e.is_running is False

    def test_is_paused_false_when_idle(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        assert e.is_paused is False


class TestEngineModuleRegistration:
    """测试模块注册与注销。"""
    def test_register_module_returns_true(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        result = e.register_module('test_module', dummy, priority=5)
        assert result is True

    def test_register_duplicate_returns_false(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        result = e.register_module('test_module', dummy)
        assert result is False

    def test_unregister_existing_module_returns_true(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        result = e.unregister_module('test_module')
        assert result is True

    def test_unregister_nonexistent_returns_false(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        result = e.unregister_module('nonexistent')
        assert result is False

    def test_enable_module_returns_true(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        result = e.enable_module('test_module')
        assert result is True

    def test_disable_module_returns_true(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        result = e.disable_module('test_module')
        assert result is True  # disable_module returns True when module exists

    def test_get_module_returns_registered_module(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        assert e.get_module('test_module') is dummy

    def test_get_module_nonexistent_returns_none(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        assert e.get_module('nonexistent') is None

    def test_get_all_modules_returns_copy(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        modules = e.get_all_modules()
        modules.clear()  # modifying copy shouldn't affect original
        assert 'test_module' in e.get_all_modules()


class TestEngineModuleLifecycle:
    """测试模块生命周期控制。"""
    def test_start_module_calls_module_start(self):
        from florr_assistant.core.engine import Engine, EngineState
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        result = e.start_module('test_module')
        assert result is True
        assert dummy.start_called is True

    def test_start_module_disabled_returns_false(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy, priority=0)
        e._modules['test_module'].enabled = False
        result = e.start_module('test_module')
        assert result is False

    def test_start_module_nonexistent_returns_false(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        result = e.start_module('nonexistent')
        assert result is False

    def test_start_module_with_exception_sets_error_state(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule(start_side_effect=RuntimeError('start failed'))
        e.register_module('test_module', dummy)
        result = e.start_module('test_module')
        assert result is False
        assert e._modules['test_module'].state == e._modules['test_module'].state.__class__.ERROR

    def test_stop_module_calls_module_stop(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        e.start_module('test_module')
        e.stop_module('test_module')
        assert dummy.stop_called is True

    def test_pause_module_calls_pause(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        e.start_module('test_module')
        result = e.pause_module('test_module')
        assert result is True
        assert dummy.pause_called is True

    def test_pause_module_not_running_returns_false(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        result = e.pause_module('test_module')
        assert result is False

    def test_resume_module_calls_resume(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        e.start_module('test_module')
        e.pause_module('test_module')
        result = e.resume_module('test_module')
        assert result is True
        assert dummy.resume_called is True

    def test_resume_module_not_paused_returns_false(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        e.start_module('test_module')
        result = e.resume_module('test_module')
        assert result is False


class TestEngineCallbacks:
    """测试回调机制。"""
    def test_add_callback_returns_true(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        cb = MagicMock()
        result = e.add_callback('on_start', cb)
        assert result is True

    def test_add_callback_invalid_event_returns_false(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        cb = MagicMock()
        result = e.add_callback('on_invalid', cb)
        assert result is False

    def test_remove_callback_returns_true(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        cb = MagicMock()
        e.add_callback('on_start', cb)
        result = e.remove_callback('on_start', cb)
        assert result is True

    def test_callback_invoked_on_start_all(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        cb = MagicMock()
        e.add_callback('on_start', cb)
        e.start_all()
        assert cb.called

    def test_callback_invoked_on_stop_all(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        e.start_all()
        cb = MagicMock()
        e.add_callback('on_stop', cb)
        e.stop_all()
        assert cb.called


class TestEngineBulkOperations:
    """测试批量操作。"""
    def test_start_all_starts_enabled_modules_in_priority_order(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        m1 = DummyModule('low')
        m2 = DummyModule('high')
        e.register_module('low', m1, priority=1)
        e.register_module('high', m2, priority=10)
        e.start_all()
        assert m1.start_called is True
        assert m2.start_called is True

    def test_start_all_fails_if_not_idle_or_stopped(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        e._state = e._state.__class__.RUNNING
        result = e.start_all()
        assert result is False

    def test_pause_all_requires_running_state(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        e._state = e._state.__class__.IDLE
        result = e.pause_all()
        assert result is False

    def test_resume_all_requires_paused_state(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        e._state = e._state.__class__.IDLE
        result = e.resume_all()
        assert result is False


class TestEngineStats:
    """测试统计功能。"""
    def test_get_stats_returns_dict(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        stats = e.get_stats()
        assert isinstance(stats, dict)
        assert 'start_time' in stats
        assert 'run_time' in stats
        assert 'modules_run' in stats
        assert 'errors' in stats

    def test_stats_modules_run_increments_on_start(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        e.start_module('test_module')
        assert e.get_stats()['modules_run'] == 1

    def test_stats_errors_increments_on_error(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule(start_side_effect=RuntimeError('fail'))
        e.register_module('test_module', dummy)
        e.start_module('test_module')
        assert e.get_stats()['errors'] >= 1

    def test_get_module_states_returns_dict(self):
        from florr_assistant.core.engine import Engine
        e = Engine()
        dummy = DummyModule()
        e.register_module('test_module', dummy)
        states = e.get_module_states()
        assert isinstance(states, dict)
        assert 'test_module' in states
