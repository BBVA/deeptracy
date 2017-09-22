import unittest
import os


class BaseDeeptracyTest(unittest.TestCase):
    """Base test class for tests suits

    Its ensure a valid environment is set before running
    each test."""

    def setUp(self):
        """Setup before each test is run"""
        # setup environment
        os.environ["REDIS_URI"] = "redis://localhost"
        os.environ["POSTGRES_URI"] = "sqlite:///:memory:"
        # load config

