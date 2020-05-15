from unittest import TestCase

from lucyfer.searchset import DjangoSearchSet
from lucyfer.searchset.base import BaseMetaClass, BaseSearchSetMetaClass
from lucyfer.searchset.fields import DjangoCharField
from tests.utils import EmptyDjangoModel


class TestSearchSetMetaClass(TestCase):
    def test_metaclass_field(self):
        class SearchSet(DjangoSearchSet):
            pass

        self.assertTrue(hasattr(SearchSet, '_meta'))
        self.assertTrue(issubclass(SearchSet._meta, BaseMetaClass))

        expected_meta_fields = [
            "model", "show_suggestions", "escape_quotes_in_suggestions",
            "fields_to_exclude_from_mapping", "fields_to_exclude_from_suggestions"]

        for field in expected_meta_fields:
            self.assertTrue(hasattr(SearchSet._meta, field))

    def test_additional_meta_fields(self):

        class SearchSet(DjangoSearchSet):
            class Meta:
                ululu = "ululu"

        self.assertTrue(hasattr(SearchSet, '_meta'))
        self.assertTrue(issubclass(SearchSet._meta, BaseMetaClass))

        expected_meta_fields = [
            "model", "show_suggestions", "escape_quotes_in_suggestions",
            "fields_to_exclude_from_mapping", "fields_to_exclude_from_suggestions", "ululu"]

        for field in expected_meta_fields:
            self.assertTrue(hasattr(SearchSet._meta, field))

    def test_default_fields_classa(self):
        class Mixin(metaclass=BaseSearchSetMetaClass):
            pass

        class SearchSet(Mixin, DjangoSearchSet):
            pass

        self.assertEqual(DjangoSearchSet._default_field, SearchSet._default_field)
        self.assertEqual(DjangoSearchSet._field_base_class, SearchSet._field_base_class)

    def test_searchsets_mixins(self):
        class SearchSetMixin(metaclass=BaseSearchSetMetaClass):
            mixinfield = DjangoCharField()

        self.assertTrue(hasattr(SearchSetMixin, "_meta"))
        self.assertTrue("mixinfield" in SearchSetMixin._meta._storage.field_name_to_field)

        class SearchSet(SearchSetMixin, DjangoSearchSet):
            searchsetfield = DjangoCharField()

            class Meta:
                model = EmptyDjangoModel

        expected_declared_fields = ["mixinfield", "searchsetfield"]
        for field in expected_declared_fields:
            self.assertTrue(field in SearchSet.storage.field_name_to_field, field)
        self.assertEqual(len(expected_declared_fields), len(SearchSet.storage.field_name_to_field))

        self.assertEqual(SearchSet.storage.field_name_to_field['mixinfield'].__class__, DjangoCharField)
