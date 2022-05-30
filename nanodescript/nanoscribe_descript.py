import argparse
from pathlib import Path
import logging
import sys

from nanodescript.describe_gds_handler import NanoscribeGdsHandler
from nanodescript.nanoscribematcher import PrintZoneCellMatcher
from nanodescript.utils import find_stl_files, find_topcell, find_cell_by_name

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))


def main():
    parser = argparse.ArgumentParser(prog='nanoscribe_descript',
                                     description='Nanoscribe code generation from gds libraries and stl files',
                                     epilog='This command line interface only provides basic functionality. Check '
                                            'documentation and contact author for more information.')

    parser.add_argument("gds",
                        nargs=1,
                        type=Path,
                        help='gds library file to process')

    parser.add_argument("out_dir",
                        nargs=1,
                        type=Path,
                        help='directory for output files')

    parser.add_argument("--describe_dir",
                        nargs=1,
                        type=Path,
                        default=None,
                        help='Installation directory for Describe',)

    parser.add_argument("--stl", "-s",
                        nargs="*",
                        type=Path,
                        action='store',
                        default=None,
                        help='Use this option to add Paths where stl files are searched. By default, stl files are'
                             'searched in the gds file directory and sub-directories. \n',
                        )

    parser.add_argument('--nonrecursive', '-nr',
                        action='store_true',
                        help="Use this flag to disable searching stl files in sub directories as well.\n",
                        )

    parser.add_argument('--topcell', '-t',
                        nargs='?',
                        help='Manually set the topcell. By default, automatic identification is attempted.\n',
                        default=None)

    parser.add_argument('--verbose', '-v',
                        action='count',
                        help='Use this flag for verbose operation, use -vv for very verbose operation (debug).\n',
                        default=0)

    parser.add_argument('--origin', '-o',
                        nargs=2,
                        type=float,
                        default=[0.0, 0.0],
                        help="Use this option to shift the print pattern origin by the specified amounts in X "
                             "and Y in um. EG, if -o 30.0 50.0 is used, the X=30.0 Y=50.0 um point of the gds pattern "
                             "will be used as the nanoscribe X=0.0, Y=0.0 position.\n")

    parser.add_argument('--recipe', '-r',
                        nargs=1,
                        type=Path,
                        default=None,
                        help='Use this option to change the base recipe used in slicing stl files.'
                        )

    # parse the arguments from standard input
    args = parser.parse_args()

    if args.verbose == 0:
        logger.setLevel(level=logging.WARNING)
    if args.verbose == 1:
        logger.setLevel(level=logging.INFO)
    if args.verbose >= 2:
        logger.setLevel(level=logging.DEBUG)

    logger.info("Initialising Nanoscribe Descript Session")
    logger.info("----------------------------------------")
    logger.info(f"GDS Library: {args.gds[0]}")
    logger.debug(f"resolved path: {args.gds[0].resolve()}")
    logger.info(f"Output  dir: {args.out_dir[0]}")
    logger.debug(f"resolved path: {args.out_dir[0].resolve()}")
    logger.info("----------------------------------------")

    # Initialise gds handler
    gdsman = NanoscribeGdsHandler(library=args.gds[0], out_dir=args.out_dir[0])

    #Update the path to describe.exe if needed
    if args.describe_dir is not None:
        gdsman.describepath = args.describe_dir

    logger.debug(f"Describe executable directory: {gdsman.describepath.resolve()}")

    #Update the slicing recipe if needed
    if args.

    # get the top cell and assign responsibility
    if args.topcell is None:
        logger.debug('Attempting to discover topcell in library')
        topcell = find_topcell(gdsman.library)
    else:
        # logging.info(f'Set topcell to: {args.topcell}')
        topcell = find_cell_by_name(gdsman.library, args.topcell[0])
        # logging.debug(f'cell address: {topcell}')

    logging.info(f'topcell set to: {topcell.name}')
    logging.debug(f"cell address: {topcell}")

    gdsman.assign_topcell(topcell)

    # Initialise a nanoscribe cell matcher
    cellmatcher = PrintZoneCellMatcher()
    gdsman.set_matcher(cellmatcher)
    logging.info(f'Matcher set to: {cellmatcher}')
    logger.info("----------------------------------------")

    # Perform Cell matching
    gdsman.find_nanoscribe_cells()
    # If requested, log matching results
    if logger.getEffectiveLevel() < 20:
        cells_found = gdsman.get_nanoscribe_cells()
        for c in cells_found:
            logging.debug(f"Nanoscribe Cell: {c}")

    # Searching for stl files
    if args.stl is None:
        args.stl = [args.gds[0].parent]
    logger.info(f"stl files searched in: {args.stl}")
    logger.info(f"stl files recursive: {not args.nonrecursive}")

    recursive = not args.nonrecursive
    stls = find_stl_files(args.stl, recursive=recursive)
    logger.info(f'stl files found: {stls}')

    # Perform stl matching
    gdsman.match_stl_files(stlpaths=stls)
    # If requested, log results
    if logger.getEffectiveLevel() < 20:
        logging.debug('STL Matches:')
        stl_cell_match = gdsman.get_cells_matched_with_stl_files()
        for sc in stl_cell_match:
            logging.debug(f"Stl match: cell {sc[0].name} - {sc[1]}")

    # Find all instances of nanoscribe prints with their cells and transformations
    gdsman.find_nanoscribe_instances_and_transformations()
    gdsman.add_stl_files_to_associations()
    # Log if requested
    if logger.getEffectiveLevel() < 20:
        logging.debug('Nanoscribe print zones:')
        for cell_asso in gdsman.nanoscribe_cells_associations:
            logging.debug(f"{cell_asso.cell.name} at: {cell_asso.transformation}")

    # Process all cells but output only
    logger.info('Processing cells starts ---------------------------------------')
    gdsman.process_all_cells()

    gdsman.set_origin(args.origin[0], args.origin[1])
    logger.info(f"Origin of print: {gdsman.print_origin}")
    gdsman.create_print_job()
    gdsman.export_print_job()

if __name__ == "__main__":
    main()