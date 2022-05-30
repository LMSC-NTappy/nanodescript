from abc import ABC, abstractmethod
from gdstk import Cell, Library


class NanoscribeMatcher(ABC):
    @abstractmethod
    def __str__(self) -> str:
        """gets called when using print)"""
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """gets called when using repr(NanoscribeMatcher) or using the interactive
        prompt (eg Jupyter notebook I presume)"""
        pass

    @abstractmethod
    def match_cell(self, gdscell: Cell) -> bool:
        """Matches an input gdsobject to a nanoscribe footprint"""

    @abstractmethod
    def setup(self, library: Library) -> None:
        """Perform setup operations after creation of the object"""


class LayerNumberMatcher(NanoscribeMatcher):
    def __init__(
            self,
            layer_num: int,
    ):
        """Initialise a Matcher that matches cells containing shapes .
        Warning: Untested.
        """
        self.layer_num = layer_num

    def __str__(self) -> str:
        return f"LayerNumberMatcher matching layer {self.layer_num}"

    def __repr__(self) -> str:
        return f"LayerNumberMatcher matching layer {self.layer_num}"

    def setup(self, library: Library) -> None:
        """Raise an error if no shape from the library can be found with the layer number"""
        found = False

        for cell in Library.cells:
            if self.match_cell(cell):
                found = True

        if not found:
            raise ValueError(f"No cell in {Library.name} gds contains a layer with number: {self.layer_num}")

    def match_cell(self, gdscell: Cell) -> bool:
        """Check whether a gds cell matches with a nanoscribe print area.
        Return True if the input cell contains the reference nanoscribe cell
        in its dependencies, return False otherwise.
        """

        # Return True at the first matching object in the Cell.
        for poly in gdscell.polygons + gdscell.paths + gdscell.labels:
            if poly.layer == self.layer_num:
                return True

        # Else return False
        return False


class LayerNumberDatatypeMatcher(NanoscribeMatcher):
    def __init__(
            self,
            layer_num: int,
            datatype: int = 0,
    ):
        """Initialise a Matcher that matches nanoscribe gds shapes by layer number.
        Warning: Untested.
        """
        self.layer_num = layer_num
        self.datatype = datatype

    def __str__(self) -> str:
        return f"LayerNumberDatatypeMatcher matching layer {self.layer_num}/{self.datatype}"

    def __repr__(self) -> str:
        return f"LayerNumberDatatypeMatcher matching layer {self.layer_num}/{self.datatype}"

    def setup(self, library: Library) -> None:
        """Raise an error if no shape from the library can be found with the layer number"""
        found = False

        for cell in Library.cells:
            if self.match_cell(cell):
                found = True

        if not found:
            raise ValueError(f"No cell in {Library.name} gds contains a layer with number: {self.layer_num}")

    def match_cell(self, gdscell: Cell) -> bool:
        """Check whether a gds cell matches with a nanoscribe print area.
        Return True if the input cell contains the reference nanoscribe cell
        in its dependencies, return False otherwise.
        """

        # Return True at the first matching object in the Cell.
        for poly in gdscell.polygons + gdscell.paths + gdscell.labels:
            if poly.layer == self.layer_num:
                return True

        # Else return False
        return False


class PrintZoneCellMatcher(NanoscribeMatcher):
    def __init__(
            self,
            nanoscribe_cell: Cell = None,
            nanoscribe_cellname: str = "nanoscribe_print_zone",
    ):
        """Initialise a Matcher that matches nanoscribe print areas as those
            containing a direct reference (non-recursive) to a specific cell"""
        self._nanoscribe_cell = nanoscribe_cell
        self.nanocellname = nanoscribe_cellname

    def __str__(self) -> str:
        return f"PrintZoneCellMatcher matching references of {self._nanoscribe_cell.name}"

    def __repr__(self) -> str:
        return f"PrintZoneCellMatcher matching references of {self._nanoscribe_cell.name}"

    def setup(self, library: Library) -> None:
        """Setup the matcher from the library given in argument. Will look for a
        cell with the appropriate name in the library and set it as matching nanoscribe cell."""

        cellnames = [c.name for c in library.cells]

        # Raise an error for empty libraries
        if len(cellnames) == 0:
            raise ValueError(f"""Empty gds library: {library}""")

        # Look for cells with the correct name in the
        try:
            idx = cellnames.index(self.nanocellname)
            self._nanoscribe_cell = library.cells[idx]
        except ValueError:
            raise ValueError(f"""No cell named {self.nanocellname} found in
                                    library. Try setting cell property manually.""")

    def match_cell(self, gdscell: Cell) -> bool:
        """Check whether a gds cell matches with a nanoscribe print area.
        Return True if the input cell contains the reference nanoscribe cell
        in its dependencies, return False otherwise."""

        # It does not make problem if a cell tries to match itself, which is good.
        return self._nanoscribe_cell in gdscell.dependencies(False)
