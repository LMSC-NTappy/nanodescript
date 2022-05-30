from nanodescript.cell_transformation import CellTransformation
import numpy as np

### WARNING! STILL Missing a test for CellTransformation initialisation from Reference!

class TestCellTransformation:
    def setup_method(self):
        self.cell_transformation = CellTransformation()

    def test_defaults(self):
        assert self.cell_transformation.magnification == 1.0
        assert self.cell_transformation.origin == (0.0,0.0)
        assert self.cell_transformation.x_reflection == False
        assert self.cell_transformation.rotation == 0.0

    def test_repr(self):
        assert self.cell_transformation.__repr__() == "CellTransformation(magnification=1.0, origin=(0.0, 0.0), x_reflection=False, rotation=0.0)"

    def test_rotation_quaternion(self):
        assert np.all(self.cell_transformation.get_rotation_quaternion() == np.array([0.0,0.0,0.0,1.0]))

    def test_magnification_matrix(self):
        self.cell_transformation.magnification = 2.5
        np.testing.assert_allclose(self.cell_transformation.get_magnification_matrix(),2.5*np.eye(3), rtol=1e-6)

    def test_xreflection_matrix(self):
        self.cell_transformation.x_reflection = True
        xrefmat = np.array([[-1,0,0],[0,1,0],[0,0,1]])
        np.testing.assert_allclose(self.cell_transformation.get_xreflection_matrix(),xrefmat,rtol=1e-6)

    def test_rotation_matrix(self):
        self.cell_transformation.rotation = 30*np.pi/180
        rotmat = np.array([[0.866025404,-0.5,0],[0.5,0.866025404,0],[0,0,1]])
        np.testing.assert_allclose(self.cell_transformation.get_rotation_matrix(),rotmat,rtol=1e-6)

    def test_transformation_matrix(self):
        self.cell_transformation.magnification = 2.5
        self.cell_transformation.x_reflection = True
        self.cell_transformation.rotation = 30*np.pi/180
        transmat = np.array([[-2.16506350946,-1.25,0,0],[-1.25,2.16506350946,0,0],[0,0,2.5,0],[0,0,0,1.0]])
        testmat = self.cell_transformation.get_transformation_matrix(with_translation=False)
        self.cell_transformation.origin = (20.0,30.0)
        transmat = np.array([[-2.16506350946,-1.25,0,20],[-1.25,2.16506350946,0,30],[0,0,2.5,0],[0,0,0,1.0]])
        testmat = self.cell_transformation.get_transformation_matrix(with_translation=True)
        np.testing.assert_allclose(testmat,transmat)

    def test_compose_transformations(self):
        t2 = CellTransformation(magnification=0.4, origin=(0.0, 0.0), x_reflection=False, rotation=15*np.pi/180)
        t1 = CellTransformation(magnification=2.5, origin=(30, 20), x_reflection=True, rotation=30*np.pi/180)
        
        t3 = t1.compose_transformations(t2)
        testmat = t3.get_transformation_matrix(with_translation=True)
        transmat = np.array([[-np.sqrt(2)/2,-np.sqrt(2)/2,0,30],[-np.sqrt(2)/2,np.sqrt(2)/2,0,20],[0,0,1.0,0],[0,0,0,1.0]])
        
        np.testing.assert_allclose(testmat,transmat)