class ApiError(Exception):
    status_code = 500

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ValidationError(ApiError):
    status_code = 400


class NotFoundError(ApiError):
    status_code = 404


class AuthError(ApiError):
    status_code = 401
