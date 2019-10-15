import warnings

warnings.warn(
    "Import from django dir will be deprecated in version 0.2.0, use lucyfer.searchset import instead",
    DeprecationWarning
)

from ..searchset import DjangoSearchSet
