from src.base.mapping import MappingValue, Mapping


class DjangoMappingValue(MappingValue):
    def _get_values(self, model, prefix):
        # todo rewrite it for one request
        result = []
        for source in self.sources:
            result.extend(list(model.objects.filter(**{'{}__icontains'.format(source): prefix}).
                               values_list(source, flat=True).distinct()))
        return list(set(result))


class DjangoMapping(Mapping):
    _value_class = DjangoMappingValue
