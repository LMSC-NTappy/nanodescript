from pathlib import Path
from configparser import SafeConfigParser, NoSectionError, NoOptionError

from platformdirs import user_config_path

import nanodescript.constants as cst

__all__ = ['nanodescript_config']


class CaseConfigParser(SafeConfigParser):
    def optionxform(self, optionstr):
        return optionstr


class NanodescriptConfig:
    def __init__(self, ):
        """Initialize the NanodescriptConfig object"""
        self.config_path = self.get_config_path()
        # Inner ConfigParser Object
        self.config = self.load_config()
        self.config.optionxform = str

    def __getitem__(self, item):
        return self.config[item]

    @staticmethod
    def get_config_path() -> Path:
        """Get the location of the configuration file"""
        return user_config_path(appname='nanodescript', appauthor=False).joinpath('nanodescript_config.ini')

    @staticmethod
    def _get_default_config() -> CaseConfigParser:
        """Get the default Config Parser"""
        config = CaseConfigParser()

        config['paths'] = {'describe': cst.DESCRIBE_DEFAULT_PATH}

        config['identifiers'] = {
            'is_nanoscribe': cst.NANOSCRIBEPROPERTY,
            'stl_file_path': cst.STLPROPERTY
        }

        config['describe_output_suffixes'] = {
            'folder': cst.DESCRIBE_OUTPUT_FOLDER_SUFFIX,
            'datgwl': cst.DESCRIBE_OUTPUT_DATGWL_SUFFIX,
            'jobgwl': cst.DESCRIBE_OUTPUT_JOBGWL_SUFFIX,
            'recipe': cst.DESCRIBE_OUTPUT_RECIPE_SUFFIX,
            'files': cst.DESCRIBE_OUTPUT_FILES_SUFFIX
        }

        config['gds_handler'] = {
            'topcell': cst.TOPCELLNAME,
            'matcher': cst.MATCHER_NAME,
        }

        config['layermatcher'] = {
            'layer_number': cst.LAYER_NUMBER,
        }

        config['layerdatatypematcher'] = {
            'layer_number': cst.LAYER_NUMBER,
            'datatype_number': cst.DATATYPE_NUMBER,
        }

        config['printzonematcher'] = {
            'printzone_name': cst.PRINTZONE_NAME
        }

        config['default_recipe'] = cst.DEFAULT_RECIPE

        return config

    def get_default_recipe(self):
        return dict(self.config['default_recipe'])

    def load_config(self) -> CaseConfigParser:
        """Load the configuration file. Also create it
         and parent directories if it does not exist."""

        if not self.config_path.exists():
            self.reset_config()

        config = CaseConfigParser()
        with self.config_path.open('r') as cf:
            config.read_file(cf)

        return config

    def reload_config(self):
        """Reload the configuration from disk"""
        self.config = self.load_config()

    def reset_config(self, also_save=True) -> None:
        """Reset the configuration file to default values. Also create it
         and parent directories if they do not exist."""

        # Make sure the directory exists in case it has been deleted
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        self.config = self._get_default_config()

        # Save it if also
        if also_save or not self.config_path.exists():
            self.save_config()
            self.reload_config()

    def save_config(self, path: Path = None) -> None:
        """Save the current state of the configuration"""
        if path is None:
            path = self.config_path

        with path.open('w') as cf:
            self.config.write(cf)

    def edit_config(self, section, option, val, also_save: bool = False) -> None:
        """Edit the configuration"""

        if self.config.has_option(section, option):
            self.config.set(section, option, str(val))
        else:
            if not self.config.has_section(section):
                raise NoSectionError(section=section)
            else:
                raise NoOptionError(section=section, option=option)
        if also_save:
            self.save_config()

    def get(self, section: str, option: str) -> str:
        """Get a configuration value"""
        return self.config.get(section, option)

    def sections(self):
        return self.config.sections()

    def options(self, section):
        return self.config.options(section)

    def _set_config(self, other_config):
        self.config = other_config.config


nanodescript_config = NanodescriptConfig()
