class Error(Exception):
    """Base class for other exceptions"""
    pass


class PiastrixGeneralError(Error):
    pass


class PiasrixResponceError(Error):

    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code
