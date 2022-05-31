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
the results. If you are interested in direct slicing of stl files, check out SamDehaeck's
[TipSlicer](https://github.com/SamDehaeck/TipSlicer) project.

## Documentation

This is it. This should get you started, for more information I let you explore the code a bit yourself,
and if you don't find what you need or still have questions you can always ask me a question.

## Installation

Warning! Without a valid DeScribe installation on the system, nanodescript will not work.

We recommend installing nanodescript in a conda environment.
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

Other dependencies will be installed automatically when installing nanodescript

```bash
# Hopefully this works at some point
pip install nanodescript
```

From source, nanodescript can be installed by downloading the github repository, and
running the pip install command from the extracted directory (use -e for a local installation):

```bash
pip install .
```

Running tests further require installing pytest (manually for now)

```bash
pip install pytest
```

or 

```bash
 conda install -c anaconda pytest 
```

## Usage

### TL;DR

After installing nanodescript you run the following command in your anaconda prompt:

```bash
 nanodescript path_to_gds_file/pattern.gds path_to_output_dir/descript_output
```

This will read the `pattern.gds` file, look for nanoscribe print zones and stl files 
(see search method below) in the library, create the `descript_output` directory 
if it does not already exist and create a `library_job.gwl` file named after your library
containing nanoscribe code.

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

### GDS design requirements

We recommend designing patterns either programmatically using gdstk, or
using [KLayout](https://www.klayout.de/) since it's open source. In
principle anything else such as L-edit should work.

![Image of the ](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)

#### nanoscribe zone matching

To identify which cells are nanoscribe prints, the gds library file must contain a 
cell named `nanoscribe_print_zone` (or a custom name can be changed by the user).

Then, all cells which contain an instance of the `nanoscribe_print_zone` cell will be
identified as nanoscribe print zones. The 

#### stl file matching

## Standard use

Standard usage is provided using the command line interface. 

```python
import foobar

# returns 'words'
foobar.pluralize('word')

# returns 'geese'
foobar.pluralize('goose')

# returns 'phenomenon'
foobar.singularize('phenomena')
```

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
