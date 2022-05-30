from nanodescript.cell_association import CellAssociation

class TestCellAssociation:
    def setup_method(self):
        self.cell_association = CellAssociation()

    def test_defaults(self):
        assert self.cell_association.cell == None
        assert self.cell_association.transformation == None
        assert self.cell_association.stl_file   == None
        assert self.cell_association.out_datgwl == None
        assert self.cell_association.out_jobgwl == None
        assert self.cell_association.out_recipe == None
        assert self.cell_association.out_files  == None
        assert self.cell_association.include_file == None