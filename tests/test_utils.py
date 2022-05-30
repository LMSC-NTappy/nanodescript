from pathlib import Path

from gdstk import read_gds, Cell, Library
from pytest import raises

import nanodescript.utils
from nanodescript.describe_recipe_handler import DescribeRecipe
from nanodescript import describe_commands as cmds

test_pattern = "test_data/test_pattern.gds"


class TestUtils:
    def setup_class(self):
        self.lib = read_gds(test_pattern)

    def test_find_stl_files(self):
        assert not nanodescript.utils.find_stl_files(Path('.'), recursive=False)
        assert nanodescript.utils.find_stl_files(Path('test_data'), recursive=True) == \
               [Path('test_data/cross_20_80.stl'),
                Path('test_data/tip.stl')]

        assert nanodescript.utils.find_stl_files(Path('.'), recursive=True) == \
               [Path('test_data/cross_20_80.stl'),
                Path('test_data/tip.stl')]

    def test_find_cell_by_name(self):
        c = nanodescript.utils.find_cell_by_name(library=self.lib,name="tip")
        assert type(c) == Cell

        with raises(ValueError):
            nanodescript.utils.find_cell_by_name(library=self.lib,name='bicyclette')

    def test_find_topcell(self):
        tc = nanodescript.utils.find_topcell(self.lib)
        assert type(tc) == Cell

        with raises(ValueError):
            nanodescript.utils.find_topcell(Library())

