from configparser import ConfigParser
from typing import Dict, Tuple
from pathlib import Path

class ConfigManager:
    """
    Manages configuration settings for the classroom simulation.
    Loads parameters from a config file and provides easy access to them.
    """
    def __init__(self, config_file: str = "config.ini"):
        """
        Initializes the configuration manager.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config = ConfigParser()
        self.config_file = Path(config_file)
        
        # Load default values first
        self._set_defaults()
        
        # Then load from file if it exists
        if self.config_file.exists():
            self.config.read(config_file)
        else:
            # Create config file with default values if it doesn't exist
            self.save_config()

    def _set_defaults(self):
        """Sets default values for all configuration parameters"""
        self.config["CLASSROOM"] = {
            "width": "30",
            "height": "30",
            "safe_zone_width": "6",
            "safe_zone_height": "6"
        }
        
        self.config["AGENTS"] = {
            "num_random_walkers": "5",
            "num_candy_seekers": "5",
            "num_avoiders": "5",
            "num_directional": "4",
            "num_strategic_timers": "4",
            "num_wall_huggers": "4",
            "num_group_seekers": "3",
            "num_candy_hoarders": "3",
            "num_safe_explorers": "3",
            "num_unpredictable": "3",
            "num_teachers": "1"
        }
        
        self.config["TIMING"] = {
            "visualization_fps": "2",
            "candy_spawn_interval": "3",
            "child_cooldown": "5.0",
            "strategic_timing_min": "0.5",
            "strategic_timing_max": "2.0"
        }
        
        self.config["VISUALIZATION"] = {
            "cell_size": "25"
        }

    def save_config(self):
        """Saves current configuration to file"""
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    @property
    def classroom_size(self) -> Tuple[int, int]:
        """Returns the classroom dimensions"""
        return (
            self.config.getint("CLASSROOM", "width"),
            self.config.getint("CLASSROOM", "height")
        )

    @property
    def safe_zone_size(self) -> Tuple[int, int]:
        """Returns the safe zone dimensions"""
        return (
            self.config.getint("CLASSROOM", "safe_zone_width"),
            self.config.getint("CLASSROOM", "safe_zone_height")
        )

    @property
    def agent_counts(self) -> Dict[str, int]:
        """Returns the number of agents for each strategy"""
        return {
            key: self.config.getint("AGENTS", key)
            for key in self.config["AGENTS"]
        }

    @property
    def fps(self) -> int:
        """Returns visualization frame rate"""
        return self.config.getint("TIMING", "visualization_fps")

    @property
    def candy_spawn_interval(self) -> int:
        """Returns interval between candy spawns"""
        return self.config.getint("TIMING", "candy_spawn_interval")

    @property
    def child_cooldown(self) -> float:
        """Returns cooldown duration for children"""
        return self.config.getfloat("TIMING", "child_cooldown")

    @property
    def strategic_timing_range(self) -> Tuple[float, float]:
        """Returns range for strategic timing delays"""
        return (
            self.config.getfloat("TIMING", "strategic_timing_min"),
            self.config.getfloat("TIMING", "strategic_timing_max")
        )

    @property
    def cell_size(self) -> int:
        """Returns visualization cell size"""
        return self.config.getint("VISUALIZATION", "cell_size")