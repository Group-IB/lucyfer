import warnings

warnings.warn(
    "Import from base dir will be deprecated in version 0.2.0, use lucyfer.backend.base import instead",
    DeprecationWarning
)

from ..backend import LuceneSearchFilter
