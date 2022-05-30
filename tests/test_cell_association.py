from nanodescript.cell_association import CellAssociation


class TestCellAssociation:
    def setup_method(self):
        self.cell_association = CellAssociation()

    def test_defaults(self):
        assert self.cell_association.cell is None
        assert self.cell_association.transformation is None
        assert self.cell_association.stl_file is None
        assert self.cell_association.recipe is None
        assert self.cell_association.include_file is None
