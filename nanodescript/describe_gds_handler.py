from pathlib import Path, PurePath
from copy import deepcopy
from typing import Union

import logging

import numpy as np
from gdstk import Library, read_gds, Cell
from tqdm import tqdm

from nanodescript.config import nanodescript_config
from nanodescript.nanoscribe_matchers import get_matcher_by_name, NanoscribeMatcher
from nanodescript.cell_transformation import CellTransformation
from nanodescript.cell_association import CellAssociation
from nanodescript.describe_gwl_handler import GwlHandler
from nanodescript.describe_recipe_handler import DescribeRecipe
import nanodescript.describe_commands as cmds
from nanodescript.utils import find_stl_files

logger = logging.getLogger(__name__)


class NanoscribeGdsHandler:
    """Class to handle gds files using Nanoscribe."""

    def __init__(
            self,
            library: Union[Library, str, Path],
            out_dir: Path,
            matcher: NanoscribeMatcher = get_matcher_by_name(nanodescript_config.get('gds_handler','matcher')),
            describerecipe: DescribeRecipe = DescribeRecipe(),
            describepath: Path = Path(nanodescript_config.get('paths', 'describe')),
    ) -> None:
        """Initialise a gds manager object"""

        # Just try if it evaluates as str
        if issubclass(type(library), PurePath):
            self.open_library_from_file(str(library.resolve()))
        elif isinstance(library, str):
            self.open_library_from_file(library)
        else:
            self.library = library

        # Initialise handlers
        self.gwlhandler = GwlHandler()
        self.describerecipe = describerecipe

        # Setting up the matcher
        self.matcher = matcher
        self.matcher.setup(self.library)

        # Associations
        self.nanoscribe_cells_associations: list[CellAssociation] = []
        self.recipes = []

        # Output directory
        if out_dir.exists() and not out_dir.is_dir():
            raise ValueError(f"Expecting a directory for out_dir. Received {out_dir}")
        else:
            out_dir.mkdir(parents=True, exist_ok=True)
            self.out_dir = out_dir

        # Production variables
        self.topcell = None
        self.print_origin = None

        # Describe.exe file for subprocess slicing
        self.describepath = describepath

    def set_matcher(self, matcher: NanoscribeMatcher) -> None:
        """Set a new matcher in the gds handler"""
        self.matcher = matcher
        self.matcher.setup(self.library)

    def open_library_from_file(self, file: str) -> None:
        """Set the library from a file"""
        self.library = read_gds(file)

    def assign_topcell(self, cell: Cell) -> None:
        """Assign top-cell role to the input cell"""
        # Make sure we can find the cell object we want in the library attribute
        try:
            idx = self.library.cells.index(cell)
        except ValueError:
            raise ValueError(f"""Cell object {cell} not found in gds library: {self.library}.""")
        # Attribute it the topcell property
        self.topcell = self.library.cells[idx]

    def find_nanoscribe_cells(self) -> None:
        """Sets isnanoscribe property to all cells in the library"""
        cells = self.library.cells
        for cell in cells:
            if self.matcher.match_cell(cell):
                cell.set_property(nanodescript_config.get('identifiers', 'is_nanoscribe'), True)
            else:
                cell.set_property(nanodescript_config.get('identifiers', 'is_nanoscribe'), False)

    def set_nanoscribe_cell(self, cell: Cell, isnanoscribe: bool):
        """Set the property of a cell as nanoscribe"""
        if cell in self.library.cells:
            cell.set_property(nanodescript_config.get('identifiers', 'is_nanoscribe'), isnanoscribe)
        else:
            raise AttributeError(f'cell {cell}: {cell.name} not in library {self.library}: {self.library.name}')

    def reset_nanoscribe_cells(self) -> None:
        """Set all cells as non-nanoscribe"""
        for cell in self.library.cells:
            cell.set_property(nanodescript_config.get('identifiers', 'is_nanoscribe'), False)

    def get_nanoscribe_cells(self) -> list[Cell]:
        """Return all the nanoscribe cells in the library"""
        ns_cells = []

        is_set = [c.get_property(nanodescript_config.get('identifiers', 'is_nanoscribe'))
                  is not None for c in self.library.cells]

        # First check if the cells are actually nanoscribe
        if not all(is_set):
            raise RuntimeError(f'Library {self.library.name} contains cells where the property '
                               f'{nanodescript_config.get("identifiers", "is_nanoscribe")} associated '
                               f'with nanoscribe cells is not set.')

        # Then, output a list of all cells evaluating Nanoscribe as true.
        for cell in self.library.cells:
            if cell.get_property(nanodescript_config.get('identifiers', 'is_nanoscribe'))[0]:
                    ns_cells.append(cell)
        return ns_cells

    def match_stl_files(self, stlpaths: list[Path] = None) -> None:
        """Test if a list of paths towards stl files contains a match for a cell. If no list of paths towards .stl files
        is given as args, will look recursively for stl files in the current directory."""

        # Check if the nanoscribe property is set in the cells
        if self.library.cells[0].get_property(nanodescript_config.get('identifiers', 'is_nanoscribe')) is None:
                raise ValueError('Nanoscribe property not set in the library. Try running find_nanoscribe_cells() first')

        # If no paths passed in argument try to find them
        if stlpaths is None:
            stlpaths = find_stl_files(workpaths=Path('.'))

        names = [path.stem for path in stlpaths]

        # Set cells properties to associate with stuff
        for cell in self.library.cells:
            if cell.get_property(nanodescript_config.get('identifiers', 'is_nanoscribe')) == [1]:
                try:
                    idx = names.index(cell.name)
                    cell.set_property(nanodescript_config.get('identifiers', 'stl_file_path'), str(stlpaths[idx].resolve()))
                except ValueError:
                    cell.set_property(nanodescript_config.get('identifiers', 'stl_file_path'), 'STL_NOT_FOUND')
            else:
                cell.set_property(nanodescript_config.get('identifiers', 'stl_file_path'), 'NOT_NANOSCRIBE')

    def get_cells_matched_with_stl_files(self) -> list[tuple]:
        nsc_stl_matches = []
        for cell in self.library.cells:
            prop = cell.get_property(nanodescript_config.get('identifiers', 'stl_file_path'))
            if prop is not None:
                prop = prop[0].decode()
                if prop not in ['STL_NOT_FOUND', 'NOT_NANOSCRIBE']:
                    nsc_stl_matches.append((cell, Path(prop)))
        return nsc_stl_matches

    def find_nanoscribe_instances_and_transformations(self) -> None:
        """Find all nanoscribe cells in a library with transformations"""

        self.find_nanoscribe_cells()

        # Initialisation of the cells and transformations queue
        queue_of_cells = [self.topcell]
        queue_of_transformations = [CellTransformation()]

        # Initialisation of the results lists
        nanoscribe_asso = []
        # Recursion: we proceed as long as the queues are not empty
        while queue_of_cells:
            # FIFO queue popping
            current_cell = queue_of_cells.pop(0)
            current_transformation = queue_of_transformations.pop(0)

            # Check if queued cell is a nanoscribe cell
            current_prop = current_cell.get_property(nanodescript_config.get('identifiers', 'is_nanoscribe'))
            if current_prop is not None and current_prop[0]:
                # Append it to the ones that need printing
                asso = CellAssociation(current_cell, current_transformation)
                nanoscribe_asso.append(asso)
            else:
                # Get all children in the cell
                children = current_cell.references
                repetitions = []
                for child in children:
                    repetitions += child.apply_repetition()
                children += repetitions

                queue_of_cells += [ref.cell for ref in children]
                # Append the cascading transformations to the cell
                queue_of_transformations += [
                    current_transformation.compose_transformations(CellTransformation(reference=ref)) for ref in
                    children]

        if nanoscribe_asso:
            self.nanoscribe_cells_associations = nanoscribe_asso
        else:
            raise ValueError(f"No nanoscribe print areas found in library {self.library}")

    def add_stl_files_to_associations(self):
        """Process the cells with"""
        for asso in self.nanoscribe_cells_associations:
            stl = asso.cell.get_property(nanodescript_config.get('identifiers', 'stl_file_path'))[0].decode()
            if stl not in ['STL_NOT_FOUND', 'NOT_NANOSCRIBE']:
                asso.stl_file = Path(stl)

    def process_all_cells(self, ) -> None:
        """Process nanoscribe cells with a recipe"""

        for asso in tqdm(self.nanoscribe_cells_associations):
            self.process_cell(asso)

    def process_cell(self, cell_association: CellAssociation) -> None:
        """Process A nanoscribe cell using the current recipe. """

        self.describerecipe.process_stl(cell_association.stl_file, cell_association.transformation)

        if self.describerecipe not in self.recipes:
            self.recipes.append(deepcopy(self.describerecipe))
            cell_recipe = self.recipes[-1]
            iterator = len(self.recipes)
            # A directory is generated for the recipe. A bit useless to generate so many of them
            # But that's the only way I have found...
            recipe_dir = self.out_dir.joinpath(f"{iterator}_{cell_association.stl_file.stem}\\")
            recipe_dir.mkdir(exist_ok=True)
            recipe_file = recipe_dir.joinpath(f"{iterator}_{cell_association.stl_file.stem}")
            cell_recipe.generate_gwl_code(tmp_recipe=recipe_file, describepath=self.describepath)
        else:
            idx = self.recipes.index(self.describerecipe)
            cell_recipe = self.recipes[idx]

        cell_association.recipe = cell_recipe
        cell_association.include_file = cell_recipe.out_datgwl

    def get_bounding_box(self) -> (float, float, float, float):
        """Get the gds bounding box of the library and transformations"""
        xmin = np.inf
        xmax = -np.inf
        ymin = np.inf
        ymax = -np.inf
        for asso in self.nanoscribe_cells_associations:
            x = asso.transformation.origin[0]
            y = asso.transformation.origin[1]
            if x < xmin:
                xmin = x
            if x > xmax:
                xmax = x
            if y < ymin:
                ymin = y
            if y > ymax:
                ymax = y
        return np.array((xmin, ymin)), np.array((xmax, ymax))

    def set_origin(self, x0: float = None, y0: float = None):
        """Set the origin of the print path"""
        if x0 is None or y0 is None:
            minpos, _ = self.get_bounding_box()
            x0 = minpos[0]
            y0 = minpos[1]
        self.print_origin = np.array((x0, y0))

    def create_print_job(self) -> None:
        """Create the print job"""
        self.gwlhandler.add_header()
        self.gwlhandler.add_system_initialisation(self.describerecipe)
        self.gwlhandler.add_command(cmds.Describe_empty())
        self.gwlhandler.add_writing_configuration(self.describerecipe)
        self.gwlhandler.add_command(cmds.Describe_empty())
        self.gwlhandler.add_writing_parameters(self.describerecipe)

        if self.print_origin is not None:
            current_pos = self.print_origin
        else:
            raise ValueError("Print Origin not set")

        for k, asso in enumerate(self.nanoscribe_cells_associations):
            printpos = np.array(asso.transformation.origin)
            move = printpos - current_pos
            self.gwlhandler.add_command(cmds.Describe_empty())
            self.gwlhandler.add_command(cmds.Comment(f'Nanoscribe Zone {k}: {asso.cell.name}'))
            self.gwlhandler.add_command(cmds.MoveStageX(val=move[0]))
            self.gwlhandler.add_command(cmds.MoveStageY(val=move[1]))
            # Include the output relative to the output directory
            if asso.include_file.is_relative_to(self.out_dir):
                include_file = asso.include_file.relative_to(self.out_dir)
            else:
                include_file = asso.include_file
                logger.warning(f"Using absolute import for file {asso.include_file}")

            self.gwlhandler.add_command(cmds.Describe_include(str(include_file)))
            current_pos = printpos

    def export_print_job(self, fname: str = None) -> None:
        """Export the main print job"""

        if fname is None:
            fname = f"{self.library.name}_job.gwl"

        export = self.out_dir.joinpath(fname)

        self.gwlhandler.write_file(str(export))

    def print_all_nanoscribe_cells(self, ) -> None:
        """Print all the nanoscribe cells found by the handler"""
        if not self.nanoscribe_cells_associations:
            raise ValueError("Nanoscribe cells list is empty")

        for cell_asso in self.nanoscribe_cells_associations:
            print(f"Nanoscribe Cell {cell_asso.cell.name} with transformation: {cell_asso.transformation}")
