# project/test_users.py

import os
import unittest

from project import app, db, mail

TEST_DB  = 'user.db'


class UserTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # Execute prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+\
            os.path.join(app.config['BASEDIR'], TEST_DB)
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

        mail.init_app(app)

        self.assertEquals(app.debug, False)
    
    ########################
    #### Helper methods ####
    ########################

    def register(self, email, password, confirm):
        return self.app.post(
            'register',
            data=dict(email=email,  password=password, confirm=confirm),
            follow_redirects=True
        )
    
    def login(self, email, password):
        return self.app.post(
            '/login',
            data=dict(email=email, password=password),
            follow_redirects=True
        )

    # Executed after each test
    def tearDown(self):
        pass
    

    ###############
    #### tests ####
    ###############

    # def test_main_page(self):
    #     response = self.app.get('/', follow_redirects=True)
    #     self.assertIn(b'Lelis Family Recipes', response.data)
    #     self.assertIn(b'Register', response.data)
    #     self.assertIn(b'Log In', response.data)

    def test_user_registration_form_displays(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please Register Your New Account', response.data)
    
    def test_valid_user_registration(self):
        self.app.get('/register', follow_redirects=True)
        response = self.register('ricardo.lelis3@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
        self.assertIn(b'Thanks for registering!', response.data)
    
    def test_duplicate_email_user_registration_error(self):
        self.app.get('/register', follow_redirects=True)
        self.register('ricardo.lelis3@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
        self.app.get('/register', follow_redirects=True)
        response =  self.register('ricardo.lelis3@gmail.com', 'FlaskIsAwesome123', 'FlaskIsAwesome123')
        self.assertIn(b'ERROR! Email (ricardo.lelis3@gmail.com) already exists', response.data)
    
    def test_missing_field_user_registration_error(self):
        self.app.get('/register', follow_redirects=True)
        response =  self.register('ricardo.lelis3@gmail.com', 'FlaskIsAwesome', '')
        self.assertIn(b'This field is required', response.data)
    
    def test_login_form_displays(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Log In', response.data)
    
    def test_valid_login(self):
        self.app.get('/register', follow_redirects=True)
        self.register('ricardo.lelis3@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
        self.app.get('/login', follow_redirects=True)
        response = self.login('ricardo.lelis3@gmail.com', 'FlaskIsAwesome')
        self.assertIn(b'Welcome, ricardo.lelis3@gmail.com', response.data)
    
    def test_login_without_registration(self):
        self.app.get('/login', follow_redirects=True)
        response = self.login('ricardo.lelis3@gmail.com', 'FlaskIsAwesome')
        self.assertIn(b'ERROR! Incorrect login credentials.', response.data)
    
    def test_valid_logout(self):
        self.app.get('/register', follow_redirects=True)
        self.register('ricardo.lelis3@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
        self.app.get('/login', follow_redirects=True)
        self.login('ricardo.lelis3@gmail.com', 'FlaskIsAwesome')
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'Goodbye!', response.data)
    
    def test_invalid_logout_within_being_logged_in(self):
        response  = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'Log In', response.data)
    
    def test_user_profile_page(self):
        self.app.get('/register', follow_redirects=True)
        self.register('ricardo.lelis3@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
        response = self.app.get('/user_profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email Address', response.data)
        self.assertIn(b'Account Actions', response.data)
        self.assertIn(b'Statistics', response.data)
        self.assertIn(b'First time logged in. Welcome!', response.data)
 
    def test_user_profile_page_after_logging_in(self):
        self.app.get('/register', follow_redirects=True)
        self.register('ricardo.lelis3@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
        self.app.get('/logout', follow_redirects=True)
        self.login('ricardo.lelis3@gmail.com', 'FlaskIsAwesome')
        response = self.app.get('/user_profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email Address', response.data)
        self.assertIn(b'Account Actions', response.data)
        self.assertIn(b'Statistics', response.data)
        self.assertIn(b'Last Logged In: ', response.data)
    
    def test_user_profile_without_logging_in(self):
        response = self.app.get('/user_profile')
        self.assertEqual(response.status_code, 302)
        self.assertIn(b'You should be redirected automatically to target URL:', response.data)
        self.assertIn(b'/login?next=%2Fuser_profile', response.data)
        
