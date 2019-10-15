import warnings

warnings.warn(
    "Import from base dir will be deprecated in version 0.2.0, use lucyfer.parser.base import instead",
    DeprecationWarning
)

from ..parser.base import BaseLuceneParserMixin
