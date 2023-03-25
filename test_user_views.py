"""User view function tests."""

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Like
from app import CURR_USER_KEY

# Environmental variable for URL
os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

# Don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Don't require CSRF for testing
app.config['WTF_CSRF_ENABLED'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# Create tables: once for all tests
db.drop_all()
db.create_all()


class UserRoutesTestCase(TestCase):
    def setUp(self):
        """Create demo data"""

        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions"""

        db.session.rollback()

    ########################################################################
    # do login/logout function tests

    # test do login yes

    # test do login no

    # test do logout yes

    ########################################################################
    # Signup route tests

    # visit signup & signup with curr user key in session

    # signup no curr user key in session

    # form validates with valid data, logs user in, redirects to /

    # form validates with invalid data (username or email not unique),
    #   renders data typed with error message

    # form doesn't validate, renders signup template

    ########################################################################
    # Login route tests

    # form validates and authenticates

    # form validates, does not authenticate

    # form does not validate

    ########################################################################
    # Logout route tests

    # g.user in session, form validates, logs out, redirects to login

    # form validates but user not in session

    # form does not validate, flash unauth, redirect to homepage /

    ########################################################################
    # /users route tests

    def test_list_users(self):
        """Test /users page that lists all users"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = client.get("/users")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("u2", html)


    def test_show_user(self):
        """Test page showing user profile"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = client.get(f"/users/{self.u1_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("u1", html)
            self.assertIn("<!-- Test: show page -->", html)


    def test_show_following_logged_in(self):
        """Test page showing people user is following if logged in"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = client.get(f"/users/{self.u1_id}/following")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- Test: following page -->", html)


    def test_show_following_logged_out(self):
        """Test following page is blocked if not logged in"""

        with app.test_client() as client:
            resp = client.get(
                f"/users/{self.u1_id}/following",
                follow_redirects=True
            )
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- Test: home-anon page -->", html)

    def test_show_followers_logged_in(self):
            """Test page showing people following user if logged in"""

            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1_id
                resp = client.get(f"/users/{self.u1_id}/followers")
                html = resp.get_data(as_text=True)
                self.assertEqual(resp.status_code, 200)
                self.assertIn("<!-- Test: followers page -->", html)


    def test_show_followers_logged_out(self):
        """Test followers page is blocked if not logged in"""

        with app.test_client() as client:
            resp = client.get(
                f"/users/{self.u1_id}/followers",
                follow_redirects=True
            )
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- Test: home-anon page -->", html)

    def test_start_following_logged_in(self):
        """Test following a person if user is logged in"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = client.post(f"/users/follow/{self.u2_id}")
            u1 = User.query.get(self.u1_id)
            u2 = User.query.get(self.u2_id)
            self.assertEqual(u2.followers, [u1])

