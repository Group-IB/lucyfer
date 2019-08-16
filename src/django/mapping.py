from src.base.mapping import MappingValue, Mapping


class DjangoMappingValue(MappingValue):
    def _get_values(self, model, prefix):
        return list(model.objects.filter(**{'{}__icontains'.format(self.name): prefix}).values_list(self.name,
                                                                                                    flat=True).distinct())


class DjangoMapping(Mapping):
    _value_class = DjangoMappingValue
