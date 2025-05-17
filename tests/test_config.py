import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from kcd_dice_game.utils.config import Config


@pytest.fixture
def config_dir(tmp_path):
    """Create a temporary config directory with test files."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Create camera.json (required for Config initialization)
    camera_config = {
        "camera_index": 0,
        "max_num_lasers_to_show": 4,
        "laser_detection": {"area_range": {"min": 5, "max": 150}},
    }
    with open(config_dir / "camera.json", "w") as f:
        json.dump(camera_config, f)

    # Create main.json (needed for some tests)
    main_config = {"foo": "bar"}
    with open(config_dir / "main.json", "w") as f:
        json.dump(main_config, f)

    return config_dir


@pytest.fixture(autouse=True)
def mock_paths(config_dir, monkeypatch):
    """Mock path resolution for config files."""
    def mock_resolve(self):
        return self

    # Create a mock Path class that returns our test directory structure
    class MockPath(Path):
        _flavour = Path()._flavour  # Needed for Path methods to work
        
        def __new__(cls, *args, **kwargs):
            if args and str(args[0]).endswith('__file__'):
                # When Path(__file__) is called, return our mock path
                mock = MagicMock()
                mock.parents = [MagicMock() for _ in range(4)]
                mock.parents[3] = config_dir.parent
                mock.__truediv__ = lambda self, other: Path(config_dir.parent / other)
                return mock
            return Path(*args, **kwargs)
    
    # Patch Path in the config module
    monkeypatch.setattr('kcd_dice_game.utils.config.Path', MockPath)


def test_config_singleton(config_dir):
    """Test that Config is a singleton."""
    # Clear any existing instances
    Config._instance = None
    Config._configs = {}
    
    config1 = Config()
    config2 = Config()
    assert config1 is config2


def test_config_loading(config_dir):
    """Test that configuration is loaded correctly."""
    # Clear any existing instances
    Config._instance = None
    Config._configs = {}
    
    # Create a config instance
    config = Config()
    
    # Test basic values
    camera_index = config.get("camera.camera_index")
    assert camera_index == 0, f"Expected camera_index to be 0, got {camera_index}"
    
    max_lasers = config.get("camera.max_num_lasers_to_show")
    assert max_lasers == 4, f"Expected max_num_lasers_to_show to be 4, got {max_lasers}"

    # Test nested values
    min_area = config.get("camera.laser_detection.area_range.min")
    assert min_area == 5, f"Expected area_range.min to be 5, got {min_area}"
    
    max_area = config.get("camera.laser_detection.area_range.max")
    assert max_area == 150, f"Expected area_range.max to be 150, got {max_area}"

    # Test default values
    assert config.get("non.existent.key", "default") == "default"

    # Test getting all config
    all_config = config.get_all("camera")
    assert "camera_index" in all_config, "camera_index not found in config"
    assert "laser_detection" in all_config, "laser_detection not found in config"


def test_set_and_save_config(config_dir):
    """Test setting and saving configuration values."""
    # Clear any existing instances
    Config._instance = None
    Config._configs = {}
    
    # Create a config instance
    config = Config()
    
    # Use a new config file for testing saves
    test_file = "test_save.json"
    config_name = test_file[:-5]  # Remove .json

    # Set new values
    config.set(f"{config_name}.new_key", "new_value")
    config.set(f"{config_name}.nested.key", "nested_value")

    # Verify values in memory
    assert config.get(f"{config_name}.new_key") == "new_value"
    assert config.get(f"{config_name}.nested.key") == "nested_value"

    # Save config to test file
    config.save_config(config_name)

    # Verify file was created and updated
    test_file_path = config_dir / test_file
    assert test_file_path.exists(), f"Config file {test_file_path} was not created"
    
    with test_file_path.open() as f:
        saved_config = json.load(f)
        assert saved_config["new_key"] == "new_value", f"Expected 'new_key' to be 'new_value', got {saved_config.get('new_key')}"
        assert saved_config["nested"]["key"] == "nested_value", f"Expected nested.key to be 'nested_value', got {saved_config.get('nested', {}).get('key')}"


def test_get_all(config_dir):
    """Test getting all configurations."""
    # Clear any existing instances
    Config._instance = None
    Config._configs = {}
    
    # Create a config instance
    config = Config()
    
    # Get specific config
    main_config = config.get_all("main")
    assert "foo" in main_config, "Expected 'foo' key in main config"
    assert main_config["foo"] == "bar", f"Expected 'foo' to be 'bar', got {main_config.get('foo')}"

    # Test non-existent config
    empty_config = config.get_all("non_existent")
    assert empty_config == {}, f"Expected empty dict for non-existent config, got {empty_config}"


def test_invalid_config(config):
    """Test handling of invalid configurations."""
    # Test invalid key format
    with pytest.raises(ValueError):
        config.set("invalid", "value")  # Missing dot separator

    # Test getting from non-existent config
    assert config.get("nonexistent.key") is None
