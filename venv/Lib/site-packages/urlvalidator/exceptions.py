NON_FIELD_ERRORS = '__all__'


class ValidationError(Exception):
    """An error while validating data."""
    def __init__(self, message, code=None, params=None):
        """
        The `message` argument can be a single error, a list of errors, or a
        dictionary that maps field names to lists of errors. What we define as
        an "error" can be either a simple string or an instance of
        ValidationError with its message attribute set, and what we define as
        list or dictionary can be an actual `list` or `dict` or an instance
        of ValidationError with its `error_list` or `error_dict` attribute set.
        """

        # PY2 can't pickle naive exception: http://bugs.python.org/issue1692335.
        super().__init__(message, code, params)

        self.message = message
        self.code = code
        self.params = params
        self.error_list = [self]


class EmptyResultSet(Exception):
    """A database query predicate is impossible."""
    pass
