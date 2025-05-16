import pytest
import os
import json
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


@pytest.fixture
def config(config_dir, monkeypatch):
    """Create a Config instance with the test config directory."""
    # Store the original abspath and dirname functions
    original_abspath = os.path.abspath
    original_dirname = os.path.dirname

    def mock_abspath(path):
        if "__file__" in str(path):
            # When getting the config.py file path, return a path that will work with our mock
            return os.path.join(
                str(config_dir.parent), "src", "kcd_dice_game", "utils", "config.py"
            )
        return original_abspath(path)

    def mock_dirname(path):
        if (
            "src/kcd_dice_game/utils/config.py" in path
            or "src\\kcd_dice_game\\utils\\config.py" in path
        ):
            return os.path.join(str(config_dir.parent), "src", "kcd_dice_game", "utils")
        elif "src/kcd_dice_game/utils" in path or "src\\kcd_dice_game\\utils" in path:
            return os.path.join(str(config_dir.parent), "src", "kcd_dice_game")
        elif "src/kcd_dice_game" in path or "src\\kcd_dice_game" in path:
            return os.path.join(str(config_dir.parent), "src")
        elif "src" in path:
            return str(config_dir.parent)
        return original_dirname(path)

    monkeypatch.setattr(os.path, "abspath", mock_abspath)
    monkeypatch.setattr(os.path, "dirname", mock_dirname)

    # Clear the Config singleton state
    Config._instance = None
    Config._configs = {}

    return Config()


def test_config_singleton():
    """Test that Config is a singleton."""
    config1 = Config()
    config2 = Config()
    assert config1 is config2


def test_config_loading(config):
    """Test that configuration is loaded correctly."""
    # Test basic values
    assert config.get("camera.camera_index") == 0
    assert config.get("camera.max_num_lasers_to_show") == 4

    # Test nested values
    assert config.get("camera.laser_detection.area_range.min") == 5
    assert config.get("camera.laser_detection.area_range.max") == 150

    # Test default values
    assert config.get("non.existent.key", "default") == "default"

    # Test getting all config
    all_config = config.get_all("camera")
    assert "camera_index" in all_config
    assert "laser_detection" in all_config


def test_set_and_save_config(config, config_dir):
    """Test setting and saving configuration values."""
    # Use a new config file for testing saves
    test_file = "test_save.json"

    # Set new values
    config.set(f"{test_file[:-5]}.new_key", "new_value")
    config.set(f"{test_file[:-5]}.nested.key", "nested_value")

    # Verify values in memory
    assert config.get(f"{test_file[:-5]}.new_key") == "new_value"
    assert config.get(f"{test_file[:-5]}.nested.key") == "nested_value"

    # Save config to test file
    config.save_config(test_file[:-5])

    # Verify file was created and updated
    with open(config_dir / test_file) as f:
        saved_config = json.load(f)
        assert saved_config["new_key"] == "new_value"
        assert saved_config["nested"]["key"] == "nested_value"


def test_get_all(config):
    """Test getting all configurations."""
    # Get specific config
    main_config = config.get_all("main")
    assert "foo" in main_config

    # Test non-existent config
    empty_config = config.get_all("non_existent")
    assert empty_config == {}


def test_invalid_config(config):
    """Test handling of invalid configurations."""
    # Test invalid key format
    with pytest.raises(ValueError):
        config.set("invalid", "value")  # Missing dot separator

    # Test getting from non-existent config
    assert config.get("nonexistent.key") is None
