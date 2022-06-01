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

### Foreword

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

### nanoscribe cells and stl files matching

To identify which cells are nanoscribe prints, the gds library file must contain a 
cell named `nanoscribe_print_zone` (or a custom name can be changed by the user).

Then, all cells which contain an instance of the `nanoscribe_print_zone` cell will be
identified as nanoscribe print zones. The following image shows an example pattern where
a cross and a flat cone (tip) need to be printed in an array. Here, the cells 
`cross_20_80` and `tip` both contain a `nanoscribe_print_zone` instance, which is
a cell containing only a 100x100 um box displayed in pink. The box serves no other 
purpose than informing the user and won't be printed. 

The other shapes in those cells (the cross and the circle) are the footprints of the structures 
to be printed. Their role is also purely informative as well. However, attention should
be paid at this stage about the center of the cells. The x-y origin of nanoscribe cells (0.0,0.0)
should correspond to the origin of the .stl file. The X-Y-Z axes orientations should be identical as well.

This strategy (that I call print zone matching) is interesting for its simplicity. There is no 
doubt about how the cell will behave in cascading dependencies. Other cell matching strategies 
such as matching cells containing shapes of a specific layer/datatype combination are also 
available but not directly supported in the CLI (API only). Those can be helpful to avoid bloating
the gds library with print zones.

To find stl files corresponding to the nanoscribe cells, the software will look for file named
like the cells bearing the `.stl` extension. In the example, it will look for `cross_20_80.stl` and 
`tip.stl` files. By default, the search path is in the directory (and sub-directories) of 
the gds file, but other search paths can be added through the CLI (see help). stl files can
also be associated _manually_ with cells using the API.

![Demonstration pattern containing nanoscribe patterns.](https://github.com/LMSC-NTappy/nanodescript/blob/master/media/demo_pattern.PNG?raw=true)

### Describe Recipe Customisation

The standard recipe applied for slicing `.stl` files is saved as a constant in the software.
It can be accessed in the following way:

```python
import nanodescript
nanodescript.DEFAULT_RECIPE
```

It can be customized during execution using the `--recipe` option. See 

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
