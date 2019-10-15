import warnings

warnings.warn(
    "Import from base dir will be deprecated in version 0.2.0, use lucyfer.searchset.mapping.base import instead",
    DeprecationWarning
)

from ..searchset.mapping.base import *
