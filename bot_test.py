import unittest

from TOKENS import group_token, user_token
from vk_search import VkBot


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.bot1 = VkBot(group_token, user_token)

    def test_get_user_age(self):
        self.assertEqual(self.bot1.get_user_age('30.10.1990'), 30)

    def test_get_sex(self):
        self.assertEqual(self.bot1.get_sex('мужчина'), 2)

    def test_get_city(self):
        self.assertEqual(self.bot1.get_city('Йошкар-Ола'), '59')

if __name__ == '__main__':
    unittest.main()
