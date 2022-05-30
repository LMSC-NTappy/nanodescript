# This file is mostly copied  from the nanoscribe guide "Nanoguide". Downloaded from
# https://support.nanoscribe.com/hc/en-gb/articles/360003617073-ServerMode-and-CommandLineSlicer
# Page consulted on 08th of november 2021"
from pathlib import Path
from stl import mesh


class StlFile(mesh.Mesh):
    def __init__(self, filename):
        self.__full_path = Path(filename).resolve()
        self.path = self.__full_path.parent
        self.filename = self.__full_path.name

        with open(filename, 'rb') as fh:
            self.name, self.data = super().load(fh)

    def __str__(self) -> str:
        return f'{self.filename} at {self.path}'

    @property
    def path(self) -> Path:
        return self._path

    @property
    def full_path(self) -> Path:
        return self.__full_path

    @path.setter
    def path(self, path: Path) -> None:
        self._path = Path(path)
        if not path.exists():
            path.mkdir(parents=True)

    @property
    def filename(self) -> Path:
        return self._filename

    @filename.setter
    def filename(self, file: Path) -> None:
        self._filename = file
