from django.db.models import Q

from src.fields.base import BaseSearchField
from src.utils import LuceneSearchCastValueError


class DjangoSearchField(BaseSearchField):
    def get_query_by_condition(self, condition, ):
        if self.match_all(value=condition.value):
            return Q()

        return Q(**{"{}__{}".format(self.get_source(condition.name),
                                    self.get_operator_by_lookup(condition.operator)): self.cast_value(condition.value)})

    def get_query(self, field_name, lookup, value):
        if self.match_all(value=value):
            return Q()

        return Q(**{"{}__{}".format(self.get_source(field_name), lookup): self.cast_value(value)})

    def match_all(self, value):
        return value == "*"

    def cast_value(self, value):
        return value

    def get_operator_by_lookup(self, operator):
        # TODO ANN
        return None


class CharField(DjangoSearchField):
    def get_query(self, field_name, lookup, value):
        if self.match_all(value=value):
            return Q()

        source = self.get_source(field_name)
        wildcard_parts = self.cast_value(value).split("*")

        parts_count = len(wildcard_parts)

        if parts_count == 1:
            return Q(**{"{}__icontains".format(source): wildcard_parts[0]})

        query = Q()
        for index, w_part in enumerate(wildcard_parts):
            if w_part:
                if index == 0:
                    query = query & Q(**{"{}__{}".format(source, "istartswith"): w_part})
                    continue

                elif index == (parts_count - 1):
                    query = query & Q(**{"{}__{}".format(source, "iendswith"): w_part})
                    continue

                else:
                    query = query & Q(**{"{}__{}".format(source, "icontains"): w_part})
                    continue

        return query

    def cast_value(self, value):
        return value.strip().strip('\"').strip("\'")


class IntegerField(DjangoSearchField):
    def cast_value(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            raise LuceneSearchCastValueError()


class FloatField(DjangoSearchField):
    def cast_value(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            raise LuceneSearchCastValueError()


class BooleanField(DjangoSearchField):
    _values = {"true": True, "false": False}

    def get_query(self, field_name, lookup, value):
        if self.match_all(value=value):
            return Q()

        return Q(**{self.get_source(field_name): self.cast_value(value)})

    def cast_value(self, value):
        value = value.lower()
        if value in self._values:
            return self._values[value]

        raise LuceneSearchCastValueError()


class NullBooleanField(BooleanField):
    _values = {"true": True, "false": False, "null": None}
