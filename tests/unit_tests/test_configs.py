import json
import os
import unittest

import main
from bot import configs


class TestConfig(unittest.TestCase):
    def test_file_exists(self):
        self.assertTrue(os.path.isfile(main.CONFIG_FILE))

    def test_load(self):
        with open(main.CONFIG_FILE) as fin:
            config = json.load(fin)

        self.assertIsInstance(configs.load_config(config), configs.Config)


if __name__ == '__main__':
    unittest.main()
