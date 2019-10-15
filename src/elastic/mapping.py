import warnings

warnings.warn(
    "Import from elastic dir will be deprecated in version 0.2.0, use lucyfer.mapping import instead",
    DeprecationWarning
)

from ..mapping import ElasticMapping, ElasticMappingValue
