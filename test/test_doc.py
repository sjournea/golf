import pytest

from golf_db.doc import Doc
from golf_db.exceptions import DocValidateFail


class TestDocBase:
    def test_init_empty(self):
        doc = Doc()
        assert doc.toDict() == {}
        doc.fromDict({})
        assert doc.toDict() == {}

    def test_init_dct(self):
        doc = Doc(dct={})
        assert doc.toDict() == {}
        doc.fromDict({})
        assert doc.toDict() == {}

    def test_validate(self):
        doc = Doc()
        doc.validate()


class DocTest(Doc):
    fields = ["ivalue", "fvalue", "svalue", "lvalue"]


class TestDocKeyword:
    def test_init(self):
        doc = DocTest(ivalue=3, fvalue=1.0, svalue="hello", lvalue=False)
        assert doc.ivalue == 3
        assert doc.fvalue == 1.0
        assert doc.svalue == "hello"
        assert not doc.lvalue

    def test_init_dct(self):
        doc = DocTest(ivalue=3, fvalue=1.0, svalue="hello", lvalue=False)
        assert doc.toDict() == {
            "ivalue": 3,
            "fvalue": 1.0,
            "svalue": "hello",
            "lvalue": False,
        }


class TestDocFieldEmpty:
    def test_init(self):
        t = DocTest()
        for field in DocTest.fields:
            assert hasattr(t, field)
            assert getattr(t, field) is None
        t.validate()

    def test_init_empty_dict(self):
        t = DocTest(dct={})
        for field in DocTest.fields:
            assert hasattr(t, field)
            assert getattr(t, field) is None

    def test_dct_is_nones(self):
        t = DocTest()
        dct = t.toDict()
        for field in DocTest.fields:
            assert field in dct
            assert dct[field] is None
        assert dct == {field: None for field in DocTest.fields}

    def test_validate(self):
        doc = DocTest()
        doc.validate()


class TestDocFieldValues:
    @pytest.mark.parametrize("value", [1, 10, 100, 1000, 0, -1])
    def test_ivalue(self, value):
        t = DocTest(dct={"ivalue": value})
        assert t.ivalue == value
        assert t.fvalue is None
        assert t.svalue is None
        assert t.lvalue is None
        dct = t.toDict()
        assert len(dct) == len(DocTest.fields)
        assert dct["ivalue"] == value
        assert t.fvalue is None
        assert t.svalue is None
        assert t.lvalue is None

    @pytest.mark.parametrize("value", [1, 10, 100, 1000, 0, -1])
    def test_fvalue(self, value):
        t = DocTest(dct={"fvalue": value})
        assert t.fvalue == value
        assert t.ivalue is None
        assert t.svalue is None
        assert t.lvalue is None
        dct = t.toDict()
        assert len(dct) == len(DocTest.fields)
        assert dct["fvalue"] == value
        assert t.ivalue is None
        assert t.svalue is None
        assert t.lvalue is None

    @pytest.mark.parametrize("svalue", ["hello", "world", "", "\x46"])
    def test_svalue(self, svalue):
        t = DocTest(dct={"svalue": svalue})
        assert t.svalue == svalue
        assert t.ivalue is None
        assert t.fvalue is None
        assert t.lvalue is None
        dct = t.toDict()
        assert len(dct) == len(DocTest.fields)
        assert dct["svalue"] == svalue
        assert t.ivalue is None
        assert t.fvalue is None
        assert t.lvalue is None

    @pytest.mark.parametrize("lvalue", [True, False])
    def test_lvalue(self, lvalue):
        t = DocTest(dct={"lvalue": lvalue})
        assert t.lvalue == lvalue
        assert t.ivalue is None
        assert t.fvalue is None
        assert t.svalue is None
        dct = t.toDict()
        assert len(dct) == len(DocTest.fields)
        assert dct["lvalue"] == lvalue
        assert t.ivalue is None
        assert t.fvalue is None
        assert t.svalue is None


class DocValidateTest(DocTest):
    """Overloads TestDoc and adds type validation."""

    def validate(self):
        # all fields MUST be defined
        for field in self.fields:
            if getattr(self, field) is None:
                raise DocValidateFail("{} must be defined".format(field))
        # Validate types
        if not isinstance(self.ivalue, int):
            raise DocValidateFail("ivalue must be an int")
        if not isinstance(self.fvalue, float):
            raise DocValidateFail("fvalue must be an float")
        if not isinstance(self.svalue, str):
            raise DocValidateFail("svalue must be an str")
        if not isinstance(self.lvalue, bool):
            raise DocValidateFail("lvalue must be an bool")


class TestDocValidate:
    def test_init(self):
        t = DocValidateTest()
        with pytest.raises(DocValidateFail):
            t.validate()

    def test_init_good(self):
        dct = {"ivalue": 1, "lvalue": True, "fvalue": 45.0, "svalue": "Spam"}
        t = DocValidateTest(dct=dct)
        t.validate()

    lstMissing = [
        {"ivalue": 1, "lvalue": True, "fvalue": 45.0},
        {"ivalue": 1, "lvalue": True, "svalue": "Spam"},
        {"ivalue": 1, "fvalue": 45.0, "svalue": "Spam"},
        {"lvalue": True, "fvalue": 45.0, "svalue": "Spam"},
    ]

    @pytest.mark.parametrize("dct", lstMissing)
    def test_init_missing(self, dct):
        t = DocValidateTest(dct=dct)
        with pytest.raises(DocValidateFail):
            t.validate()

    lstBadTypes = [
        {"ivalue": 1.0, "lvalue": True, "fvalue": 45.0, "svalue": "Spam"},
        {"ivalue": 1, "lvalue": "s", "fvalue": 45.0, "svalue": "Spam"},
        {"ivalue": 1, "lvalue": True, "fvalue": "h", "svalue": "Spam"},
        {"ivalue": 1, "lvalue": True, "fvalue": 45.0, "svalue": 46},
    ]

    @pytest.mark.parametrize("dct", lstBadTypes)
    def test_bad_types(self, dct):
        t = DocValidateTest(dct=dct)
        with pytest.raises(DocValidateFail):
            t.validate()
