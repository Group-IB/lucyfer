import warnings

warnings.warn(
    "Import from django dir will be deprecated in version 0.2.0, use lucyfer.fields import instead",
    DeprecationWarning
)

from ..fields.django import *
