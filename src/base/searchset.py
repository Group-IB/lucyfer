import warnings

warnings.warn(
    "Import from base dir will be deprecated in version 0.2.0, use lucyfer.searchset.base import instead",
    DeprecationWarning
)

from ..searchset.base import BaseSearchSet
