TOPCELLNAME = "topcell"  # Name match should be only lowercase alphabetic
NANOSCRIBEPROPERTY = 'is_nanoscribe'
STLPROPERTY = 'stl_file_path'

COMMENT_CHAR = '%'

# Default installation path for describe
DESCRIBE_TMP_RECIPE_SUFFIX = "tmp.recipe"
DESCRIBE_DEFAULT_PATH = 'C:\\Program Files\\Nanoscribe\\DeScribe\\DeScribe.exe'
DESCRIBE_OUTPUT_SUFFIX = "output"
DESCRIBE_OUTPUT_DATGWL_SUFFIX = "_data.gwl"
DESCRIBE_OUTPUT_JOBGWL_SUFFIX = "_job.gwl"
DESCRIBE_OUTPUT_RECIPE_SUFFIX = "_job.recipe"
DESCRIBE_OUTPUT_FILES_SUFFIX = "_files"

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
