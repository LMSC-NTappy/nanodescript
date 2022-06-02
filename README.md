# nanodescript

nanodescript is a python Command-Line Application / Application Programming interface aiming at
interfacing [nanoscribe](https://nanoscribe.com/) stereo-lithography prints with the gds file format, which is standard in
the Semiconducting industry.

It uses the Nanoscribe DeScribe slicer to generate patterns of nanoscribe prints externally defined 
in a gds file. This allows for more flexibility than the native patterning tool. This also provides 
integrability with other lithography and micro-fabrication processes. 

The name nanodescript comes from NanoScribe-DeScribe-Scripting. 

Warning: nanodescript is NOT a standalone stl slicer for nanoscribe printers. It relies
on a DeScribe installation existing on the system for performing the slicing operation and visualising 
the results. If you are interested in python slicing of stl files, check out SamDehaeck's
[TipSlicer](https://github.com/SamDehaeck/TipSlicer) project.

Nanodescript is developed and tested on the Photonic Professional GT(2).

## Documentation

This is it. It should get you started, for more information I let you explore the code a bit yourself,
and if you don't find what you need or still have questions you can always ask me.

## Installation

Warning! Without a valid DeScribe installation on the system, nanodescript will not work.

We recommend installing nanodescript in a [conda](https://docs.conda.io/en/latest/) environment.
The reason for this is that [gdstk](https://heitzmann.github.io/gdstk/) is used for the
manipulation of gdsII files, and does not support pip installation. It must be installed
manually beforehand using conda.

Installing gdstk:
```bash
# Configure the conda-forge channel. channel_priority strict will be default in conda 5
conda config --env --add channels conda-forge
conda config --env --set channel_priority strict
# Install gdstk
conda install gdstk
```

Other dependencies will be installed automatically when installing nanodescript.

For now, nanodescript can be installed only from source by downloading the github repository, and
running the pip install command from the extracted directory (use -e for dev-mode installation):

```bash
pip install .
```

## Usage

After installing nanodescript you run the following command in your anaconda prompt:

```bash
 nanodescript path_to_gds_file/pattern.gds path_to_output_dir/descript_output
```

This will read the `pattern.gds` file, look for nanoscribe print zones and in the library, find associated
stl files and slice them, create the `descript_output` directory if it does not exist already. 
Inside, it will create a `<library>_job.gwl` file named after your library containing nanoscribe-ready code.

Then, you can open the job with DeScribe and generate the 3D preview to verify the output
before running it.

Basic help and command line options can be accessed with

```bash
 nanodescript -h
```

### Intro

The point of application for nanodescript are patterns of microstructures integrated in a 
semiconductor device fabrication process flow, such as micro-lenses arrays,
photonics couplers, grayscale lithography etc. 

The patterning strategy is to create a gds file where some Cell and their Instances can be
automatically identified as being nanoscribe prints, matched with .stl files and sliced with Describe. 
A global print job is then generated automatically.

Hereafter, we provide instructions for basic usage using the Command Line Interface and an example
pattern where crosses and tips are printed. (API) is briefly explained at the end, documentation
will be expanded on request.

### GDS software requirements

We recommend designing patterns either programmatically using gdstk, or
using [KLayout](https://www.klayout.de/) since it's open source. In
principle anything else such as L-edit should work.

### nanoscribe cells matching

To identify (==match) which cells are nanoscribe prints, the program applies a matching strategy.
There are currently three different matching strategies supported:
- Print zone matching 
- Layer matching (by default)
- Layer/Datatype matching

They are described below but perform in essence the same task: identifying which cell 
instances have to be included in the nanoscribe gwl job.

#### Print zone matching

This strategy matches all cells containing a reference to a cell named `nanoscribe_print_zone` 
(or a custom name set by the user). All cells containing an instance of the `nanoscribe_print_zone` 
cell will be identified as nanoscribe print zones. The following image shows an 
example pattern where a cross and a flat cone (tip) needs to be printed in an array. 
Here, both `cross_20_80` and `tip` contain a `nanoscribe_print_zone` instance directly. 

In the example, the `nanoscribe_print_zone` cell contains a 100x100 um box displayed in pink. 
This poly serves no other purpose than informing the user and won't be printed. Actually, the 
content of the nanoscribe print zone can be arbitrary.

<img src="https://github.com/LMSC-NTappy/nanodescript/blob/master/media/demo_pattern.PNG?raw=true" alt="Demonstration of a pattern containing nanoscribe print zones." width="50%" height="50%">

After running the following command from the directory containing the gds and stl files
```bash
nanodescript test_pattern_printzone.gds gds_slicing_output --matcher printzonematcher
```
the following job file is created in the `gds_slicing_output` folder (also created).

<img src="https://github.com/LMSC-NTappy/nanodescript/blob/master/media/outputpattern_printzone.PNG?raw=true" alt="Output of the Print Zone matching strategy" width="50%" height="50%">

This strategy is a bit overkill since it supposes populating (_bloating_) your gds library with 
placeholder cell instances that serve no practical purposes in the fabrication. Originally, the 
intention was to implement additional functionality to the `nanoscribe_print_zone`. In the end 
I didn't drive the initial development of this project in that direction, so that this entire 
strategy is not so relevant as it used to be.

#### layer matching

This strategy matches all cells that contain polygons, paths or labels of a certain layer number.

In the example below, the nanoscribe layer is number 66, here again both `cross_20_80` and `tip`
are matched.

<img src="https://github.com/LMSC-NTappy/nanodescript/blob/master/media/demo_pattern_layer.PNG?raw=true" alt="Demonstration of a pattern containing nanoscribe layers and datatypes." width="50%" height="50%">

After running the following command outputs the same result as the print zone matcher

```bash
nanodescript test_pattern_printzone.gds gds_slicing_output --matcher layermatcher
```

<img src="https://github.com/LMSC-NTappy/nanodescript/blob/master/media/outputpattern_layer.PNG?raw=true" alt="Output of the layer matching strategy" width="50%" height="50%">

#### layer/datatype matching

This strategy extends on the previous one by only matching cells containing a certain layer number and datatype number
combination. For example, the layer 66 and datatype 1 combination can be used to print only part of the cross pattern.

```bash
nanodescript test_pattern_printzone.gds gds_slicing_output --matcher layerdatatypematcher
```

Which outputs as expected a job file that will prints only the crosses.

<img src="https://github.com/LMSC-NTappy/nanodescript/blob/master/media/outputpattern_layerdatatype.PNG?raw=true" alt="Output of the layer datatype matching strategy" width="50%" height="50%">


### stl matching

Once nanoscribe cells have been matched, they are associated with files bearing the same names and 
the `.stl` extension. In our example, `cross_20_80.stl` and`tip.stl` are searched. By default, the
 files are searched in the same directory as the .gds library but this can be changed during execution.

Since the stl matching is performed by cell name, needless to say the content of those cells can be 
arbitrary. However, I recommend inserting shapes resembling the footprints of the structures 
to be printed. Attention should be paid at this stage about the coordinate systems in the cells. The
X-Y-Z orientation and origin in the .stl should ideally be identical to the one used in the nanoscribe
cell.

If for some reason this does not work for your application, stl files can also be associated _manually_ 
using the API.

### Transformations

nanodescript (through the describe slicer) supports applying scaling and rotations to cells during 
instantiations. Here below is an example with four crosses.

<img src="https://github.com/LMSC-NTappy/nanodescript/blob/master/media/output_pattern_scale.PNG?raw=true" alt="Output with cell transformations" width="50%" height="50%">

### Efficiency in the output 

The main rationale for using nanodescript for patterning is that it guarantees that the slicing operation
is performed the minimal necessary number of times, so that the output files are as small as possible and 
render as quickly as possible

### configuration

Configuration options for the software are stored locally in a configuration file called `nanodescript_config.ini`.
Notably, it contains the default recipe applied for stl slicing, the path to `describe.exe` and options for .

The location of the configuration file can be shown by using
```bash
nanodescript -c
C:\Users\USERNAME\AppData\Local\nanodescript\nanodescript_config.ini
```

The default recipe can be seen using
```python
import nanodescript
nanodescript.nanodescript_config.get_default_recipe()
```

You can edit configuration entries by using e.g.
```python
import nanodescript
#Default recipe hatching distance
nanodescript.nanodescript_config.edit_config('default_recipe', 'Filling.HatchingDistance', 0.2)
nanodescript.nanodescript_config.save_config()
#Layer matcher number
nanodescript.nanodescript_config.edit_config('layermatcher', 'layer_number', 88)
nanodescript.nanodescript_config.save_config()
#layer datatype matcher options. Also saves it so that running save_config() is not needed.
nanodescript.nanodescript_config.edit_config('layerdatatypematcher', 'layer_number', 88, also_save=True)
nanodescript.nanodescript_config.edit_config('layerdatatypematcher', 'datatype_number', 2, also_save=True)
#Reset the config if you suddenly mess up and need to retrieve the installation configuration
nanodescript.nanodescript_config.reset_config()
```

This edits the hatching distance of the default recipe. The call to `save_config` effectively overwrites the 
`nanodescript_config.ini` file on disk so that the settings are applied at the program next start 
(can also be achieved by calling `edit_config` with the `also_save=True` optional argument).

## Bugs and releases

Nanodescript is currently pre-alpha release, meaning that it is continuously developed
to fit my needs and applications. I try to implement some kind of continuous deployment 
workflow.

In any case, if you use this code I am happy, if you signal me bugs I am even more happy.

## Further developments

Future developments will be made on a "need to use" basis. If you have ideas or needs please signal
it to me, so we can look at how to implement it.

Existing ideas include:
- Customisation of individual print instances using labels as modificators.
- STL generation from the gds pattern directly (simplest case: vertical extrusion).
- Support for text printing.
- Dedicated interface finding routines etc.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss 
what you would like to change. Please make sure to update tests as appropriate. 

Improvement suggestions / New Feature requests are welcome as well. Commitment to testing 
the new features and providing feedback is expected on the requesting side.

Running the tests further requires installing pytest (manually for now)

```bash
pip install pytest
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
