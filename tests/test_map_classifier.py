"""
test_map_classifier.py - 地图分类器测试
"""

import pytest
import numpy as np
from unittest.mock import MagicMock, patch, mock_open


# Mock cv2 before importing the module
cv2_mock = MagicMock()
numpy_mock = np

# Create mock arrays
def make_mock_image(shape=(480, 640, 3), dtype='uint8'):
    return np.zeros(shape, dtype=dtype)


class MockMatchResult:
    TM_CCOEFF_NORMED = 1.0
    pass


class TestFullscreenTemplateMatcherInit:
    """测试 FullscreenTemplateMatcher 初始化。"""
    @patch('florr_assistant.modules.pathing.map_classifier.cv2')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    @patch('florr_assistant.modules.pathing.map_classifier.os.listdir')
    def test_init_loads_templates_from_dir(self, mock_listdir, mock_exists, mock_cv2):
        mock_exists.return_value = True
        mock_listdir.return_value = ['ocean.png', 'desert.png']
        mock_cv2.imread.return_value = make_mock_image()

        from florr_assistant.modules.pathing.map_classifier import FullscreenTemplateMatcher
        matcher = FullscreenTemplateMatcher('/fake/maps')
        assert len(matcher.templates) == 2

    @patch('florr_assistant.modules.pathing.map_classifier.cv2')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_init_handles_missing_dir(self, mock_exists, mock_cv2):
        mock_exists.return_value = False
        from florr_assistant.modules.pathing.map_classifier import FullscreenTemplateMatcher
        matcher = FullscreenTemplateMatcher('/nonexistent/maps')
        assert len(matcher.templates) == 0

    @patch('florr_assistant.modules.pathing.map_classifier.cv2')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_default_scales(self, mock_exists, mock_cv2):
        mock_exists.return_value = False
        from florr_assistant.modules.pathing.map_classifier import FullscreenTemplateMatcher
        matcher = FullscreenTemplateMatcher('/fake')
        expected_scales = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 2.0]
        assert matcher.default_scales == expected_scales


class TestFullscreenTemplateMatcherMultiScale:
    """测试多尺度匹配。"""
    @patch('florr_assistant.modules.pathing.map_classifier.cv2')
    def test_multi_scale_match_returns_tuple(self, mock_cv2):
        image = make_mock_image()
        template = make_mock_image()
        mock_cv2.resize.return_value = make_mock_image()
        mock_cv2.minMaxLoc.return_value = (0.8, 0.9, (100, 50), (150, 100))
        mock_cv2.matchTemplate.return_value = np.zeros((10, 10), dtype=np.float32)

        from florr_assistant.modules.pathing.map_classifier import FullscreenTemplateMatcher
        matcher = FullscreenTemplateMatcher('/fake', default_scales=[1.0])
        result = matcher._multi_scale_match(image, template, scales=[1.0], threshold=0.5)
        assert isinstance(result, tuple)
        assert len(result) == 4

    @patch('florr_assistant.modules.pathing.map_classifier.cv2')
    def test_multi_scale_match_returns_zero_when_template_too_large(self, mock_cv2):
        image = make_mock_image((100, 100, 3))
        template = make_mock_image((500, 500, 3))
        from florr_assistant.modules.pathing.map_classifier import FullscreenTemplateMatcher
        matcher = FullscreenTemplateMatcher('/fake')
        result = matcher._multi_scale_match(image, template, scales=[2.0], threshold=0.5)
        best_val = result[0]
        assert best_val == 0  # should skip because template larger than image


class TestFullscreenTemplateMatcherPyramid:
    """测试金字塔搜索。"""
    @patch('florr_assistant.modules.pathing.map_classifier.cv2')
    def test_pyramid_search_returns_tuple(self, mock_cv2):
        image = make_mock_image()
        template = make_mock_image()
        mock_cv2.resize.return_value = make_mock_image()
        mock_cv2.matchTemplate.return_value = np.zeros((10, 10), dtype=np.float32)
        mock_cv2.minMaxLoc.side_effect = [
            (0.8, 0.8, (100, 50), (150, 100)),  # coarse
            (0.85, 0.85, (100, 50), (150, 100)),  # fine
        ]

        from florr_assistant.modules.pathing.map_classifier import FullscreenTemplateMatcher
        matcher = FullscreenTemplateMatcher('/fake')
        result = matcher._pyramid_search(image, template, threshold=0.5)
        assert isinstance(result, tuple)
        assert len(result) == 4


class TestFullscreenTemplateMatcherMatch:
    """测试主匹配方法。"""
    @patch('florr_assistant.modules.pathing.map_classifier.cv2')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_match_returns_none_when_no_templates(self, mock_exists, mock_cv2):
        mock_exists.return_value = False
        from florr_assistant.modules.pathing.map_classifier import FullscreenTemplateMatcher
        matcher = FullscreenTemplateMatcher('/fake')
        result = matcher.match(make_mock_image())
        assert result is None

    @patch('florr_assistant.modules.pathing.map_classifier.cv2')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_match_returns_none_when_screenshot_none(self, mock_exists, mock_cv2):
        mock_exists.return_value = False
        from florr_assistant.modules.pathing.map_classifier import FullscreenTemplateMatcher
        matcher = FullscreenTemplateMatcher('/fake')
        result = matcher.match(None)
        assert result is None

    @patch('florr_assistant.modules.pathing.map_classifier.cv2')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    @patch('florr_assistant.modules.pathing.map_classifier.os.listdir')
    def test_match_with_template(self, mock_listdir, mock_exists, mock_cv2):
        mock_exists.return_value = True
        mock_listdir.return_value = ['ocean.png']
        mock_template = make_mock_image()
        mock_cv2.imread.return_value = mock_template
        mock_cv2.resize.return_value = make_mock_image()
        mock_cv2.matchTemplate.return_value = np.zeros((10, 10), dtype=np.float32)
        mock_cv2.minMaxLoc.side_effect = [
            (0.9, 0.9, (10, 10), (100, 100)),  # _multi_scale_match
        ]

        from florr_assistant.modules.pathing.map_classifier import FullscreenTemplateMatcher
        matcher = FullscreenTemplateMatcher('/fake')
        result = matcher.match(make_mock_image(), threshold=0.5)
        assert result is not None

    @patch('florr_assistant.modules.pathing.map_classifier.cv2')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    @patch('florr_assistant.modules.pathing.map_classifier.os.listdir')
    def test_match_with_search_region(self, mock_listdir, mock_exists, mock_cv2):
        mock_exists.return_value = True
        mock_listdir.return_value = ['ocean.png']
        mock_cv2.imread.return_value = make_mock_image()
        mock_cv2.resize.return_value = make_mock_image()
        mock_cv2.matchTemplate.return_value = np.zeros((10, 10), dtype=np.float32)
        mock_cv2.minMaxLoc.side_effect = [
            (0.9, 0.9, (5, 5), (50, 50)),
        ]

        from florr_assistant.modules.pathing.map_classifier import FullscreenTemplateMatcher
        matcher = FullscreenTemplateMatcher('/fake')
        result = matcher.match(
            make_mock_image(),
            threshold=0.5,
            search_region=(500, 0, 640, 200)
        )
        assert result is not None


class TestFullscreenTemplateMatcherMatchAll:
    """测试 match_all 方法。"""
    @patch('florr_assistant.modules.pathing.map_classifier.cv2')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_match_all_returns_empty_when_no_templates(self, mock_exists, mock_cv2):
        mock_exists.return_value = False
        from florr_assistant.modules.pathing.map_classifier import FullscreenTemplateMatcher
        matcher = FullscreenTemplateMatcher('/fake')
        result = matcher.match_all(make_mock_image())
        assert result == []

    @patch('florr_assistant.modules.pathing.map_classifier.cv2')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_match_all_returns_empty_when_screenshot_none(self, mock_exists, mock_cv2):
        mock_exists.return_value = False
        from florr_assistant.modules.pathing.map_classifier import FullscreenTemplateMatcher
        matcher = FullscreenTemplateMatcher('/fake')
        result = matcher.match_all(None)
        assert result == []


class TestMatchResult:
    """测试 MatchResult 数据类。"""
    def test_match_result_creation(self):
        from florr_assistant.modules.pathing.map_classifier import MatchResult
        result = MatchResult(
            map_name='ocean',
            confidence=0.95,
            top_left=(10, 20),
            bottom_right=(110, 120),
            scale=1.2,
            template_size=(100, 100),
            matched_size=(120, 120)
        )
        assert result.map_name == 'ocean'
        assert result.confidence == 0.95
        assert result.scale == 1.2


class TestFullscreenTemplateMatcherHelpers:
    """测试辅助方法。"""
    @patch('florr_assistant.modules.pathing.map_classifier.cv2')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_get_center(self, mock_exists, mock_cv2):
        mock_exists.return_value = False
        from florr_assistant.modules.pathing.map_classifier import FullscreenTemplateMatcher, MatchResult
        matcher = FullscreenTemplateMatcher('/fake')
        result = MatchResult(
            map_name='ocean',
            confidence=0.9,
            top_left=(10, 20),
            bottom_right=(110, 120),
            scale=1.0,
            template_size=(100, 100),
            matched_size=(100, 100)
        )
        center = matcher.get_center(result)
        assert center == (60, 70)

    @patch('florr_assistant.modules.pathing.map_classifier.cv2')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_get_width_height(self, mock_exists, mock_cv2):
        mock_exists.return_value = False
        from florr_assistant.modules.pathing.map_classifier import FullscreenTemplateMatcher, MatchResult
        matcher = FullscreenTemplateMatcher('/fake')
        result = MatchResult(
            map_name='ocean',
            confidence=0.9,
            top_left=(10, 20),
            bottom_right=(110, 120),
            scale=1.0,
            template_size=(100, 100),
            matched_size=(100, 100)
        )
        w, h = matcher.get_width_height(result)
        assert w == 100
        assert h == 100


class TestMapClassifierInit:
    """测试 MapClassifier 初始化。"""
    @patch('florr_assistant.modules.pathing.map_classifier.FullscreenTemplateMatcher')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_init_loads_matcher_if_dir_exists(self, mock_exists, mock_matcher):
        mock_exists.return_value = True
        mock_matcher.return_value.templates = {}
        from florr_assistant.modules.pathing.map_classifier import MapClassifier
        mc = MapClassifier(config={'maps_dir': '/fake/maps'})
        assert mc._matcher is not None

    @patch('florr_assistant.modules.pathing.map_classifier.FullscreenTemplateMatcher')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_init_uses_default_maps_dir(self, mock_exists, mock_matcher):
        mock_exists.return_value = True
        mock_matcher.return_value.templates = {}
        from florr_assistant.modules.pathing.map_classifier import MapClassifier
        mc = MapClassifier()
        assert mc._maps_dir is not None

    @patch('florr_assistant.modules.pathing.map_classifier.FullscreenTemplateMatcher')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_init_uses_config_values(self, mock_exists, mock_matcher):
        mock_exists.return_value = True
        mock_matcher.return_value.templates = {}
        from florr_assistant.modules.pathing.map_classifier import MapClassifier
        mc = MapClassifier(config={
            'maps_dir': '/custom/maps',
            'check_interval': 5.0,
            'confidence_threshold': 0.7,
        })
        assert mc._check_interval == 5.0
        assert mc._confidence_threshold == 0.7


class TestMapClassifierPublicMethods:
    """测试 MapClassifier 公共方法。"""
    @patch('florr_assistant.modules.pathing.map_classifier.FullscreenTemplateMatcher')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_get_current_map_returns_none_initially(self, mock_exists, mock_matcher):
        mock_exists.return_value = False
        mock_matcher.return_value.templates = {}
        from florr_assistant.modules.pathing.map_classifier import MapClassifier
        mc = MapClassifier()
        assert mc.get_current_map() is None

    @patch('florr_assistant.modules.pathing.map_classifier.FullscreenTemplateMatcher')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_get_map_info_returns_none_initially(self, mock_exists, mock_matcher):
        mock_exists.return_value = False
        mock_matcher.return_value.templates = {}
        from florr_assistant.modules.pathing.map_classifier import MapClassifier
        mc = MapClassifier()
        assert mc.get_map_info() is None

    @patch('florr_assistant.modules.pathing.map_classifier.FullscreenTemplateMatcher')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_get_stats_returns_dict(self, mock_exists, mock_matcher):
        mock_exists.return_value = False
        mock_matcher.return_value.templates = {}
        from florr_assistant.modules.pathing.map_classifier import MapClassifier
        mc = MapClassifier()
        stats = mc.get_stats()
        assert isinstance(stats, dict)
        assert 'current_map' in stats
        assert 'classification_count' in stats
        assert 'templates_loaded' in stats

    @patch('florr_assistant.modules.pathing.map_classifier.FullscreenTemplateMatcher')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_get_matcher_returns_matcher(self, mock_exists, mock_matcher):
        mock_exists.return_value = False
        mock_matcher_instance = mock_matcher.return_value
        mock_matcher_instance.templates = {}
        from florr_assistant.modules.pathing.map_classifier import MapClassifier
        mc = MapClassifier()
        assert mc.get_matcher() is not None

    @patch('florr_assistant.modules.pathing.map_classifier.FullscreenTemplateMatcher')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_classify_returns_none_when_matcher_none(self, mock_exists, mock_matcher):
        mock_exists.return_value = False
        mock_matcher.return_value = None
        from florr_assistant.modules.pathing.map_classifier import MapClassifier
        mc = MapClassifier()
        result = mc._classify(make_mock_image())
        assert result is None

    @patch('florr_assistant.modules.pathing.map_classifier.FullscreenTemplateMatcher')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_classify_returns_none_when_screenshot_none(self, mock_exists, mock_matcher):
        mock_exists.return_value = False
        mock_matcher.return_value = None
        from florr_assistant.modules.pathing.map_classifier import MapClassifier
        mc = MapClassifier()
        result = mc._classify(None)
        assert result is None


class TestMapClassifierSearchRegion:
    """测试搜索区域计算。"""
    @patch('florr_assistant.modules.pathing.map_classifier.FullscreenTemplateMatcher')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_search_region_is_top_right(self, mock_exists, mock_matcher):
        mock_exists.return_value = False
        mock_matcher.return_value = None
        from florr_assistant.modules.pathing.map_classifier import MapClassifier
        mc = MapClassifier()
        screenshot = make_mock_image((480, 640, 3))
        region = mc._get_search_region(screenshot)
        x1, y1, x2, y2 = region
        assert x2 == 640
        assert y2 == int(480 * 0.4)  # 40% of height
        assert x1 == int(640 * 0.65)  # right 35%


class TestMapClassifierInheritance:
    """测试 MapClassifier 继承自 BaseModule。"""
    @patch('florr_assistant.modules.pathing.map_classifier.FullscreenTemplateMatcher')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_inherits_from_base_module(self, mock_exists, mock_matcher):
        mock_exists.return_value = False
        mock_matcher.return_value = None
        from florr_assistant.modules.pathing.map_classifier import MapClassifier
        from florr_assistant.modules.base import BaseModule
        assert issubclass(MapClassifier, BaseModule)

    @patch('florr_assistant.modules.pathing.map_classifier.FullscreenTemplateMatcher')
    @patch('florr_assistant.modules.pathing.map_classifier.os.path.exists')
    def test_has_required_class_attributes(self, mock_exists, mock_matcher):
        mock_exists.return_value = False
        mock_matcher.return_value = None
        from florr_assistant.modules.pathing.map_classifier import MapClassifier
        assert MapClassifier.name == 'map_classifier'
        assert MapClassifier.version == '3.0.0'
        assert MapClassifier.priority == 90
