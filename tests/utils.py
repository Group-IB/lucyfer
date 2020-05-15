from collections.abc import Mapping, Iterable


class Panic(Exception):
    pass


def compare_dicts(d1, d2):
    if not all(isinstance(d, dict) for d in [d1, d2]):
        raise Panic()

    sorted_d1_keys = sorted(d1)
    sorted_d2_keys = sorted(d2)

    if sorted_d1_keys != sorted_d2_keys:
        raise Panic()

    for k in sorted_d1_keys:
        if isinstance(d1[k], dict):
            compare_dicts(d1[k], d2[k])

        elif isinstance(d1[k], Iterable):
            if all(isinstance(v, dict) for v in d1[k]) and all(isinstance(v, dict) for v in d2[k]):
                dict_from_d1_values = dict()
                for v in d1[k]:
                    dict_from_d1_values = dict_merge(dict_from_d1_values, v)

                dict_from_d2_values = dict()
                for v in d2[k]:
                    dict_from_d2_values = dict_merge(dict_from_d2_values, v)

                compare_dicts(dict_from_d1_values, dict_from_d2_values)

            elif all(not isinstance(v, dict) for v in d1[k]) and all(not isinstance(v, dict) for v in d2[k]):
                if not sorted(d1[k]) == sorted(d2[k]):
                    raise Panic()
            else:
                raise Panic()
        else:
            if d1[k] != d2[k]:
                raise Panic()


def dict_merge(dct, merge_dct):
    """
    SOURCE: https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
    """
    dct = dct.copy()

    for k, v in merge_dct.items():
        if isinstance(dct.get(k), dict) and isinstance(v, Mapping):
            dct[k] = dict_merge(dct[k], v)
        else:
            dct[k] = v

    return dct


class ModelMeta:
    fields = []


class EmptyDjangoModel:
    _meta = ModelMeta()

    class objects:
        @classmethod
        def filter(cls, *args, **kwargs):
            return cls

        @classmethod
        def values_list(cls, *args, **kwargs):
            return cls

        @classmethod
        def distinct(cls):
            return []


class DjangoModel(EmptyDjangoModel):
    @classmethod
    def distinct(cls):
        return ["a", "b", "c"]


class Indicies:
    @staticmethod
    def get_mapping(*args, **kwargs):
        return None


class EsClient:
    indices = Indicies


class ElasticModel:
    @staticmethod
    def _get_index(*args, **kwargs):
        return "ululu"
