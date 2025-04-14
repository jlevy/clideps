class ClidepsError(RuntimeError):
    """
    Base class for all errors in clideps.
    """


class CommandFailed(ClidepsError):
    """
    Raised for fatal errors.
    """

    def __init__(self, message: str = "Operation failed"):
        super().__init__(message)


class CommandCancelled(ClidepsError):
    """
    Raised for cancelled operations.
    """


class NotSupportedError(ClidepsError):
    """
    Error raised when OS or terminal doesn't support the operation.
    """


class PkgMissing(ClidepsError):
    """
    Exception raised when a required external package is missing.
    """
