import warnings

warnings.warn(
    "Import from django dir will be deprecated in version 0.2.0, use lucyfer.searchset.mapping import instead",
    DeprecationWarning
)

from ..searchset.mapping import DjangoMappingValue, DjangoMapping
