import json
import os
from typing import Dict, Any

class Config:
    _instance = None
    _configs: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._configs:
            self.load_config()

    def load_config(self, config_name: str = 'default') -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_name (str): Name of the config file without .json extension.
                             Will load from config/{config_name}.json
        """
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        config_dir = os.path.join(root_dir, 'config')
        config_path = os.path.join(config_dir, f"{config_name}.json")

        try:
            with open(config_path, 'r') as f:
                self._configs[config_name] = json.load(f)
        except FileNotFoundError:
            # If file doesn't exist, create it with empty config
            self._configs[config_name] = {}
            # Ensure the directory exists before creating the file
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump({}, f, indent=4)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file: {config_path}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key (str): The configuration key (format: 'file_name.nested.key')
                      First part is the config file name without .json
            default: The default value to return if the key is not found
            
        Returns:
            The configuration value or default if not found
            
        Example:
            config.get('main.foo')  # Gets 'foo' from main.json
            config.get('default.camera.index')  # Gets 'camera.index' from default.json
        """
        parts = key.split('.')
        if len(parts) < 2:
            return default

        config_name = parts[0]
        key_path = parts[1:]

        # Load config file if not already loaded
        if config_name not in self._configs:
            try:
                self.load_config(config_name)
            except (FileNotFoundError, ValueError):
                return default

        # Navigate through the config
        value = self._configs[config_name]
        for k in key_path:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
                
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value by key.
        
        Args:
            key (str): The configuration key (format: 'file_name.nested.key')
                      First part is the config file name without .json
            value: The value to set
            
        Example:
            config.set('main.foo', 'new_value')
            config.set('default.camera.index', 0)
        """
        parts = key.split('.')
        if len(parts) < 2:
            raise ValueError("Key must be in format 'file_name.nested.key'")

        config_name = parts[0]
        key_path = parts[1:]

        # Load or initialize config if not exists
        if config_name not in self._configs:
            try:
                self.load_config(config_name)
            except FileNotFoundError:
                self._configs[config_name] = {}

        # Navigate and create nested dictionaries
        current = self._configs[config_name]
        for k in key_path[:-1]:
            if k not in current:
                current[k] = {}
            elif not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
            
        # Set the value at the final key
        current[key_path[-1]] = value

    def save_config(self, config_name: str = 'default') -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            config_name (str): Name of the config file without .json extension
        """
        if config_name not in self._configs:
            raise ValueError(f"No configuration loaded for '{config_name}'")

        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_dir = os.path.join(root_dir, 'config')
        config_path = os.path.join(config_dir, f"{config_name}.json")

        # Ensure the directory exists
        os.makedirs(config_dir, exist_ok=True)

        try:
            with open(config_path, 'w') as f:
                json.dump(self._configs[config_name], f, indent=4)
        except IOError as e:
            raise IOError(f"Failed to save configuration file: {config_path}. Error: {str(e)}")

    def get_all(self, config_name: str) -> Dict[str, Any]:
        """
        Get the entire configuration dictionary for a specific config file.
        
        Args:
            config_name (str): Name of the config file without .json extension
        """
        if config_name not in self._configs:
            try:
                self.load_config(config_name)
            except (FileNotFoundError, ValueError):
                return {}
        return self._configs[config_name].copy() 