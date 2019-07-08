class FindItEngineResponse(object):
    """ standard response for engine """

    def __init__(self):
        self._content = dict()
        self._brief = dict()

    def append(self, key, value, important: bool = None):
        if important:
            self._brief[key] = value
        self._content[key] = value

    def get_brief(self) -> dict:
        return self._brief

    def get_content(self) -> dict:
        return self._content


class FindItEngine(object):
    def get_type(self):
        return self.__class__.__name__

    def execute(self, *_, **__) -> FindItEngineResponse:
        """ MUST BE IMPLEMENTED """
        raise NotImplementedError("this function must be implemented")
