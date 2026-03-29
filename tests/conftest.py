"""
conftest.py - pytest fixtures and shared utilities
"""

import sys
import os

# Ensure florr_assistant is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add user site-packages for cv2 and other deps not in venv
_user_packages = '/home/kuli/.local/lib/python3.12/site-packages'
if _user_packages not in sys.path:
    sys.path.insert(0, _user_packages)

import pytest


def pytest_configure(config):
    """Reset singletons before any test runs."""
    _reset_all_singletons()


def _reset_all_singletons():
    """Reset singleton instances to allow clean test isolation."""
    import florr_assistant.core.engine as engine_module
    import florr_assistant.core.config as config_module
    import florr_assistant.core.logger as logger_module
    import florr_assistant.core.events as events_module

    engine_module.Engine._instance = None
    config_module.Config._instance = None
    logger_module.Logger._instance = None
    events_module.EventBus._instance = None


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singletons before each test for isolation."""
    _reset_all_singletons()
    yield
    _reset_all_singletons()


@pytest.fixture
def temp_config_dir(tmp_path):
    """Provide a temporary directory for config files."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def sample_yaml_config(temp_config_dir):
    """Create a sample YAML config file."""
    import yaml
    config_data = {
        'general': {
            'language': 'en_US',
            'theme': 'light',
            'auto_start': True,
        },
        'modules': {
            'afk': {
                'enabled': False,
                'check_interval': 1.0,
            }
        }
    }
    config_path = temp_config_dir / "test_config.yaml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f)
    return str(config_path)
