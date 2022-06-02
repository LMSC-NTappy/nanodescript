# nanodescript

nanodescript is a python Command-Line Application / Application Programming interface
patterning nanoscribe 2-photon stereo-lithography prints using the gds file format.

It uses the Nanoscribe DeScribe slicer to generate patterns of nanoscribe prints 
externally defined in a gds file. This allows for more flexibility than the 
native patterning tool. This also provides integrability with other lithography and
micro-fabrication processes. 

The name nanodescript comes from NanoScribe DeScribe Scripting. 

Warning: nanodescript is NOT a standalone stl slicer for nanoscribe printers. It relies
on a DeScribe installation existing on the system for performing the slicing operation and visualising 
the results. If you are interested in python slicing of stl files, check out SamDehaeck's
[TipSlicer](https://github.com/SamDehaeck/TipSlicer) project.

## Documentation

This is it. It should get you started, for more information I let you explore the code a bit yourself,
and if you don't find what you need or still have questions you can always ask me a question.

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

Running tests further require installing pytest (manually for now)

```bash
pip install pytest
```

## Usage

### TL;DR

After installing nanodescript you run the following command in your anaconda prompt:

```bash
 nanodescript path_to_gds_file/pattern.gds path_to_output_dir/descript_output
```

This will read the `pattern.gds` file, look for nanoscribe print zones and stl files 
(see search method below) in the library, create the `descript_output` directory
if it does not already exist. Then, it will create a `<library>_job.gwl` file named after your library
containing nanoscribe-ready code.

Then, you can open the library with DeScribe and generate the 3D preview to verify the output
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

Hereafter, we provide instructions for basic usage using the Command Line Interface. Advanced
usage (API) is briefly explained and will be expanded on request.

### GDS software requirements

We recommend designing patterns either programmatically using gdstk, or
using [KLayout](https://www.klayout.de/) since it's open source. In
principle anything else such as L-edit should work.

### nanoscribe cells matching

To identify (==match) which cells are nanoscribe prints, the program applies a matching strategy.
There are currently three different matching strategies supported:
- Print zone matching (by default)
- Layer matching
- Layer/Datatype matching

They are described below but perform in essence the same task: identifying which cell 
instances have to be included in the nanoscribe gwl job.

#### Print zone matching

This strategy matches all cells that contain a reference to a "print-zone" cell 
named `nanoscribe_print_zone` (or a custom name set by the user).

All cells containing an instance of the `nanoscribe_print_zone` cell will be
identified as nanoscribe print zones. The following image shows an example pattern where
a cross and a flat cone (tip) needs to be printed in an array. Here, both
`cross_20_80` and `tip` contain a `nanoscribe_print_zone` instance directly. 
Cells occupying the upper levels of the hierarchy are not matched.

In the example, the `nanoscribe_print_zone` cell contains a 100x100 um box displayed in pink. 
This poly serves no other purpose than informing the user and won't be printed. Actually, the 
content of the nanoscribe print zone can be arbitrary.

![Demonstration of a pattern containing nanoscribe print zones.](https://github.com/LMSC-NTappy/nanodescript/blob/master/media/demo_pattern.PNG?raw=true)

After running the following command from the directory containing the gds and stl files
```bash
nanodescript test_pattern_printzone.gds gds_slicing_output --matcher printzonematcher
```

the following job file is created in the `gds_slicing_output` folder (also created).

![Output of the Print Zone matching strategy](https://github.com/LMSC-NTappy/nanodescript/blob/master/media/outputpattern_printzone.PNG?raw=true)

#### layer matching

This strategy matches all cells that contain polygons, paths or labels of a certain layer number.

In the example below, the nanoscribe layer is number 66, here again both `cross_20_80` and `tip`
are matched.

![Demonstration of a pattern containing nanoscribe layers and datatypes.](https://github.com/LMSC-NTappy/nanodescript/blob/master/media/demo_pattern_layer.PNG?raw=true)

After running the following command outputs the same result as the print zone matcher

```bash
nanodescript test_pattern_printzone.gds gds_slicing_output --matcher layermatcher
```

![Output of the layer matching strategy](https://github.com/LMSC-NTappy/nanodescript/blob/master/media/outputpattern_layer.PNG?raw=true)

#### layer/datatype matching

This strategy extends on the previous one by only matching cells containing a certain layer number and datatype number
combination. For example, the layer 66 and datatype 1 combination can be used to print only part of the cross pattern.

```bash
nanodescript test_pattern_printzone.gds gds_slicing_output --matcher layerdatatypematcher
```

Which outputs as expected

![Output of the layer datatype matching strategy](https://github.com/LMSC-NTappy/nanodescript/blob/master/media/outputpattern_layerdatatype.PNG?raw=true)


### stl matching

The other shapes in those cells (the cross and the circle) are the footprints of the structures 
to be printed. Their role is also purely informative as well. However, attention should
be paid at this stage about the center of the cells. 

To find stl files corresponding to the nanoscribe cells, the software will look for file named
like the cells bearing the `.stl` extension. In the example, it will look for `cross_20_80.stl` and 
`tip.stl` files. By default, the search path is in the directory (and sub-directories) of 
the gds file, but other search paths can be added through the CLI (see help). stl files can
also be associated _manually_ with cells using the API.


### configuration

Configuration options for the software are stored locally in a configuration file called `nanodescript_config.ini`.
Notably, it contains the standard recipe applied in slicing `.stl` files and the path to the `describe.exe` executable.

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
nanodescript.nanodescript_config.edit_config('default_recipe', 'Filling.HatchingDistance', 0.2)
nanodescript.nanodescript_config.save_config()
```
This edits the hatching distance of the default recipe. The call to `save_config` effectively overwrites the 
`nanodescript_config.ini` file on disk so that the settings are applied at the program next start.

## Bugs

Nanodescript is currently in alpha release, meaning that it is continuously developed
to fit the main developer's application. We want 

## Further developments

Future developments will be made on a "need to use" basis. 

Existing ideas include:
- Support for other matchers in the CLI.
- Customisation of individual print instances using labels as describe recipe modificators.
- STL generation from the gds pattern directly (simple case of vertical extrusions at least).
- Support for nanoscribe text printing.
- Dedicated interface finding zones at dedicated positions.


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss 
what you would like to change. Please make sure to update tests as appropriate. 

Improvement suggestions / New Feature requests are welcome as well. Commitment to testing 
the new features and providing feedback is expected on the requesting side.

## License
[MIT](https://choosealicense.com/licenses/mit/)
