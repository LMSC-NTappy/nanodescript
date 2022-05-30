from setuptools import setup

install_req = ['gdstk>=0.6.1',
               'numpy>=1.21',
               'numpy-stl>=2.16',
               'scipy>=1.7',
               'tqdm>=4.64',
               ]

setup(name='nanoscribe_descript_python',
      version='0.0.1',
      description='Python Nanoscribe coordination with gds code',
      author='Nicolas Tappy',
      author_email='nicolas.tappy@epfl.ch',
      packages=['nanodescript'],
      install_requires=install_req)
