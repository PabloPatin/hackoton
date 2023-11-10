class AuthorisationError(Exception):
    def __init__(self, msg: str, ex: Exception = None):
        self.msg = msg
        self.ex = ex

    def __repr__(self):
        return self.msg + '\n' + str(self.ex)


class HttpRequestError(Exception):
    def __init__(self, msg: str, ex: Exception = None):
        self.msg = msg
        self.ex = ex

    def __repr__(self):
        return self.msg + '\n' + str(self.ex)
