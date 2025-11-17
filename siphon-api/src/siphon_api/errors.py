# General Siphon errors
class SiphonClientError(Exception):
    pass


class SiphonServerError(Exception):
    pass


# Pipeline classes
class SiphonParserError(Exception):
    pass


class SiphonExtractorError(Exception):
    pass


class SiphonEnricherError(Exception):
    pass


# Source-specific
class ArticleCacheError(Exception):
    pass
