import warnings

warnings.warn(
    "Import from base dir will be deprecated in version 0.2.0, use lucyfer.mapping import instead",
    DeprecationWarning
)

from ..mapping.base import Mapping, MappingValue
