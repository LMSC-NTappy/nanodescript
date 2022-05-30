from dataclasses import dataclass
from pathlib import Path

from gdstk import Cell

from nanodescript.cell_transformation import CellTransformation
from nanodescript.describe_recipe_handler import DescribeRecipe


@dataclass
class CellAssociation:
    cell: Cell = None
    transformation: CellTransformation = None
    stl_file: Path = None
    recipe: DescribeRecipe = None
    out_datgwl: Path = None
    out_jobgwl: Path = None
    out_recipe: Path = None
    out_files: Path = None
    include_file: Path = None