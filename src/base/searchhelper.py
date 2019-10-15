import warnings

warnings.warn(
    "Import from base dir will be deprecated in version 0.2.0, use lucyfer.searchhelper import instead",
    DeprecationWarning
)

from ..searchhelper.base import SearchHelperMixin
