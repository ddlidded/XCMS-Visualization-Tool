"""Custom error classes for the application."""

class XCMSProcessingError(Exception):
    """Base exception for XCMS processing errors."""
    pass


class MS2ExtractionError(XCMSProcessingError):
    """Error during MS2 spectrum extraction."""
    pass


class LibraryParseError(XCMSProcessingError):
    """Error parsing spectral library."""
    pass


class MatchingError(XCMSProcessingError):
    """Error during spectral matching."""
    pass

