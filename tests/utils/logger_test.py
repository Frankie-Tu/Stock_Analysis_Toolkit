import unittest

from scrappers.utils.logger import Logger


class LoggerTest(unittest.TestCase):
    def test(self):
        logger = Logger(__name__).get_logger()
        with self.assertLogs(logger) as cm:
            logger.info("test message")
        self.assertEqual(cm.output, ["INFO:{}:test message".format(__name__)])