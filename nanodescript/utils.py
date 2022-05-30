import re
from pathlib import Path, PurePath
from typing import Union

from gdstk import Library, Cell

from nanodescript.constants import TOPCELLNAME

def find_stl_files(workpaths: Union[Path,list[Path]] = '.', recursive: bool = True) -> list[Path]:
    """find all stl files in a directory (recursively)"""

    if isinstance(workpaths, PurePath):
        workpaths = [workpaths]

    allexist = [wp.exists() for wp in workpaths]
    alldir = [wp.is_dir() for wp in workpaths]

    if not all(allexist) or not all(alldir):
        raise ValueError(f"{workpaths} does not exist or is not a directory.")

    foundpath = []
    if recursive:
        for wp in workpaths:
            foundpath.extend(wp.rglob('*.stl'))
    else:
        for wp in workpaths:
            foundpath.extend(wp.glob('*.stl'))

    return list(foundpath)

def find_cell_by_name(library: Library, name: str) -> Union[Cell,bool]:
    """Find a cell with the input name in the input library.
    If a cell is found, the cell object is returned.
    If no cell is found, ValueError is raised.
    """
    names = [cell.name for cell in library.cells]
    try:
        idx = names.index(name)
    except ValueError:
        raise ValueError(f"""No cell named {name} not found in gds library: {library}.""")

    return library.cells[idx]

def find_topcell(library: Library) -> Cell:
    """Find the topcell using name matching. If only one cell is found at
    the top level, it will be regarded as top cell no matter its name """

    toplvl = library.top_level()
    # No ambiguity -> Only cell is topcell
    if len(toplvl) == 1:
        idx = 0
    # With ambiguity: try to match name
    elif len(toplvl) > 1:
        topcell_match_pattern = re.compile(r'[\W_0-9]+')  # expression for all characters that are not alphabetic

        stdnames = [cell.name for cell in toplvl]
        stdnames = [topcell_match_pattern.sub('', name) for name in
                    stdnames]  # substitute empty str for all matches
        stdnames = [name.lower() for name in stdnames]  # convert remaining
        try:
            idx = stdnames.index(TOPCELLNAME)
        except ValueError:
            # No value is found
            raise ValueError(f"""No topcell found in top level cells:
                                 {[cell.name for cell in toplvl]}.""")
    # 0-length cells list
    else:
        raise ValueError('gds library is empty')

    # Finally, return topcell
    return toplvl[idx]