from nanodescript.describe_gds_handler import NanoscribeGdsHandler
from nanodescript.constants import DEFAULT_RECIPE
from nanodescript.nanoscribe_matchers import PrintZoneMatcher
from nanodescript.utils import find_topcell

from pathlib import Path
from gdstk import Cell
from pytest import raises

TESTLIB = r"Y:\Nicolas\Software\descript_python\tests\test_data\test_pattern_printzonematcher.gds"
OUTDIR = r"Y:\Nicolas\Software\descript_python\tests\test_pattern"

heredir = Path(__file__).parent


class TestNanoscribeGdsHandler:
    def setup_class(self):
        self.t_h = NanoscribeGdsHandler(library=Path(TESTLIB), out_dir=Path(OUTDIR))

    def test_init(self):
        assert self.t_h.library.name == "Test_Tip_Pattern"

    def test_no_nanoscribe_cells(self):
        with raises(RuntimeError):
            self.t_h.get_nanoscribe_cells()

    def test_set_nanoscribe_cell(self):
        tc = Cell('test')

        with raises(AttributeError):
            self.t_h.set_nanoscribe_cell(tc, False)

        tc = self.t_h.library.cells[0]

        self.t_h.reset_nanoscribe_cells()
        self.t_h.set_nanoscribe_cell(tc, True)

        nsc = self.t_h.get_nanoscribe_cells()

        assert len(nsc) == 1 and nsc[0] == tc

    def test_set_library(self):
        assert self.t_h.library.name == 'Test_Tip_Pattern'
        assert self.t_h.describerecipe.recipe == DEFAULT_RECIPE
        assert self.t_h.topcell is None

        matcher = PrintZoneMatcher()
        self.t_h.set_matcher(matcher)
        tc = find_topcell(library=self.t_h.library)
        self.t_h.assign_topcell(tc)

        assert self.t_h.topcell.name == 'TOPCELL'

        self.t_h.find_nanoscribe_cells()

        nsc = self.t_h.get_nanoscribe_cells()

        assert [c.name for c in nsc] == ['tip', 'cross_20_80', ]

        self.t_h.match_stl_files()

        nsc_stl = [(c[0].name, c[1].resolve()) for c in self.t_h.get_cells_matched_with_stl_files()]

        assert nsc_stl == [('tip', heredir.joinpath('test_data/tip.stl').resolve()),
                           ('cross_20_80', heredir.joinpath('test_data/cross_20_80.stl').resolve())]

        self.t_h.find_nanoscribe_instances_and_transformations()

        assert self.t_h.nanoscribe_cells_associations

    def test_output_directory(self, tmp_path):
        self.t_h.output_directory = tmp_path
