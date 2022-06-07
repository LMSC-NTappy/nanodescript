from nanodescript.describe_recipe_handler import DescribeRecipe
from nanodescript.constants import DEFAULT_RECIPE

from pytest import raises
from pathlib import Path

here_path = Path(__file__).parent


class TestGwlHandler:
    def setup_class(self):
        self.t = DescribeRecipe()

    def test_init(self):
        assert self.t.recipe == DEFAULT_RECIPE

    def test_check_field(self):
        assert self.t.check_recipe_field("Model.Rotation")
        assert not self.t.check_recipe_field("Model.Domination_station")

    def test_recipe_fromfile(self):
        # Test initialisation of a recipe from a file
        t2 = DescribeRecipe(here_path.joinpath("test_data\\test_ref_recipe.recipe"))
        assert t2.recipe['Model.FilePath'] == \
               r"\\sti1files.epfl.ch\lmsc-commun\Nicolas\Software\descript_python\tests\test_data\cross_20_80.stl"

    def test_update_recipe(self):
        stlfilepath = here_path.joinpath('test_data\\cross_20_80.stl').resolve()
        assert stlfilepath.is_file()

        self.t.update_recipe('Model.FilePath', stlfilepath)
        assert self.t.recipe['Model.FilePath'] == str(stlfilepath.resolve())

        with raises(ValueError):
            self.t.update_recipe('Mobylette', 'rouge')

    def test_strtobool(self):
        assert self.t._strtobool("True")
        assert self.t._strtobool("true")
        assert self.t._strtobool("1")
        assert self.t._strtobool("TRUE")

        assert not self.t._strtobool("False")
        assert not self.t._strtobool("false")
        assert not self.t._strtobool("0")
        assert not self.t._strtobool("FALSE")

        with raises(ValueError):
            self.t._strtobool('invalid_str')

    def test_write_recipe(self, tmp_path):
        self.t.process_stl(here_path.joinpath('test_data\\cross_20_80.stl').resolve())

        recipepath = tmp_path.joinpath('test_recipe.recipe').resolve()

        self.t.write_recipe(str(recipepath))

        assert recipepath.exists() & recipepath.is_file()

        ref_recipe_file = here_path.joinpath('test_data\\test_ref_recipe.recipe').resolve()

        assert self.t.recipe == DescribeRecipe(recipe_file=ref_recipe_file).recipe

    def test_get_boundingbox(self):
        test_rec = DescribeRecipe()
        test_rec.recipe['Model.BoundingBox'] = "Minimum:X:-0.000 Y:0.000 Z:0.000 Maximum:X:95.000 Y:95.000 Z:9.000"
        xmin, ymin, zmin, xmax, ymax, zmax = test_rec.get_bounding_box()

        assert xmin == 0.000
        assert ymin == 0.000
        assert zmin == 0.000
        assert xmax == 95.000
        assert ymax == 95.000
        assert zmax == 9.000

        #Missing key raises
        test_rec.recipe['Model.BoundingBox'] = "Minimum:X:-0.000 Y:0.000 Z:0.000 Maximum:X:95.000 Y:95.000 "

        with raises(ValueError):
            test_rec.get_bounding_box()

    def test_generate_gwl(self, tmp_path):

        gwl_file_loc = tmp_path.joinpath('tmp')

        self.t.generate_gwl_code(tmp_recipe=gwl_file_loc)

        assert self.t.out_files == gwl_file_loc.parent.joinpath('tmp_output\\cross_20_80_files').resolve()
        assert self.t.out_recipe == gwl_file_loc.parent.joinpath('tmp_output\\cross_20_80_job.recipe').resolve()
        assert self.t.out_jobgwl == gwl_file_loc.parent.joinpath('tmp_output\\cross_20_80_job.gwl').resolve()
        assert self.t.out_datgwl == gwl_file_loc.parent.joinpath('tmp_output\\cross_20_80_data.gwl').resolve()
