import unittest

import main
from bot import configs


class TestConfig(unittest.TestCase):
    def test_load(self):
        self.assertIsInstance(configs.load(main.CONFIG_FILE), configs.Config)


if __name__ == '__main__':
    unittest.main()
