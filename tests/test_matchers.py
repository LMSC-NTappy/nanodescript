import nanodescript.nanoscribe_matchers as ndm

class TestMatcher:
    def setup_class(self):
        pass

    def test_matcher_names(self):
        assert ndm.get_all_matchers_names() == ['LayerMatcher', 'LayerDatatypeMatcher', 'PrintZoneMatcher']

    def test_get_matcher(self):
        assert isinstance(ndm.get_matcher_by_name('LayerMatcher'), ndm.NanoscribeMatcher)
