"""
test_config.py - 配置管理器测试
"""

import pytest
import os
import json
import yaml
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestConfigSingleton:
    """测试 Config 单例模式。"""
    def test_singleton_returns_same_instance(self):
        from florr_assistant.core.config import Config
        c1 = Config()
        c2 = Config()
        assert c1 is c2


class TestConfigDefaults:
    """测试默认配置。"""
    def test_default_general_config(self):
        from florr_assistant.core.config import Config
        c = Config()
        general = c.get_section('general')
        assert general['language'] == 'zh_CN'
        assert general['theme'] == 'dark'
        assert general['auto_start'] is False

    def test_default_module_configs(self):
        from florr_assistant.core.config import Config
        c = Config()
        modules = c.get_section('modules')
        assert 'afk' in modules
        assert modules['afk']['enabled'] is True
        assert 'pathing' in modules
        assert modules['pathing']['enabled'] is True

    def test_default_platform_config(self):
        from florr_assistant.core.config import Config
        c = Config()
        platform = c.get_section('platform')
        assert platform['capture_fps'] == 30

    def test_default_ui_config(self):
        from florr_assistant.core.config import Config
        c = Config()
        ui = c.get_section('ui')
        assert ui['window_width'] == 800
        assert ui['opacity'] == 0.95


class TestConfigGetSet:
    """测试配置读取和写入。"""
    def test_get_existing_key_returns_value(self):
        from florr_assistant.core.config import Config
        c = Config()
        assert c.get('general.language') == 'zh_CN'

    def test_get_nonexistent_key_returns_default(self):
        from florr_assistant.core.config import Config
        c = Config()
        assert c.get('nonexistent.key', 'default_val') == 'default_val'

    def test_get_nested_key_dot_notation(self):
        from florr_assistant.core.config import Config
        c = Config()
        assert c.get('modules.afk.check_interval') == 0.5

    def test_set_updates_value(self):
        from florr_assistant.core.config import Config
        c = Config()
        c.set('general.theme', 'light', save=False)
        assert c.get('general.theme') == 'light'

    def test_set_nested_key_dot_notation(self):
        from florr_assistant.core.config import Config
        c = Config()
        c.set('modules.afk.check_interval', 1.5, save=False)
        assert c.get('modules.afk.check_interval') == 1.5

    def test_get_section_returns_dict(self):
        from florr_assistant.core.config import Config
        c = Config()
        section = c.get_section('general')
        assert isinstance(section, dict)

    def test_get_module_config(self):
        from florr_assistant.core.config import Config
        c = Config()
        module_cfg = c.get_module_config('afk')
        assert isinstance(module_cfg, dict)
        assert module_cfg['enabled'] is True


class TestConfigDeepMerge:
    """测试深度合并。"""
    def test_deep_merge_overrides_nested_values(self):
        from florr_assistant.core.config import Config
        c = Config()
        base = {'a': {'b': 1, 'c': 2}}
        override = {'a': {'b': 99}}
        result = c._deep_merge(base, override)
        assert result['a']['b'] == 99
        assert result['a']['c'] == 2  # preserved

    def test_deep_merge_adds_new_keys(self):
        from florr_assistant.core.config import Config
        c = Config()
        base = {'a': {'b': 1}}
        override = {'a': {'c': 2}}
        result = c._deep_merge(base, override)
        assert result['a']['c'] == 2

    def test_deep_merge_replaces_non_dict(self):
        from florr_assistant.core.config import Config
        c = Config()
        base = {'a': 'string'}
        override = {'a': {'b': 2}}
        result = c._deep_merge(base, override)
        assert result['a'] == {'b': 2}


class TestConfigSaveLoad:
    """测试配置保存和加载。"""
    def test_save_yaml_format(self, tmp_path):
        from florr_assistant.core.config import Config
        c = Config()
        save_path = tmp_path / "config.yaml"
        c.set('general.theme', 'light', save=False)
        c.save(str(save_path))
        assert save_path.exists()

        with open(save_path, 'r', encoding='utf-8') as f:
            loaded = yaml.safe_load(f)
        assert loaded['general']['theme'] == 'light'

    def test_save_json_format(self, tmp_path):
        from florr_assistant.core.config import Config
        c = Config()
        save_path = tmp_path / "config.json"
        c.set('general.theme', 'light', save=False)
        c.save(str(save_path))
        assert save_path.exists()
        assert save_path.suffix == '.json'

        with open(save_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        assert loaded['general']['theme'] == 'light'

    def test_save_creates_parent_directories(self, tmp_path):
        from florr_assistant.core.config import Config
        c = Config()
        save_path = tmp_path / "subdir" / "config.yaml"
        c.save(str(save_path))
        assert save_path.exists()

    def test_load_from_yaml_file(self, sample_yaml_config):
        from florr_assistant.core.config import Config
        c = Config(config_path=sample_yaml_config)
        assert c.get('general.language') == 'en_US'
        assert c.get('general.theme') == 'light'
        assert c.get('general.auto_start') is True

    def test_load_from_json_file(self, tmp_path):
        import json
        from florr_assistant.core.config import Config
        config_data = {
            'general': {'language': 'ja_JP'},
            'modules': {}
        }
        json_path = tmp_path / "config.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        c = Config(config_path=str(json_path))
        assert c.get('general.language') == 'ja_JP'

    def test_load_nonexistent_file_uses_defaults(self, tmp_path):
        from florr_assistant.core.config import Config
        c = Config(config_path=str(tmp_path / "nonexistent.yaml"))
        assert c.get('general.language') == 'zh_CN'  # default


class TestConfigCallbacks:
    """测试配置变更回调。"""
    def test_on_change_register(self):
        from florr_assistant.core.config import Config
        c = Config()
        cb = MagicMock()
        c.on_change('general.theme', cb)
        assert 'general.theme' in c._callbacks

    def test_callback_invoked_on_set(self):
        from florr_assistant.core.config import Config
        c = Config()
        cb = MagicMock()
        c.on_change('general.theme', cb)
        c.set('general.theme', 'blue', save=False)
        assert cb.called

    def test_callback_with_wildcard(self):
        from florr_assistant.core.config import Config
        c = Config()
        cb = MagicMock()
        c.on_change('*', cb)
        c.set('general.theme', 'blue', save=False)
        assert cb.called


class TestConfigReload:
    """测试配置重载。"""
    def test_reload_keeps_default_when_no_file(self):
        from florr_assistant.core.config import Config
        c = Config()
        original = c.get('general.language')
        c.reload()
        assert c.get('general.language') == original

    def test_all_property_returns_copy(self):
        from florr_assistant.core.config import Config
        c = Config()
        all_config = c.all
        all_config['general']['language'] = 'changed'
        assert c.get('general.language') == 'zh_CN'  # original unchanged


class TestConfigReset:
    """测试重置为默认。"""
    def test_reset_to_defaults_restores_original(self):
        from florr_assistant.core.config import Config
        c = Config()
        c.set('general.theme', 'blue', save=False)
        c.reset_to_defaults()
        assert c.get('general.theme') == 'dark'
