from pathlib import Path
import copy
from configparser import NoSectionError, NoOptionError

import pytest

from nanodescript.config import nanodescript_config as conf

from nanodescript.constants import DEFAULT_RECIPE

here_path = Path(__file__).parent


class TestGwlHandler:

    @classmethod
    def setup_class(self):
        """ setup the initial configuration state to default while back-uping
        """

        self.bkup_conf = copy.deepcopy(conf)
        conf.reset_config()

    @classmethod
    def teardown_class(self):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        conf = self.bkup_conf
        conf.save_config()

    def test_path(self):
        p = conf.get_config_path()
        assert p.exists()

    def test_delete_and_reset(self):
        p = conf.get_config_path()
        p.unlink()
        assert not p.exists()

        conf.reset_config()

        assert p.exists()

    def test_sections(self):
        assert conf.sections() == ['paths',
                                   'identifiers',
                                   'describe_output_suffixes',
                                   'gds_handler',
                                   'layermatcher',
                                   'layerdatatypematcher',
                                   'printzonematcher',
                                   'default_recipe']

    @pytest.mark.parametrize('input_section,expected_options',
                             [('paths', ['describe']),
                              ('identifiers', ['is_nanoscribe', 'stl_file_path']),
                              ('describe_output_suffixes', ['folder', 'datgwl', 'jobgwl', 'recipe', 'files']),
                              ('gds_handler', ['topcell', 'matcher']),
                              ('layermatcher', ['layer_number']),
                              ('layerdatatypematcher', ['layer_number', 'datatype_number']),
                              ('printzonematcher', ['printzone_name']),
                              ('default_recipe', list(DEFAULT_RECIPE.keys())),
                              ])
    def test_options(self, input_section, expected_options):
        assert conf.options(input_section) == expected_options

    def test_create_on_load(self):
        p = conf.get_config_path()
        p.unlink()
        assert not p.exists()

        conf.load_config()

        assert p.exists()

    def test_edit_config(self):
        conf.reset_config()

        with pytest.raises(NoOptionError):
            conf.edit_config('identifiers', 'bottomcell', 'ttcc')

        with pytest.raises(NoSectionError):
            conf.edit_config('anonymizers', 'bottomcell', 'ttcc')

        conf.edit_config('gds_handler', 'topcell', 'TC')

        assert conf['gds_handler']['topcell'] == 'TC'

        conf.reset_config()

        assert conf['gds_handler']['topcell'] == 'topcell'

    def test_save_config(self):
        conf.reset_config()

        conf.edit_config('gds_handler', 'topcell', 'TC', also_save=True)

        conf.reload_config()

        assert conf['gds_handler']['topcell'] == 'TC'

        conf.reset_config()
