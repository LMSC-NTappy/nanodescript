from nanodescript.describe_gds_handler import NanoscribeGdsHandler

from nanodescript.nanoscribematcher import PrintZoneCellMatcher
from nanodescript.utils import find_stl_files, find_topcell

from pathlib import Path

LIB_DIR = r"..\tests\test_data\test_pattern.gds"

out_dir = r"..\tests\test_pattern"

def main():
    #Open a gds library, get the top cell
    gdsman = NanoscribeGdsHandler(library=LIB_DIR, tmp_recipe_dir=Path(out_dir))
    gdsman.assign_topcell(find_topcell(gdsman.library))

    # #Initialise a nanoscribe cell matcher and initialise gds handler with it
    cellmatcher = PrintZoneCellMatcher()
    gdsman.set_matcher(cellmatcher)

    #Find all instances of nanoscribe prints with their cells and transformations
    gdsman.find_nanoscribe_instances_and_transformations()
    gdsman.match_stl_files(stlpaths=find_stl_files(r"..\tests\test_data"))
    gdsman.add_stl_files_to_associations()

    gdsman.print_all_nanoscribe_cells()

    gdsman.process_all_cells()

    gdsman.set_origin()
    print(f"Origin of print: {gdsman.print_origin}")
    gdsman.create_print_job()
    gdsman.export_print_job()

if __name__ == "__main__":
    main()


