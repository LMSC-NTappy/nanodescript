from abc import ABC
import re
from typing import Union
import warnings

from nanodescript.constants import COMMENT_CHAR

# Abstract Base Class for Nanoscribe commands
class DescribeCommand(ABC):
    """Factory that initializes the correct Describe Command from a string. The factory doesn't maintain any of the
    instances it creates."""

    def __str__(self) -> str:
        """Universal str representation of nanoscribe commands. Works so far but dangerous for more than 1 arg"""
        valstr = " ".join([str(v) for v in self.__dict__.values()])
        return f"{self.__class__.__name__} {valstr}"

    def parse(self, valstr: str) -> None:
        """Default method to let a command cast a value into its argument. Seems stupid but The idea is that it might be
        overloaded as per necessity in daughter classes"""
        # The idea: for each (key,val) in the dictionary of all object attributes we cast the input string in the value
        # of the needed type. Probably a bad idea because it will fail if the dict is len>1 but let's see if practically
        # it poses problems at some point. Especially, if we need to support complex commands.

        # Here we get all the attributes [k1,k2,...] and their values [v1,v2,...] from an object.
        for k, v in self.__dict__.items():
            # We set the k-th attribute of the current object to the input value, casted into the type of current value.
            # Note how this will stupidly fail for bool
            setattr(self, k, type(v)(valstr))


# If the Command is unknown:
class UnknownDescribeCommand(DescribeCommand):
    """All commands that are not understood or non-supported by the software. Handled as a simple string."""

    def __init__(self, strcmd: str = '\n') -> None:
        self.strcmd = strcmd

    def __str__(self) -> str:
        return self.strcmd


# Writing mode parameters
class PiezoScanMode(DescribeCommand):
    """PiezoScanMode is a 0-argument describe command.
    In PiezoScanMode all coordinates are addressed through piezo movement in x-, y- and z-directions. In this mode, all
    coordinates are relative to the current position of the stage with the origin at the corner of the piezo. Upon
    switching to this mode, the galvo will move to (0,0).
    """

    def __init__(self) -> None:
        pass


class StageScanMode(DescribeCommand):
    """StageScanMode is a 0-argument describe command.
    WARNING Apparently this is deprecated and should not be used
    """

    def __init__(self) -> None:
        pass


class GalvoScanMode(DescribeCommand):
    """GalvoScanMode is a 0-argument describe command.
    In GalvoScanMode all coordinates are relative to the current positions of the stage and the piezo. In this mode the
    x- and y-coordinates are addressed by the galvo scan head whereas the z-coordinate is still addressed asynchronously
    with the piezo using layer-by-layer printing. Upon switching to GalvoScanMode the piezo position will be set to
    (0,0,0)."""

    def __init__(self) -> None:
        pass


class PulsedMode(DescribeCommand):
    """PulsedMode is a 0-argument describe command.
    In this mode each programmed point is addressed individually. Laser exposure is paused between each point, with
    the delay time defined by SettlingTime. The exposure time for each point is defined with ExposureTime."""

    def __init__(self) -> None:
        pass


class ContinuousMode(DescribeCommand):
    """ContinuousMode is a 0-argument describe command.
    In this mode programmed line segments are exposed continuously. Laser exposure is paused after each Write command.
    The printing speed is set with ScanSpeed. """

    def __init__(self) -> None:
        pass


class LogMode(DescribeCommand):
    """LogMode is a 0-argument describe command.
    This piezo printing mode is equivalent to ContinuousMode. Additionally to the ContinuousMode, one log file per line
    segment (after each Write command) is created consisting of the following 8 columns:
    """

    def __init__(self) -> None:
        pass


class ConnectPointsOn(DescribeCommand):
    """ConnectPointsOn is a 0-argument describe command.
    ConnectPointsOn interpolates additional points between the programmed coordinates in a linear fashion. The distance
    of the interpolated points is specified with PointDistance. These points are then sent to the piezo with the given
    UpdateRate."""

    def __init__(self) -> None:
        pass


class ConnectPointsOff(DescribeCommand):
    """ConnectPointsOff is a 0-argument describe command. For ConnectPointsOff no interpolation between the programmed
    coordinates is carried out. Therefore, only the coded points are addressed by the piezo.
    """

    def __init__(self) -> None:
        pass


# Writing/Printing Parameters
class PowerScaling(DescribeCommand):
    """Sets the factor for the power scale on which LaserPower operates. PowerScaling 1.0 is the default setting for
    which LaserPower 0-100 operates between 0 mW and the reference power at the objective aperture
    (20 mW for the Photonic Professional or 50 mW for the Photonic Professional GT). Laser powers higher than this can
    be reached by increasing PowerScaling. For example, to achieve 150% of the calibrated laser power you may use
    PowerScaling 1.5 and LaserPower 100 or PowerScaling 2 and LaserPower 75. The actual power setting is the product
    of PowerScaling multiplied by LaserPower."""

    def __init__(self, value: float = 1.0):
        self.value = value


class LaserPower(DescribeCommand):
    """Sets the laser power as a percentage of the current power scale. Unit %"""

    def __init__(self, value: float = 100.0):
        self.value = value


class PointDistance(DescribeCommand):
    """Sets the distance between the interpolated points when ConnectPointsOn. This feature is applicable in
    PiezoScanMode during both ContinuousMode and PulsedMode, and in GalvoScanMode during PulsedMode only.
    The unit is nanometer. Values between 10-200 nm are useful. """

    def __init__(self, value: float = 100.0):
        self.value = value


class UpdateRate(DescribeCommand):
    """Sets the rate at which the programmed or interpolated coordinates are sent to the piezo. This command is only
    valid in PiezoScanMode and ConnectPointsOn. Unit: [Hz]"""

    def __init__(self, value: int = 1000):
        self.value = value


class ScanSpeed(DescribeCommand):
    """Sets the printing velocity in [µm/s]. This command applies for all ScanModes. UpdateRate and ScanSpeed are
    mutually dependent. Changing the UpdateRate changes the ScanSpeed accordingly, and vice versa."""

    def __init__(self, value: float = 10000.0):
        self.value = value


class ExposureTime(DescribeCommand):
    """Sets the exposure time in PulsedMode for each programmed or interpolated coordinate. Unit: [ms] """

    def __init__(self, value: float = 50.0):
        self.value = value


class SettlingTime(DescribeCommand):
    """Sets the wait time between two line segments (in ContinuousMode) or between two points (in PulsedMode). """

    def __init__(self, value: float = 1.0):
        self.value = value


class PiezoSettlingTime(DescribeCommand):
    """Sets the wait time between two line segments (in ContinuousMode) or between two points (in PulsedMode).
    PiezoSettlingTime defines the time NanoWrite waits between switching off the laser at the last print position and
    switching on the laser at the next position. If the SettlingTime is less than the time the piezo takes to travel
    between the two positions, the laser will be switched on too early. If the SettlingTime is greater, the piezo will
    rest at the destination. Settling times between 100-500 ms are recommended, depending on the distance between two
    lines or points."""

    def __init__(self, settlingtime: float = 100.):
        self.settlingtime = settlingtime

    # Overloading the str method seems superfluous here
    # def __str__(self):
    #     return f"PiezoSettlingTime {self.settlingtime}\n"


class GalvoSettlingTime(DescribeCommand):
    """Sets the wait time between two line segments (in ContinuousMode) or between two points (in PulsedMode).
    GalvoSettlingTime lessens the effect of oscillations attributed to galvo movement. Values between 1-3 ms are
    recommended. This command is only relevant in PulsedMode."""

    def __init__(self, settlingtime: float = 2.0):
        self.settlingtime = settlingtime


class LineStartMode(DescribeCommand):
    """Sets the waiting time prior to line (or point) exposure. LineStartMode 1 waits for the set SettlingTime prior to
    exposure. LineStartMode 2 does not wait for SettlingTime and exposure takes place immediately. This feature is not
    applicable for GalvoScanMode."""

    def __init__(self, value: int = 1):
        self.value = value


class LineNumber(DescribeCommand):
    """Sets the number of lines that are written for one programmed line. This command is useful to quickly program
    gratings or for increasing the line thickness by printing multiple adjacent lines. The distance is controlled
    with LineDistance. value [1, 2, ... n]"""

    def __init__(self, value: int = 1):
        self.value = value


class LineDistance(DescribeCommand):
    """Sets the pitch of the lines according to LineNumber. The unit is nanometer. Unit: [nm]"""

    def __init__(self, value: int = 100):
        self.value = value


class PolyLineMode(DescribeCommand):
    """Specifies the position of lines generated with LineNumber relative to the programmed vector. The distance is
    defined by a multiple of LineDistance.
    0. to one side of the programmed line (depends on print direction, see paragraph)
    1. to the other side of the programmed line
    2. on both sides (alternating) with the programmed line coordinates in the center; with even LineNumber values the
        programmed line itself will not be printed and lines either side of the programmed vector will be printed
    value [0, 1, 2]. Default value 2
    """

    def __init__(self, value: int = 2):
        self.value = value


class PowerValues(DescribeCommand):
    """PiezoScanMode is a 0-argument describe command.
    Determines whether the fourth column of the coordinates will be used for defining LaserPower."""

    def __init__(self) -> None:
        pass


class PowerValuesOn(DescribeCommand):
    """PiezoScanMode is a 0-argument describe command.
    Determines whether the fourth column of the coordinates will be used for defining LaserPower."""

    def __init__(self) -> None:
        pass


class PowerValuesOff(DescribeCommand):
    """PiezoScanMode is a 0-argument describe command.
    Determines whether the fourth column of the coordinates will be used for defining LaserPower."""

    def __init__(self) -> None:
        pass


class MeanderOn(DescribeCommand):
    """PiezoScanMode is a 0-argument describe command.
    MeanderOn uses alternating printing directions for lines added with LineNumber."""

    def __init__(self) -> None:
        pass


class MeanderOff(DescribeCommand):
    """MeanderOff is a 0-argument describe command.
    MeanderOff uses the same printing direction for lines added with LineNumber."""

    def __init__(self) -> None:
        pass


class Wait(DescribeCommand):
    """Waits for the specified time in seconds before the printing procedure continues. A corresponding message will
    be issued in the message log. """

    def __init__(self, value: int = 1):
        self.value = value


class Write(DescribeCommand):
    """Write is a 0-argument describe command.
    This command determines the end of a trajectory defined by a prior set of coordinates."""

    def __init__(self) -> None:
        pass


class GalvoAcceleration(DescribeCommand):
    """The maximum acceleration of galvo scanner. Value range: 0.1 – 10 [V/ms^2]
    Recommended values:
        63x objective: 1 - 2
        25x objective: 1 - 10
        10x objective: 1 - 10
    """

    def __init__(self, value: float = 1.0):
        self.value = value


# Positioning commands
# Scan Fields Offsets
class XOffset(DescribeCommand):
    """Sets an offset for all programmed x-coordinates. The offset is added to each x-coordinate for each programmed or
    interpolated point. This command is useful to shift the position of subsequent structures within a single print job.
    Unit: [µm]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val

    # Overloading the DescribeCommand str method seems superfluous here
    def __str__(self):
        return f"XOffset {self.val}\n"


class YOffset(DescribeCommand):
    """Sets an offset for all programmed y-coordinates. The offset is added to each y-coordinate for each programmed or
    interpolated point. This command is useful to shift the position of subsequent structures within a single print job.
    Unit: [µm]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val

    # Overloading the DescribeCommand str method seems superfluous here
    def __str__(self):
        return f"YOffset {self.val}\n"


class ZOffset(DescribeCommand):
    """Sets an offset for all programmed z-coordinates. The offset is added to each z-coordinate for each programmed or
    interpolated point. This command is useful to shift the position of subsequent structures within a single print job.
    Unit: [µm]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val

    # Overloading the DescribeCommand str method seems superfluous here
    def __str__(self):
        return f"ZOffset {self.val}\n"


class PiezoXOffset(DescribeCommand):
    """Sets a piezo offset for all programmed x|y|z-coordinates. The offset is added to each x|y|z-coordinate of each
    programmed point. This command is only applicable in PiezoScanMode. Unit [um]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class PiezoYOffset(DescribeCommand):
    """Sets a piezo offset for all programmed x|y|z-coordinates. The offset is added to each x|y|z-coordinate of each
    programmed point. This command is only applicable in PiezoScanMode. Unit [um]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class PiezoZOffset(DescribeCommand):
    """Sets a piezo offset for all programmed x|y|z-coordinates. The offset is added to each x|y|z-coordinate of each
    programmed point. This command is only applicable in PiezoScanMode. Unit [um]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class GalvoXOffset(DescribeCommand):
    """Sets a galvo offset for all programmed x|y|z-coordinates. The offset is added to each x|y|z-coordinate of each
    programmed point. This command is only applicable in GalvoScanMode. Unit [um]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class GalvoYOffset(DescribeCommand):
    """Sets a galvo offset for all programmed x|y|z-coordinates. The offset is added to each x|y|z-coordinate of each
    programmed point. This command is only applicable in GalvoScanMode. Unit [um]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class GalvoZOffset(DescribeCommand):
    """Sets a galvo offset for all programmed x|y|z-coordinates. The offset is added to each x|y|z-coordinate of each
    programmed point. This command is only applicable in GalvoScanMode. Unit [um]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class MoveStageX(DescribeCommand):
    """Performs a relative displacement of the x|y-axis. Unit [um]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class MoveStageY(DescribeCommand):
    """Performs a relative displacement of the x|y-axis. Unit [um]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class GotoX(DescribeCommand):
    """Positions the piezo or the stage at the specified x|y-coordinate, depending on the current ScanMode.
    For GalvoScanMode the position will always be addressed with the piezo. Unit [um]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class GotoY(DescribeCommand):
    """Positions the piezo or the stage at the specified x|y-coordinate, depending on the current ScanMode.
    For GalvoScanMode the position will always be addressed with the piezo. Unit [um]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class StageGotoX(DescribeCommand):
    """Positions the stage at the defined x|y-coordinate. This command ignores offsets and transformations."""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class StageGotoY(DescribeCommand):
    """Positions the stage at the defined x|y-coordinate. This command ignores offsets and transformations."""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class PiezoGotoX(DescribeCommand):
    """Positions the piezo at the defined x|y|z-coordinate. This command ignores offsets but takes possible
    transformations into account. Unit [um]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class PiezoGotoY(DescribeCommand):
    """Positions the piezo at the defined x|y|z-coordinate. This command ignores offsets but takes possible
    transformations into account. Unit [um]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class PiezoGotoZ(DescribeCommand):
    """Positions the piezo at the defined x|y|z-coordinate. This command ignores offsets but takes possible
    transformations into account. Unit [um]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class CenterStage(DescribeCommand):
    """0-argument describe command.
    Moves the stage to the center coordinates (x=0, y=0) of the current sample position."""

    def __init__(self) -> None:
        pass


class AddZDrivePosition(DescribeCommand):
    """Defines relative movements of the microscope z-drive from the current position; both positive and negative values
    are allowed. It is necessary to use this command for stitching together structures higher than 300 µm and can be
    used for layer-by-layer printing. If InvertZaxis = 1, positive values of AddZDrivePosition move the z-position away
    from the substrate. Unit [um]"""

    def __init__(self, val: float = 0.0, ):
        self.val = val


# PerfectShape parameters
class PerfectShape(DescribeCommand):
    """Sets the piezo PerfectShape mode.
    0. PerfectShapeOff
    1. PerfectShapeQuality
    2. PerfectShapeIntermediate
    3. PerfectShapeFast
    The above-mentioned commands (e.g. PerfectShapeOff) can be used directly instead of using PerfectShape 0|1|2|3."""

    def __init__(self, val: int = 2, ):
        self.val = val


class PerfectShapeOff(DescribeCommand):
    """0-argument describe command.
    Turns PerfectShape off for piezo modes. Conventional printing is recommended for straight lines and sharp corners.
    PerfectShape is always active for galvo mode.
    """

    def __init__(self) -> None:
        pass


class PerfectShapeQuality(DescribeCommand):
    """0-argument describe command.
    PerfectShapeQuality: the highest trajectory accuracy is achieved at comparatively low speed.
    PerfectShapeIntermediate: the . PerfectShapeFast: """

    def __init__(self) -> None:
        pass


class PerfectShapeIntermediate(DescribeCommand):
    """0-argument describe command.
    trajectory accuracy is lower but the structures are written faster compared to
    PerfectShapeQuality"""

    def __init__(self) -> None:
        pass


class PerfectShapeFast(DescribeCommand):
    """0-argument describe command.
    minimizes printing time by maximizing printing speed. The piezo trajectory
    is less accurate than for PerfectShapeQuality and PerfectShapeIntermediate."""

    def __init__(self) -> None:
        pass


class PsLoadPowerProfiles(DescribeCommand):
    """Loads a set of power profiles. Path to *.lp file It is recommended to copy the *.lp file in the same directory of
    the GWL print job. If no file name is specified, only the standard power profiles ('IP Resist' and 'None') are
    available.
    Honestly if you are using this command I assume you know better than me so it'll just cast the param to a string
    and you deal with the rest (Note from N.Tappy)"""

    def __init__(self, lp_file: str = 'IP Resist'):
        self.lp_file = lp_file


class PsPowerProfiles(DescribeCommand):
    """Selects a stored power profile.
    Apparently also a string, from what I read on the nanoguide I kinda expect it to be single-quoted. You make your
    test and I'd be happy to read about it. Cheers, NT
    """

    def __init__(self, lp: str = 'IP Resist'):
        self.lp = lp


class PsPowerSlope(DescribeCommand):
    """Sets the slope which is used for the laser power adaptation (aberration compensation). This is valid for
    GalvoScanMode and PerfectShape with PiezoScanMode. """

    def __init__(self, val: float = 1.0):
        self.val = val


class StageVelocity(DescribeCommand):
    """Defines the displacement velocity of the stage in [um/s]. Stage movements occur without laser exposure and the
    printing speed is defined separately with ScanSpeed."""

    def __init__(self, velocity: int = 200):
        self.velocity = velocity

    def __str__(self):
        return f"StageVelocity {self.velocity}\n"


# Loop statements and variables
class Describe_include(DescribeCommand):
    """Adds the code of another GWL file to the current GWL file at the current command line. If the file resides within
    the current directory no path needs to be given (include subroutine.gwl). Otherwise the path can either be relative
    (subroutines\filename.gwl) or absolute (D:\\gwls\\subroutines\filename.gwl).
    Spaces are allowed but the path must not be wrapped in quotation marks. Variables cannot be included."""

    def __init__(self, gwl_path: str = 'none'):
        self.gwl_path = gwl_path

    def __str__(self) -> str:
        return f"include {self.gwl_path}"

    def parse(self, gwl_path: str):
        gwl_path = gwl_path.strip(" '\"\t\n")

        if not gwl_path.endswith(".gwl") or gwl_path.endswith(".gwl"):
            raise ValueError(f"{gwl_path} is does not direct to a '.gwl' or '.gwlb' file")


class Describe_repeat(DescribeCommand):
    """Sets the number of repetitions for the next Include line only. To repeat several lines of code, place them within
    the included file or use a loop. The total number of executions is n+1, since the line following the command will
    itself be executed."""

    def __init__(self, value: int = 1):
        self.value = value

# Helper functions to ensure that var, local and set treat variable names similarily
def _check_var_name(varstring: str) -> None:
    """ raise an error if the variable name does not comply with describe rules."""
    if not varstring.startswith("$"):
        raise ValueError(f'string does not start with $ which is mandatory for describe variable names')
    describe_expression = re.compile("^(\w)+$")
    if not describe_expression.match(varstring[1:]):
        raise ValueError(
            f'{varstring} does not comply with describe name rules: only _ and alphanumeric characters.')


def _parse_var_value(valstr: str) -> Union[int, float, str]:
    """ Try parsing value into either an int or a float. Return a single-quote decorated string if it fails"""
    # This works because int(2) is ok, int(2.0) raise ValueError for example, and int (2.0E-6) too
    try:
        return int(valstr)
    except ValueError:
        pass
    try:
        return float(valstr)
    except ValueError:
        pass
    # Return a string if numbercasting has failed.
    return f"'{valstr}'"


def _parse_var_str(varstr: str) -> (str, Union[int, float, str]):
    """Parse a string into a var command"""

    # Separate str into name and value
    varstr = varstr.strip()
    spl = varstr.split('=')

    name = spl[0].strip()
    value = spl[1].strip()

    # Raise error if name doesn't match
    _check_var_name(name)

    # Raise error if value doesn't exist, otherwise parse it
    if not value:
        raise ValueError("No value found")
    else:
        value = _parse_var_value(value)

    return name, value


# In the following, some functions do not obey camelcase to stay as close to the
# Describe language as possible.
class Describe_var(DescribeCommand):
    """Defines a new variable with an initial value (required). This value may be an integer, a decimal number or
    another variable. In the case another variable is used, the value will be read but no persistent connection will
    remain between the variables. Variable names are case insensitive and may contain numbers and underscores."""

    def __init__(self, name: str = "$var", value: Union[int, float, str] = 0.0):
        _check_var_name(name)
        self.name = name
        self.value = value

    def __str__(self):
        return f"var {self.name} = {self.value}"

    def parse(self, string: str) -> None:
        n, v = _parse_var_str(string)
        self.name = n
        self.value = v


class Describe_local(DescribeCommand):
    """Defines a new local variable with an initial value. The usage is identical to var but the scope of the variable
    is limited to the current GWL file only."""

    def __init__(self, name: str = "$var", value: Union[int, float, str] = 0.0):
        _check_var_name(name)
        self.name = name
        self.value = value

    def __str__(self):
        return f"local {self.name} = {self.value}"

    def parse(self, string: str) -> None:
        n, v = _parse_var_str(string)
        self.name = n
        self.value = v


class Describe_set(DescribeCommand):
    """Updates the value of a previously defined variable. The same rules for valid values apply."""

    def __init__(self, name: str = "$var", value: Union[int, float, str] = 0.0):
        _check_var_name(name)
        self.name = name
        self.value = value

    def __str__(self):
        return f"set {self.name} = {self.value}"

    def parse(self, string: str) -> None:
        n, v = _parse_var_str(string)
        self.name = n
        self.value = v


class Describe_empty(DescribeCommand):
    """Adds an empty line to the recipe"""
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return ""

# if elif end statement will be basically treated as strings for the moment
class Describe_if(DescribeCommand):
    """Conditional jumps based on Boolean expressions. If the condition is true the block following the if keyword is
    executed, otherwise the block following the else keyword is executed. elif is short for "else if" and can be used
    to chain conditionals. Boolean expressions can be constructed using the comparison operators ==, !=, >, >=, <, <=,
    the unary operator not and the binary operators and, or. Boolean expressions can only be used within while loops
    and if-elif-end clauses. The result of a Boolean expression cannot be assigned to a variable."""

    def __init__(self, if_condition: str = "0 == 0"):
        self.if_condition = if_condition

    def __str__(self):
        return f"if {self.if_condition}"


class Describe_elif(DescribeCommand):
    """Conditional jumps based on Boolean expressions. If the condition is true the block following the if keyword is
    executed, otherwise the block following the else keyword is executed. elif is short for "else if" and can be used
    to chain conditionals. Boolean expressions can be constructed using the comparison operators ==, !=, >, >=, <, <=,
    the unary operator not and the binary operators and, or. Boolean expressions can only be used within while loops
    and if-elif-end clauses. The result of a Boolean expression cannot be assigned to a variable."""

    def __init__(self, elif_condition: str = "0 == 0"):
        self.elif_condition = elif_condition

    def __str__(self):
        return f"elif {self.elif_condition}"


class Describe_else(DescribeCommand):
    """0 argument command.
    Conditional jumps based on Boolean expressions. If the condition is true the block following the if keyword is
    executed, otherwise the block following the else keyword is executed. elif is short for "else if" and can be used
    to chain conditionals. Boolean expressions can be constructed using the comparison operators ==, !=, >, >=, <, <=,
    the unary operator not and the binary operators and, or. Boolean expressions can only be used within while loops
    and if-elif-end clauses. The result of a Boolean expression cannot be assigned to a variable."""

    def __init__(self):
        pass

    def __str__(self):
        return f"else"


class Describe_end(DescribeCommand):
    """0 argument command.
    Conditional jumps based on Boolean expressions. If the condition is true the block following the if keyword is
    executed, otherwise the block following the else keyword is executed. elif is short for "else if" and can be used
    to chain conditionals. Boolean expressions can be constructed using the comparison operators ==, !=, >, >=, <, <=,
    the unary operator not and the binary operators and, or. Boolean expressions can only be used within while loops
    and if-elif-end clauses. The result of a Boolean expression cannot be assigned to a variable."""

    def __init__(self):
        pass

    def __str__(self):
        return f"end"


class Describe_for(DescribeCommand):
    """Loop a command applied to a variable. The variable $a defines the start value of the loop counter $i. The
    variable $i will be incremented by $s until the maximum value $b is reached after each loop. Step is optional and
    has a default value of 1.0 if it is not defined. The starting value $a can be declared before the loop (e.g. local
    $a = 0) or within the loop (e.g. for $i=0 ...). The for loop must always be closed with end."""

    def __init__(self, for_condition: str = "$i = $a to $b step $s"):
        self.for_condition = for_condition

    def __str__(self):
        return f"for {self.for_condition}"


class Describe_while(DescribeCommand):
    """Similar to the for loop but using a Boolean expression for the loop condition. The loop cycles as long as the
    boolean expression returns true. To avoid infinite loops, the variables must be updated within the loop so that
    expression returns false at one point! Use while loops with care."""

    def __init__(self, bool_condition: str = "$i = $a to $b step $s"):
        self.bool_condition = bool_condition


class Describe_break(DescribeCommand):
    """0 argument command.
    Applicable in for and while loops. The break statement exits the loop immediately.
    """

    def __init__(self):
        pass

    def __str__(self):
        return f"break"


class Describe_continue(DescribeCommand):
    """0 argument command.
    Applicable in for and while loops. The continue statement continues with the next iteration of the loop by jumping
    to the evaluation of the loop condition.
    """

    def __init__(self):
        pass

    def __str__(self):
        return f"continue"


class AddScanSpeed(DescribeCommand):
    """sum the specified values with the current values of the command."""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class AddLaserPower(DescribeCommand):
    """sum the specified values with the current values of the command."""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class AddExposureTime(DescribeCommand):
    """sum the specified values with the current values of the command."""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class AddPowerScaling(DescribeCommand):
    """sum the specified values with the current values of the command."""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class AddLineNumber(DescribeCommand):
    """sum the specified values with the current values of the command."""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class AddLineDistance(DescribeCommand):
    """sum the specified values with the current values of the command."""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class AddXOffset(DescribeCommand):
    """sum the specified values with the current values of the command."""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class AddYOffset(DescribeCommand):
    """sum the specified values with the current values of the command."""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class AddZOffset(DescribeCommand):
    """sum the specified values with the current values of the command."""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class AddDefocus(DescribeCommand):
    """sum the specified values with the current values of the command."""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class AddUpdateRate(DescribeCommand):
    """sum the specified values with the current values of the command."""

    def __init__(self, val: float = 0.0, ):
        self.val = val


class AddPointDistance(DescribeCommand):
    """sum the specified values with the current values of the command."""

    def __init__(self, val: float = 0.0):
        self.val = val


class MultScanSpeed(DescribeCommand):
    """multiply the specified values with the current values of the command"""
    """sum the specified values with the current values of the command."""

    def __init__(self, val: float = 1.0):
        self.val = val


class MultLaserPower(DescribeCommand):
    """multiply the specified values with the current values of the command"""

    def __init__(self, val: float = 1.0):
        self.val = val


class MultExposureTime(DescribeCommand):
    """multiply the specified values with the current values of the command"""

    def __init__(self, val: float = 1.0):
        self.val = val


class MultPowerScaling(DescribeCommand):
    """multiply the specified values with the current values of the command"""

    def __init__(self, val: float = 1.0):
        self.val = val


class MultLineNumber(DescribeCommand):
    """multiply the specified values with the current values of the command"""

    def __init__(self, val: float = 1.0):
        self.val = val


class MultLineDistance(DescribeCommand):
    """multiply the specified values with the current values of the command"""

    def __init__(self, val: float = 1.0):
        self.val = val


class MultXOffset(DescribeCommand):
    """multiply the specified values with the current values of the command"""

    def __init__(self, val: float = 1.0):
        self.val = val


class MultYOffset(DescribeCommand):
    """multiply the specified values with the current values of the command"""

    def __init__(self, val: float = 1.0):
        self.val = val


class MultZOffset(DescribeCommand):
    """multiply the specified values with the current values of the command"""

    def __init__(self, val: float = 1.0):
        self.val = val


class MultDefocus(DescribeCommand):
    """multiply the specified values with the current values of the command"""

    def __init__(self, val: float = 1.0):
        self.val = val


class MultUpdateRate(DescribeCommand):
    """multiply the specified values with the current values of the command"""

    def __init__(self, val: float = 1.0):
        self.val = val


class MultPointDistance(DescribeCommand):
    """multiply the specified values with the current values of the command"""

    def __init__(self, val: float = 1.0):
        self.val = val


# Printing text


class WriteText(DescribeCommand):
    """Prints the string given within quotation marks. A line break can be introduced with \n.
    For details of string formatting refer to the Advanced GWL Programming article. WriteText has seperate settings for
    printing speed, laser power and uses a fixed PowerScaling of 1.0.
    """

    def __init__(self, text: str = ""):
        self.text = text

    def __str__(self) -> str:
        return f'WriteText "{self.text}"'


class TextPositionX(DescribeCommand):
    """Offsets the position of the first letter of the last line in the x|y|z-direction. Unit: µm"""

    def __init__(self, textoffset: float = 1.0):
        self.textoffset = textoffset


class TextPositionY(DescribeCommand):
    """Offsets the position of the first letter of the last line in the x|y|z-direction. Unit: µm"""

    def __init__(self, textoffset: float = 1.0):
        self.textoffset = textoffset


class TextPositionZ(DescribeCommand):
    """Offsets the position of the first letter of the last line in the x|y|z-direction. Unit: µm"""

    def __init__(self, textoffset: float = 1.0):
        self.textoffset = textoffset


class LineSpacingX(DescribeCommand):
    """Offsets lines in the x|y|z-direction each time a line break /n is invoked.
     The direction of the line break can be changed by using negative y-values for
     LineSpacingY. Unit: µm"""

    def __init__(self, linespacing: float = 10.0):
        self.linespacing = linespacing


class LineSpacingY(DescribeCommand):
    """Offsets lines in the x|y|z-direction each time a line break /n is invoked.
     The direction of the line break can be changed by using negative y-values for
     LineSpacingY. Unit: µm"""

    def __init__(self, linespacing: float = 10.0):
        self.linespacing = linespacing


class LineSpacingZ(DescribeCommand):
    """Offsets lines in the x|y|z-direction each time a line break /n is invoked.
     The direction of the line break can be changed by using negative y-values for
     LineSpacingY. Unit: µm"""

    def __init__(self, linespacing: float = 10.0):
        self.linespacing = linespacing


class TextLaserPower(DescribeCommand):
    """Laser power value that is used for printing text. It is independent from the
    general LaserPower. Unit %, value 0-100"""

    def __init__(self, laserpower: float = 100.0):
        self.laserpower = laserpower


class TextPointDistance(DescribeCommand):
    """Sets the distance between two interpolated points for printing text. Unit % default 50"""

    def __init__(self, pointdistance: float = 50.0):
        self.pointdistance = pointdistance


class TextScanSpeed(DescribeCommand):
    """Sets the speed for printing text. Unit [um/s] """

    def __init__(self, scanspeed: float = 10000.0):
        self.scanspeed = scanspeed


class TextFontSize(DescribeCommand):
    """Sets the size of the font used for the WriteText command.
    The size is given in micrometer and corresponds to the
    distance between baseline and cap height. unit [um]. Default 5
    """

    def __init__(self, fontsize: float = 10000.0):
        self.fontsize = fontsize


# Correction features
class DefocusFactor(DescribeCommand):
    """ Each z-coordinate is multiplied by this factor. The DefocusFactor compensates
    for shifts of the focus position in the z-direction according to the index mismatch
    between the immersion medium, the substrate and the 2PP resin."""

    def __init__(self, defocus: float = 1):
        self.defocus = defocus


class MeasureTilt(DescribeCommand):
    """Specifies the array size of the measurement for the sample tilt. MeasureTilt 5 measures
    the interface on a regular 5x5 array on the substrate, thus at 25 points throughout the
    maximum printing area. Hence, in PiezoScanMode the measurement area is 300 µm2."""

    def __init__(self, numpts: int = 5):
        self.numpts = numpts


class TiltCorrectionOn(DescribeCommand):
    """0 arguments command. TiltCorrectionOn activates tilt correction based on previously
    measured values acquired by MeasureTilt. The tilt correction compensates for substrate
    tilts by adapting the z-position individually for each x-y-coordinate. The angle of the
    z-axis will not be changed. TiltCorrectionOn should always follow a preceding MeasureTilt
    command to ensure a valid correction will be applied. Subsequently, a FindInterface command
    should always be executed. TiltCorrectionOff deactivates tilt correction.
    Note: The GalvoScanMode does not feature a tilt correction.
    """
    pass


class TiltCorrectionOff(DescribeCommand):
    """0 arguments command. TiltCorrectionOn activates tilt correction based on previously
    measured values acquired by MeasureTilt. The tilt correction compensates for substrate
    tilts by adapting the z-position individually for each x-y-coordinate. The angle of the
    z-axis will not be changed. TiltCorrectionOn should always follow a preceding MeasureTilt
    command to ensure a valid correction will be applied. Subsequently, a FindInterface command
    should always be executed. TiltCorrectionOff deactivates tilt correction.
    Note: The GalvoScanMode does not feature a tilt correction.
    """
    pass


class ManualTiltX(DescribeCommand):
    """ManualTiltX and ManualTiltY set values for the tilt correction along the x- and y-axis,
    respectively. Unit [degree]
    NOTE: The GalvoScanMode does not feature a tilt correction."""

    def __init__(self, tilt: float = 5.0):
        self.tilt = tilt


class ManualTiltY(DescribeCommand):
    """ManualTiltX and ManualTiltY set values for the tilt correction along the x- and y-axis,
    respectively. Unit [degree]
    NOTE: The GalvoScanMode does not feature a tilt correction."""

    def __init__(self, tilt: float = 5.0):
        self.tilt = tilt


class AccelerationTime(DescribeCommand):
    """Sets the time interval in which the laser power is adjusted
    at a line start (line ending for DecelerationTime) to account
    for the acceleration of the piezo. It is invalid for both PerfectShape
    and GalvoScanMode. unit [s]"""

    def __init__(self, time: float = 5.0):
        self.time = time


class DecelerationTime(DescribeCommand):
    """Sets the time interval in which the laser power is adjusted
    at a line start (line ending for DecelerationTime) to account
    for the acceleration of the piezo. It is invalid for both PerfectShape
    and GalvoScanMode. unit [s]"""

    def __init__(self, time: float = 5.0):
        self.time = time


class Acceleration(DescribeCommand):
    """Defines the shape of the laser power adjustment curve at the start or end of a line.
    It is invalid for both PerfectShape and GalvoScanMode.
    """

    def __init__(self, value: float = 5.0):
        self.value = value


class Deceleration(DescribeCommand):
    """Defines the shape of the laser power adjustment curve at the start or end of a line.
    It is invalid for both PerfectShape and GalvoScanMode.
    """

    def __init__(self, value: int = 5):
        self.value = value


# Autofocus parameters
class FindInterfaceAt(DescribeCommand):
    """Initiates autofocusing with the given value as the piezo z-coordinate.
    This value represents a hardware offset of the interface relative to the
    substrate. Coordinates below the interface may be accessed, ensuring that
    structures can be anchored securely to the substrate surface.
    After a successful search, NanoWrite displays: Interface found x@y. Value
    x is a measure for the interface signal amplitude and value y is inversely
    proportional to the exposure time of the autofocus camera on a scale between
    1 to 100. Thus, y=1 indicates maximum exposure time and y=100 indicates
    minimum exposure time. These two values are useful for selecting one interface
    if many happen to be present. Unit [um] default 0"""

    def __init__(self, value: int = 0.0):
        self.value = value


class InterfaceMax(DescribeCommand):
    """Sets a maximum value for the interface. Consider the message log of NanoWrite
    displaying Interface found x@y. InterfaceMax x.yyy suppresses all interfaces with
    greater amplitudes or with shorter exposure times (greater than yyy, expressed as
    a three-digit number). For example, InterfaceMax 100.002 suppresses all interfaces
    with an amplitude > 100 at an exposure time value > 2. Both InterfaceMax and InterfaceMin
    may be used, but only the most recent command will be used for interface finding.
    Unit: three-digit float."""

    def __init__(self, x_yyy: float = 0.0):
        self.x_yyy = x_yyy


class InterfaceMin(DescribeCommand):
    """Sets a maximum value for the interface. Consider the message log of NanoWrite
    displaying Interface found x@y. InterfaceMax x.yyy suppresses all interfaces with
    greater amplitudes or with shorter exposure times (greater than yyy, expressed as
    a three-digit number). For example, InterfaceMin 200.005 suppresses all interfaces
    with an amplitude < 200 at an exposure time value < 5. Both InterfaceMax and InterfaceMin
    may be used, but only the most recent command will be used for interface finding.
    Unit: three-digit float."""

    def __init__(self, x_yyy: float = 0.0):
        self.x_yyy = x_yyy


class ResetInterface(DescribeCommand):
    """0 argument Command. Erases InterfaceMax or InterfaceMin settings."""
    pass


class InterfacePosition(DescribeCommand):
    """ NanoWrite applies the Defocus Factor starting from the z-value given
    in the most recent FindInterfaceAt command. InterfacePosition overwrites
    this value so that the DefocusFactor can be used starting at any desired
    z-coordinate. This command does not influence the interface-finding routine.
    Unit [um]"""

    def __init__(self, value: float = 0.0):
        self.value = value


class InterfaceAccuracyHigh(DescribeCommand):
    """0 Argument command. Sets the accuracy of the interface finder. See nanoguide
    for more information."""
    pass


class InterfaceAccuracyDefault(DescribeCommand):
    """0 Argument command. Sets the accuracy of the interface finder. See nanoguide
    for more information."""
    pass


class InterfaceAccuracyLow(DescribeCommand):
    """0 Argument command. Sets the accuracy of the interface finder. See nanoguide
    for more information."""
    pass


# Initialization parameters
class SamplePosition(DescribeCommand):
    """Moves to the defined sample position. The objective is lowered, the stage
    moves to the selected sample center and an approach procedure is performed.
    This is different from double clicking a sample position. SamplePosition must
    match one of the valid sample positions on the selected sample holder."""

    def __init__(self, value: float = 0.0):
        self.value = value


class ChooseObjective(DescribeCommand):
    """After lowering the objective, the specified objective position is
    addressed by the motorized nosepiece of the microscope. The objective
    name is displayed in the message log of NanoWrite. Automated sample
    approach will not be executed to allow for a change of sample position.
    I guess the value is between 1 and 6"""

    def __init__(self, value: float = 1):
        self.value = value


class InvertZAxis(DescribeCommand):
    """Triggers inversion of the z-axis. To conserve a right-handed coordinate
    system the x-axis is inverted at the same time. Default Value 0.
    0. deactivates InvertZAxis
    1. activates InvertZAxis
    """

    def __init__(self, value: int = 0):
        self.value = value


# Protocol and logging
class CapturePhoto(DescribeCommand):
    """This command saves a TIFF file of the current live-view camera image.

    CapturePhoto "filename.tiff"
    CapturePhoto "C:\\Users\\user\\folder\\filename.tiff"
    CapturePhoto "LaserPower%d.tiff" # $LP

    If no folder path is specified, the file is saved in the folder of the
    executed GWL print job. Preexisting pictures with the same file name are overwritten.

    The camera view in NanoWrite must be active for this feature to work.
    Captured images require software capable of displaying 16-bit images.
    This is not the case for standard Windows 7 viewers, however, most freeware image
    software supports these file types. It may be useful to set a preceding GWL delay
    command (e.g. Wait 0.5) to reduce the chance of blurry images as a result of stage
    movements. Furthermore, activating auto-exposure and auto-contrast within the
    AxioVision settings are recommended. The string must be given in quotation marks.
    """

    def __init__(self, imgname: str = "img.tiff"):
        self.imgname = imgname

    def __str__(self) -> str:
        return f'CapturePhoto "{self.imgname}"'


class TimeStampOn(DescribeCommand):
    """0 argument command. For TimeStampOn each message in the message log of
     NanoWrite is accompanied by the current time stamp. For TimeStampOff no
     time stamp is added. These two commands can be used anywhere in the code.
     """
    pass


class TimeStampOff(DescribeCommand):
    """0 argument command. For TimeStampOn each message in the message log of
     NanoWrite is accompanied by the current time stamp. For TimeStampOff no
     time stamp is added. These two commands can be used anywhere in the code.
     """
    pass


class MessageOut(DescribeCommand):
    """Displays the string in the message log of NanoWrite. The string must be given in quotation marks."""

    def __init__(self, message: str = "msg"):
        self.message = message

    def __str__(self) -> str:
        return f'MessageOut "{self.message}"'


class DebugModeOn(DescribeCommand):
    """0 argument command. Messages generated by MessageOut and ShowVar will be displayed in
    the message log when loading jobs.
    """
    pass


class DebugModeOff(DescribeCommand):
    """0 argument command. Messages generated by MessageOut and ShowVar will not be displayed in
    the message log when loading jobs.
    """
    pass


class ShowParameter(DescribeCommand):
    """0 arguments command. Displays the power adaption parameters as
    well as the current InterfaceMax or InterfaceMin value in the
    message log of NanoWrite.
    Note: PerfectShape and GalvoScanMode use different approaches.
    """
    pass


class ShowVar(DescribeCommand):
    """Displays the name and value of the given variable in the message
    log of NanoWrite."""

    def __init__(self, varname: str = "$var"):
        _check_var_name(varname)
        self.varname = varname


class SaveMessages(DescribeCommand):
    """Saves the current content of the message log of NanoWrite in the file specified.
    The string must be given in quotation marks."""

    def __init__(self, message: str = "msg"):
        self.message = message

    def __str__(self):
        return f'SaveMessages "{self.message}"'


class Pause(DescribeCommand):
    """0 argument command. Pauses the printing process and opens a dialog window that
    must be confirmed by the user to proceed with the printing process or further
    commands."""
    pass


class ZDrivePosition(DescribeCommand):
    """0 argument command. Writes the current position of the microscope in the
    NanoWrite message log."""
    pass


class NewStructure(DescribeCommand):
    """0 argument command. Pressing the Skip button on the NanoWrite GUI
    (Advanced tab) during the printing procedure skips all printing
    commands until the next NewStructure command is encountered.
    Printing will be continued from this point. MoveStage and StageGoTo
    commands will not be skipped."""
    pass


# Maintenance
class ManualControl(DescribeCommand):
    """Opens the manual control window. In this window the controls for
    the AOM voltage and for the electric shutter are directly accessible.
    Furthermore, the photo diode voltage is plotted.
    WARNING: Do not use ManualControl unless you are sure about what you
    are doing or you have been sent instructions from a service engineer!"""
    pass


class ReloadIni(DescribeCommand):
    """0 argument Command. Reloads the INI files of the system. A changed INI file
    can be directly updated without closing and restarting NanoWrite."""
    pass


class Recalibrate(DescribeCommand):
    """0 argument command. Recalibrates the laser power (by measuring the power
    scale relative to the AOM voltage)."""
    pass


# Comment
class Comment(DescribeCommand):
    def __init__(self, cmt: str = "Comment"):
        # This is taken care of during initialisation.
        # if not cmt.startswith(COMMENT_CHAR):
        #     raise ValueError(f'Comment lines must start with {COMMENT_CHAR}')
        # else:
        #     self.line = cmt
        self.cmtline = cmt

    def __str__(self):
        return f"{COMMENT_CHAR} {self.cmtline}"


# Commands designators for parsing.
def _build_commands_dictionary():
    subs = [cls for cls in DescribeCommand.__subclasses__()]
    result_dict = {}
    for s in subs:
        shortname = s.__name__
        if shortname.startswith('Describe'):
            shortname = shortname[len('Describe'):]
        elif shortname == 'Comment':
            shortname = COMMENT_CHAR
        result_dict.update({shortname: s})
    return result_dict


available_describe_commands = _build_commands_dictionary()


def parse_describe_line(describe_line: str, accept_unknown: bool = True) -> DescribeCommand:
    """Initialize the correct Describe command object based on input string"""
    for name in available_describe_commands.keys():
        if describe_line.startswith(name):
            command = available_describe_commands[name]()
            # python 3.9 has describe_line.removeprefix(name)
            valstr = describe_line[len(name):]
            command.parse(valstr)
            return command
        elif accept_unknown:
            warnings.warn(f"Warning: Parsed unknown line: {describe_line}")
            return UnknownDescribeCommand(describe_line)

    raise ValueError(f'unable to parse {describe_line} into DescribeCommand')
