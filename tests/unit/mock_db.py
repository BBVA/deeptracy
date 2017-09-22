from contextlib import contextmanager

class MockQuery:
    _ret_val = None

    def __init__(self, model):
        self._model = model

    def get(self, id):
        return self._ret_val


class MockSession:
    query = MockQuery

    def close(self):
        pass


class MockDeeptracyDBEngine:

    engine = None
    Base = None
    Session = MockSession
    created_session = None
