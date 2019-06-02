# project/test_users.py

import unittest

from project import app

class ProjectTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # Execute prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

        self.assertEquals(app.debug, False)

    # Executed after each test
    def tearDown(self):
        pass
    

    ###############
    #### tests ####
    ###############

    def test_main_page(self):
        response = self.app.get('/login', follow_redirects=True)
        self.assertIn(b'Future site for logging into Lelis Family Recipe App', response.data)

