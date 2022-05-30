from __future__ import annotations

from dataclasses import dataclass, InitVar

from gdstk import Reference
import numpy as np
from scipy.spatial.transform import Rotation


@dataclass
class CellTransformation:
    magnification: float = 1.0
    origin: np.ndarray = (0.0, 0.0)
    x_reflection: bool = False
    rotation: float = 0.0
    reference: InitVar[Reference] = None

    def __post_init__(self, reference):
        # Initialise a transformation object.
        if reference is not None:
            self.magnification = reference.magnification
            self.origin = np.array(reference.origin)
            self.rotation = reference.rotation
            self.x_reflection = reference.x_reflection

    def compose_transformations(
            self,
            transfo=None,
    ) -> CellTransformation:
        """Compose the transformation object with an other transformation"""
        # Composition of magnification, rotation and reflection is additive
        compound_magnification = self.magnification * transfo.magnification
        compound_rotation = self.rotation + transfo.rotation
        compound_xreflection = self.x_reflection ^ transfo.x_reflection

        # Compound origin is the result of transformation matrix composition
        tmp = np.zeros(4)
        tmp[:2] = transfo.origin
        compound_origin = self.origin + (self.get_transformation_matrix() @ tmp)[:2]  # @ is matrix multiplication oper.
        # compound_origin = tuple(compound_origin)

        # Return new transformation
        return CellTransformation(magnification=compound_magnification,
                                  rotation=compound_rotation,
                                  origin=compound_origin,
                                  x_reflection=compound_xreflection)

    def get_rotation_matrix(self) -> np.ndarray:
        """Return the rotation matrix"""
        rot = Rotation.from_rotvec(self.rotation * np.array([0, 0, 1]))
        return rot.as_matrix()

    def get_rotation_quaternion(self) -> np.ndarray:
        """Return the rotation quaternion"""
        rot = Rotation.from_rotvec((self.rotation * np.array([0, 0, 1])))
        return rot.as_quat()

    def get_magnification_matrix(self) -> np.ndarray:
        """Return the scale matrix"""
        return self.magnification * np.eye(3)

    def get_xreflection_matrix(self) -> np.ndarray:
        """Return the x-axis reflection matrix"""
        xref = np.eye(3)
        xref[0, 0] = (-1) ** self.x_reflection
        return xref

    def get_transformation_matrix(self, with_translation: bool = False) -> np.ndarray:
        """Get the total transformation matrix"""
        mat = np.eye(4)
        rom = self.get_rotation_matrix()
        scm = self.get_magnification_matrix()
        xrm = self.get_xreflection_matrix()
        # @ operator is the matrix multiplication operator. Order of operation is defined by gds convention
        tot = scm @ (rom @ xrm)
        mat[:3, :3] = tot
        # If desired we can add the translation in the matrix but often it is treated separately
        if with_translation:
            mat[:2, 3] = self.origin
        return mat
