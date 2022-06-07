import subprocess
from pathlib import Path
import logging
import re

from nanodescript.stl_handler import StlFile
from nanodescript.cell_transformation import CellTransformation
from nanodescript.config import nanodescript_config

from nanodescript.constants import DEFAULT_RECIPE, DESCRIBE_OUTPUT_FOLDER_SUFFIX, \
    DESCRIBE_OUTPUT_JOBGWL_SUFFIX, DESCRIBE_OUTPUT_DATGWL_SUFFIX, DESCRIBE_OUTPUT_FILES_SUFFIX, \
    DESCRIBE_OUTPUT_RECIPE_SUFFIX

logger = logging.getLogger(__name__)


class DescribeRecipe:
    """Class to process Describe Recipes."""

    def __init__(self, recipe_file: Path = None):
        # If a custom recipe is provided, use it
        # otherwise initialise with default recipe
        if recipe_file is not None:
            self.recipe = self._recipe_from_file(recipe_file)
        else:
            self.recipe = self._recipe_from_config()

        self.out_datgwl: Path = None  # output gwl file with the data
        self.out_jobgwl: Path = None  # output gwl file with the full job
        self.out_recipe: Path = None  # output recipe file (backup)
        self.out_files: Path = None  # output files directory

    @staticmethod
    def check_recipe_field(field: str) -> bool:
        """Verify if a key is canonical in a describe recipe."""
        return field in DEFAULT_RECIPE.keys()

    @staticmethod
    def _strtobool(s: str) -> bool:
        """
        Convert str to bool based on the string content. This is needed to circumvent python default behaviour
        which is that any str that is not empty is casted to True. Case-sensitive. Cast to True: ["1","True"]
        Cast to False: ["0","False"]
        """
        true_like = ["1", "true"]
        false_like = ["0", "false"]
        if s.lower() in true_like:
            return True
        elif s.lower() in false_like:
            return False
        else:
            raise ValueError(f"{s} str invalid for casting to boolean")

    def update_recipe(self, key: str, val) -> None:
        if self.check_recipe_field(field=key):
            # Here we cast the value passed as argument as the same type as the default recipe, bool str float etc.
            # This also ensures that an error is raised if something weird happens
            self.recipe[key] = type(DEFAULT_RECIPE[key])(val)
        # Otherwise raise an error
        else:
            raise ValueError(f"key {key} is not a valid Describe Recipe key")

    def update_transformation(self, transformation: CellTransformation, translation: bool, fmt=".3f") -> None:
        """Update the current transformation in the recipe"""
        # Transformation as a 4x4 matrix ignoring translation
        m = transformation.get_transformation_matrix(with_translation=translation)

        transformationstring = f"[M11:{m[0, 0]:{fmt}} M12:{m[0, 1]:{fmt}} M13:{m[0, 2]:{fmt}} M14:{m[0, 3]:{fmt}}] " + \
                               f"[M21:{m[1, 0]:{fmt}} M22:{m[1, 1]:{fmt}} M23:{m[1, 2]:{fmt}} M24:{m[1, 3]:{fmt}}] " + \
                               f"[M31:{m[2, 0]:{fmt}} M32:{m[2, 1]:{fmt}} M33:{m[2, 2]:{fmt}} M34:{m[2, 3]:{fmt}}] " + \
                               f"[M41:{m[3, 0]:{fmt}} M42:{m[3, 1]:{fmt}} M43:{m[3, 2]:{fmt}} M44:{m[3, 3]:{fmt}}]"

        self.update_recipe("Model.Transformation", transformationstring)

    def process_stl(self,
                    stlpath: Path,
                    transformation: CellTransformation = CellTransformation(),
                    fmt=".3f",
                    ) -> None:
        """
        Update the recipe file with the model informations. fmt argument can be used to set precision for writing the
        float values
        """
        # We initialise an Stl Mesh object
        stl = StlFile(filename=stlpath)
        fullpathstring = f"{stl.full_path}"

        # Boundingboxstring is the bounding-box-defining string
        boundingboxstring = f"Minimum:X:{stl.min_[0]:{fmt}} " + \
                            f"Y:{stl.min_[1]:{fmt}} " + \
                            f"Z:{stl.min_[2]:{fmt}} " + \
                            f"Maximum:X:{stl.max_[0]:{fmt}} " + \
                            f"Y:{stl.max_[1]:{fmt}} " + \
                            f"Z:{stl.max_[2]:{fmt}}"

        # Transformation update
        self.update_transformation(transformation, translation=False)

        # Rotation as a quaternion
        quat = transformation.get_rotation_quaternion()
        rotationstring = f"X:{quat[0]:{fmt}} Y:{quat[1]:{fmt}} Z:{quat[2]:{fmt}} W:{quat[3]:{fmt}}"

        # Scaling
        s = transformation.magnification
        scalingstring = f"X:{s:{fmt}} Y:{s:{fmt}} Z:{s:{fmt}}"

        self.update_recipe("Model.Type", "Mesh")
        self.update_recipe("Model.FilePath", fullpathstring)
        self.update_recipe("Model.BoundingBox", boundingboxstring)
        self.update_recipe("Model.Rotation", rotationstring)
        self.update_recipe("Model.Scaling", scalingstring)
        self.update_recipe("Model.Translation", "X:0 Y:0 Z:0")

    def get_bounding_box(self) -> (float, float, float, float, float, float):
        """Get the bounding box in floating point values"""
        bbox = self.recipe['Model.BoundingBox']
        bsplit = re.split(':| ', bbox)
        result = []
        for s in bsplit:
            if s is not False and s not in ['Minimum','Maximum','X','Y','Z']:
                result.append(float(s))
        xmin = result[0]
        ymin = result[1]
        zmin = result[2]
        xmax = result[3]
        ymax = result[4]
        zmax = result[5]
        return xmin, ymin, zmin, xmax, ymax, zmax

    def _recipe_from_config(self,) -> dict:
        """Return the recipe from the configuration file"""
        config_recipe = nanodescript_config['default_recipe']

        resdict = {}

        for key, val in config_recipe.items():
            casted = self._cast_recipe_key_val(key, val)
            resdict.update(casted)
        return resdict

    def _recipe_from_file(self, recipe_file: Path) -> dict:
        """Sets the recipe from a file"""
        resdict = {}
        # Open file
        with open(recipe_file) as f:
            # Get all lines inside
            lines = f.readlines()
            for line in lines:
                # Split the entry from the variable
                lsplit = [ll.strip() for ll in line.split('=')]
                # Check if entry is in the default, in which case cast the variable into default recipe type
                casted = self._cast_recipe_key_val(lsplit[0], lsplit[1])
                resdict.update(casted)

        return resdict

    def _cast_recipe_key_val(self, recipe_key, recipe_val) -> dict:
        """Cast a key and val pair into the type defined in constants.DEFAULT_RECIPE.
        Raise ValueError if the field does not belong in the nanoscribe default recipe."""
        casted = {}
        # Check if the key is in the default recipe, in which case cast the variable type
        if self.check_recipe_field(recipe_key):
            # Getting the type of the default recipe field
            field_type = type(DEFAULT_RECIPE[recipe_key])
            # If the recipe field is bool, we need to handle the problem of converting str to bool
            if field_type == bool:
                casted[recipe_key] = self._strtobool(recipe_val)
            # Otherwise cast
            else:
                casted[recipe_key] = field_type(recipe_val)
        # Otherwise raise an error
        else:
            raise ValueError(f"{recipe_key} is not a valid Describe Recipe line")
        
        return casted

    def write_recipe(self, f: str) -> None:
        """Save the recipe as a file"""
        logger.debug(f"Writing recipe file: {f}")

        with open(f, 'w') as r:
            for key, val in self.recipe.items():
                r.write(f"{key} = {val} \n")

    def generate_gwl_code(self, tmp_recipe: Path,
                          describepath: Path = Path(nanodescript_config.get("paths", "describe")),
                          ) -> None:  # (str, str, str, str):
        """Generate the GWL code from the current recipe."""

        recipepath = tmp_recipe.resolve()

        # Check if the recipe path is a directory in which case it's an error
        if recipepath.is_dir():
            raise ValueError(f"Expected a filename, got a directory instead: {recipepath}")

        # Check the extension. Either it has to be a .recipe or no-extension
        ext = recipepath.suffix
        if ext == '':
            recipepath = recipepath.with_suffix('.recipe')
        elif ext != '.recipe':
            raise ValueError(f"'recipe_save_dir' expects '.recipe' or no file extension, got '{ext}' instead")
        #
        if recipepath.exists():
            logger.debug(f"Warning: The file {recipepath} already exists and will be overwritten.")

        # Bare name of the file
        stl_filename = Path(self.recipe["Model.FilePath"]).stem

        # String versions of paths for subprocess.
        recipestr = str(recipepath)
        describestr = str(describepath.resolve())

        self.write_recipe(recipestr)

        # Slicing Command to Run
        subp = f"\"{describestr}\" -p {recipestr}"
        # Logging if requested
        logger.debug(f"Running subprocess: {subp}")
        # Actual slicing
        _ = subprocess.run(subp)

        # We check that everything exists.
        output_jobgwl = recipepath.parent.joinpath(
            f"{recipepath.stem}_{DESCRIBE_OUTPUT_FOLDER_SUFFIX}/{stl_filename}_{DESCRIBE_OUTPUT_JOBGWL_SUFFIX}")
        output_datgwl = recipepath.parent.joinpath(
            f"{recipepath.stem}_{DESCRIBE_OUTPUT_FOLDER_SUFFIX}/{stl_filename}_{DESCRIBE_OUTPUT_DATGWL_SUFFIX}")
        output_recipe = recipepath.parent.joinpath(
            f"{recipepath.stem}_{DESCRIBE_OUTPUT_FOLDER_SUFFIX}/{stl_filename}_{DESCRIBE_OUTPUT_RECIPE_SUFFIX}")
        output_files = recipepath.parent.joinpath(
            f"{recipepath.stem}_{DESCRIBE_OUTPUT_FOLDER_SUFFIX}/{stl_filename}_{DESCRIBE_OUTPUT_FILES_SUFFIX}")

        # Perform checks that all expected output files have been created.
        checks = [(output_jobgwl.exists() & output_jobgwl.is_file()),
                  (output_datgwl.exists() & output_datgwl.is_file()),
                  (output_recipe.exists() & output_recipe.is_file()),
                  (output_files.exists() & output_files.is_dir()),
                  ]

        if not all(checks):
            raise RuntimeError("Unexpected behaviour from subprocess.run")

        self.out_files = output_files
        self.out_datgwl = output_datgwl
        self.out_jobgwl = output_jobgwl
        self.out_recipe = output_recipe

    def __eq__(self, other):
        return self.recipe == other.recipe
