# This is either smart or very stupid, but this file serves as a hardcoded set of defaults for setting
# or resetting the configuration file of this project. It also provides some special functionality such as
# type definition whereas the configparser only provides strings.

#identifiers defaults
NANOSCRIBEPROPERTY = 'is_nanoscribe'
STLPROPERTY = 'stl_file_path'
DESCRIBE_DEFAULT_PATH = 'C:\\Program Files\\Nanoscribe\\DeScribe\\DeScribe.exe'

# Default installation path for describe
DESCRIBE_OUTPUT_FOLDER_SUFFIX = "output"
DESCRIBE_OUTPUT_DATGWL_SUFFIX = "data.gwl"
DESCRIBE_OUTPUT_JOBGWL_SUFFIX = "job.gwl"
DESCRIBE_OUTPUT_RECIPE_SUFFIX = "job.recipe"
DESCRIBE_OUTPUT_FILES_SUFFIX = "files"

#Default gds file configuration
TOPCELLNAME = "topcell"  # Name match should be only lowercase alphabetic
MATCHER_NAME = 'layermatcher'

#LAYER NUMBER and DATATYPE Matchers
LAYER_NUMBER = 66
DATATYPE_NUMBER = 0

#Default for print zone matcher
PRINTZONE_NAME = 'nanoscribe_print_zone'

# The default recipe contains all default configurations but no model
DEFAULT_RECIPE = {
    'Version': 1.3,
    'Model.Type': 'Mesh',
    'Model.FilePath': "",
    'Model.Transformation': '[M11:1 M12:0 M13:0 M14:0] '
                            '[M21:0 M22:1 M23:0 M24:0] '
                            '[M31:0 M32:0 M33:1 M34:0] '
                            '[M41:0 M42:0 M43:0 M44:1]',
    'Model.BoundingBox': 'Minimum:X:0 Y:0 Z:0 Maximum:X:0 Y:0 Z:0',
    'Model.Rotation': 'X:0 Y:0 Z:0 W:1',
    'Model.Scaling': 'X:1 Y:1 Z:1',
    'Model.Translation': 'X:0 Y:0 Z:0',
    'Slicing.Mode': 'Fixed',
    'Slicing.DistanceMax': 0.1,
    'Slicing.SimplificationTolerance': 0,
    'Slicing.FixSelfIntersections': True,
    'Filling.Mode': 'Solid',
    'Filling.SolidContourCount': 2,
    'Filling.SolidContourDistance': 0.1,
    'Filling.ConcaveCornerMode': 'Sharp',
    'Filling.HatchingDistance': 0.1,
    'Filling.HatchingAngle': 0,
    'Filling.HatchingAngleOffset': 30,
    'Splitting.Mode': 'None',
    'Splitting.BlockSize': 'X:100 Y:100 Z:10',
    'Splitting.BlockOffset': 'X:0 Y:0 Z:0',
    'Splitting.BlockShearAngle': 0,
    'Splitting.BlockOverlap': 0,
    'Splitting.LayerOverlap': 0,
    'Splitting.BlockWidth': 'X:100.00 Y:100.0 Z:10',
    'Splitting.BlockOrderMode': 'Meander',  # Lexical, Meander, Spiral
    'Splitting.AvoidFlyingBlocks': True,
    'Splitting.GroupBlocks': False,
    'Splitting.UseBacklashCorrection': True,
    'Output.ScanMode': 'Galvo',
    'Output.ZAxis': 'Piezo',
    'Output.Exposure': 'Variable',  # Variable means contour / Solid
    'Output.InvertZAxis': True,  # True for DiLL
    'Output.WritingDirection': 'Up',  # Up for DiLL
    'Output.HatchLineMode': 'Alternate',
    'Exposure.GalvoAcceleration': 1,
    'Exposure.FindInterfaceAt': 0.5,
    'Exposure.ShellLaserPower': 36,
    'Exposure.ShellScanSpeed': 20000,
    'Exposure.CoreLaserPower': 40,
    'Exposure.CoreScanSpeed': 20000}
