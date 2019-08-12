from src.base.searchset import BaseSearchSet
from src.django.fields import DjangoSearchField
from src.django.parser import LuceneToDjangoParserMixin


class DjangoSearchSet(LuceneToDjangoParserMixin, BaseSearchSet):
    _field_base_class = DjangoSearchField
