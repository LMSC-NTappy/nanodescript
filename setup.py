from setuptools import setup

install_req = ['gdstk>=0.6.1',
               'numpy>=1.21',
               'numpy-stl>=2.16',
               'scipy>=1.7',
               'tqdm>=4.64',
               'platformdirs',
               ]

setup(name='nanodescript',
      version='0.0.2',
      description='Python Nanoscribe coordination with gds code',
      author='Nicolas Tappy',
      author_email='nicolas.tappy@epfl.ch',
      url="https://github.com/LMSC-NTappy/nanodescript",
      keywords='nanoscribe describe scripting',
      packages=['nanodescript'],
      install_requires=install_req,
      entry_points={'console_scripts': ['nanodescript=nanodescript.nanoscribe_descript:main']})
