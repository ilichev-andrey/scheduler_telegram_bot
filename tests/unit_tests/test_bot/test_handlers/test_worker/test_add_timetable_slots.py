import datetime
import unittest
from collections import OrderedDict

from bot.handlers.worker import add_timetable_slots


class TestHandleDates(unittest.TestCase):
    def test_generate_times(self):
        # Тестирование функции, которая генерирует список времен с определенным шагом

        cases = [
            OrderedDict({
                'start_tm': datetime.time(10, 31),
                'end_tm': datetime.time(13, 29),
                'step': 30,
                'expected': {
                    '11:00': datetime.time(11),
                    '11:30': datetime.time(11, 30),
                    '12:00': datetime.time(12),
                    '12:30': datetime.time(12, 30),
                    '13:00': datetime.time(13)
                }
            })
        ]

        for case in cases:
            start_tm, end_tm, step, expected = case.values()
            self.assertEqual(expected, add_timetable_slots._generate_times(start_tm, end_tm, step))


if __name__ == '__main__':
    unittest.main()
