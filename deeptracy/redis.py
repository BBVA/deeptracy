from redis import StrictRedis
from urllib.parse import urlparse
from deeptracy.config import BROKER_URI


class DeeptracyRedis:
    client = None

    def set_up(self):
        _, netloc, path, _, _, _ = urlparse(BROKER_URI)

        host, port = netloc.split(":", maxsplit=1)

        if not path:
            path = 0

        self.client = StrictRedis(host=host, port=port, db=path)


redis = DeeptracyRedis()
