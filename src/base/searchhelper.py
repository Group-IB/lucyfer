import warnings

warnings.warn(
    "Import from base dir will be deprecated in version 0.2.0, use lucyfer.searchset.searchhelper.base import instead",
    DeprecationWarning
)

from ..searchset.searchhelper.base import SearchHelperMixin
