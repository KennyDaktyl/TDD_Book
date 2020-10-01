from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import unittest
import time


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox(
            executable_path=r'/usr/local/bin/geckodriver')
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')

        self.assertIn(row_text, [row.text for row in rows])

    def test_can_start_a_list_and_retrieve_it_later(self):
        self.browser.get(self.live_server_url)

        self.assertIn('Listy rzeczy do zrobienia', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Utwórz nową listę rzeczy do zrobienia', header_text)
        # time.sleep(3)

        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Kupić pawie pióra')
        inputbox.send_keys(Keys.ENTER)
        time.sleep(2)
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/(.+)')

        WebDriverWait(self.browser, 10).until(
            expected_conditions.text_to_be_present_in_element(
                (By.ID, 'id_list_table'), 'Kupić pawie pióra'))
        # self.assertRegex(edith_list_url, '/lists/the-only-list-in-the-world/')
        self.browser.quit()

        self.browser = webdriver.Firefox()
        self.browser.get(self.live_server_url)
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Użyć pawich piór do zrobienia przynęty')
        inputbox.send_keys(Keys.ENTER)

        WebDriverWait(self.browser, 10).until(
            expected_conditions.text_to_be_present_in_element(
                (By.ID, 'id_list_table'),
                'Użyć pawich piór do zrobienia przynęty'))
        self.browser.quit()

        self.browser = webdriver.Firefox()
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Kupić nowe pióra', page_text)
        self.assertNotIn('Zrobienia przynęty', page_text)

        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Kupić mleko')
        inputbox.send_keys(Keys.ENTER)
        time.sleep(2)
        francis_list_url = self.browser.current_url

        self.assertRegex(francis_list_url, '/lists/(.+)')
        self.assertNotEqual(francis_list_url, edith_list_url)

        self.check_for_row_in_list_table('1: Kupić pawie pióra')
        self.check_for_row_in_list_table(
            '2: Użyć pawich piór do zrobienia przynęty')

        # time.sleep(3)
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn('1: Kupić pawie pióra', [row.text for row in rows])
        self.assertIn('2: Użyć pawich piór do zrobienia przynęty',
                      [row.text for row in rows])

        self.fail('Zakończenie testu')


if __name__ == '__main__':
    unittest.main(warnings='ignore')
