from pathlib import Path
import nanodescript.describe_commands as cmds
from nanodescript.describe_recipe_handler import DescribeRecipe
import logging

logger = logging.getLogger(__name__)


class GwlHandler:
    """Class to handle reading, editing and writing gds files"""

    def __init__(self, ):
        self.gwl_commands = []

    def add_header(self, ):
        """Add a header to a file."""
        header = 'File Generated by DesCRIPT-python alpha'
        self.gwl_commands.append(cmds.Comment(header))

    def add_system_initialisation(self, recipe: DescribeRecipe) -> None:
        cmt = 'System initialization'
        self.gwl_commands.append(cmds.Comment(cmt))
        self.gwl_commands.append(cmds.InvertZAxis(int(recipe.recipe['Output.InvertZAxis'])))

    def add_writing_configuration(self, recipe: DescribeRecipe) -> None:
        """Add a writing configuration block to a gwl job file"""
        cmt = 'Writing configuration'
        self.gwl_commands.append(cmds.Comment(cmt))

        scanmode = recipe.recipe['Output.ScanMode']
        if scanmode == 'Galvo':
            self.gwl_commands.append(cmds.GalvoScanMode())
        elif scanmode == 'Piezo':
            self.gwl_commands.append(cmds.PiezoScanMode())
        else:
            raise ValueError(f"Invalid Output.ScanMode field in recipe: {scanmode}")

        # Put Continuous exposure since I don't know how PulsedMode or LogMode works
        self.gwl_commands.append(cmds.ContinuousMode())
        # No possibility to define PiezosettlingTime that I know of in .recipe file
        self.gwl_commands.append(cmds.PiezoSettlingTime(settlingtime=10))
        # Galvo Acceleration
        self.gwl_commands.append(cmds.GalvoAcceleration(value=recipe.recipe['Exposure.GalvoAcceleration']))
        # Stage Velocity (Max)
        self.gwl_commands.append(cmds.StageVelocity(velocity=20000))  # No definition in .recipe I think

    def add_field_offsets(self, ) -> None:
        """Add a Field offsets block to a gwl job file"""
        self.gwl_commands.append(cmds.Comment("Scan field offsets"))
        self.gwl_commands.append(cmds.XOffset(val=0.0))
        self.gwl_commands.append(cmds.YOffset(val=0.0))
        self.gwl_commands.append(cmds.ZOffset(val=0.0))

    def add_writing_parameters(self, recipe: DescribeRecipe) -> None:
        """Add a writing parameters block to a gwl file"""

        self.gwl_commands.append(cmds.Comment("Writing parameters"))
        self.gwl_commands.append(cmds.PowerScaling(value=1.0))
        self.add_command(cmds.Describe_empty())
        self.gwl_commands.append(cmds.Comment("Contour writing parameters"))
        self.gwl_commands.append(cmds.Describe_var(name='$contourLaserPower',
                                                   value=recipe.recipe['Exposure.ShellLaserPower']))
        self.gwl_commands.append(cmds.Describe_var(name='$contourScanSpeed',
                                                   value=recipe.recipe['Exposure.ShellScanSpeed']))
        self.add_command(cmds.Describe_empty())
        self.gwl_commands.append(cmds.Comment("Solid hatch lines writing parameters"))
        self.gwl_commands.append(cmds.Describe_var(name='$solidLaserPower',
                                                   value=recipe.recipe['Exposure.CoreLaserPower']))
        self.gwl_commands.append(cmds.Describe_var(name='$solidScanSpeed',
                                                   value=recipe.recipe['Exposure.CoreScanSpeed']))
        self.gwl_commands.append(cmds.Describe_var(name='$interfacePos',
                                                   value=recipe.recipe['Exposure.FindInterfaceAt']))

    def add_command(self, command: cmds.DescribeCommand):
        """Add a command to the current recipe"""
        self.gwl_commands.append(command)

    def reset(self):
        """Reset the content of the file."""
        self.gwl_commands = []

    @staticmethod
    def verify_file(filename) -> Path:
        """Verify that a file exists and has the right extension.
        Also makes sure that the file is a Path object."""
        filepath = Path(filename)
        if filepath.suffix == '.gwl' and filepath.exists():
            return filepath
        else:
            raise ValueError(f"Invalid input file {filename}")

    def read_job_file(self, filename: str, reset: bool = True, accept_unknown_commands: bool = True) -> None:
        """Read a job file and initialize the object."""
        if reset:
            self.reset()
            self.add_header()

        file = Path(filename)

        with file.open("r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line:
                    cmd = cmds.parse_describe_line(line, accept_unknown=accept_unknown_commands)
                    self.gwl_commands.append(cmd)

    def get_gwlstrings(self) -> list[str]:
        """Return all the gwl strings in the current handler"""
        return [str(gwl) for gwl in self.gwl_commands]

    def write_file(self, filepath: str = None) -> None:
        """"Write the gwl file in a file"""
        cmd_strings = self.get_gwlstrings()

        logger.info(f"Writing gwl file: {filepath}")

        with open(filepath, 'w') as aim:
            for cmd in cmd_strings:
                aim.write(str(cmd) + '\n')
