"""User model tests."""

import os
from sqlalchemy.exc import IntegrityError
from unittest import TestCase
from flask_bcrypt import Bcrypt

from models import db, User

# Environmental variable for URL
os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

# instantiate Bcrypt to create hashed passwords for test data
bcrypt = Bcrypt()

# Create tables: once for all tests
db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        hashed_password = (bcrypt
            .generate_password_hash("password")
            .decode('UTF-8')
        )

        u1 = User(
            username="u1",
            email="u1@email.com",
            password=hashed_password,
            image_url=None
        )

        u2 = User(
            username="u2",
            email="u2@email.com",
            password=hashed_password,
            image_url=None
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    ########################################################################
    # User model tests

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.authored_messages), 0)
        self.assertEqual(len(u1.followers), 0)

    ########################################################################
    # is_following tests

    def test_is_following_yes(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        u2.followers.append(u1)

        # u1 should be following u2
        self.assertTrue(u1.is_following(u2))

    def test_is_following_no(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        # u1 should not be following u2
        self.assertFalse(u1.is_following(u2))

    ########################################################################
    # Following/Followers tests

    def test_followers_following(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.followers.append(u2)
        db.session.commit()

        self.assertEqual(u1.followers, [u2])
        self.assertEqual(u1.following, [])
        self.assertEqual(u2.followers, [])
        self.assertEqual(u2.following, [u1])

    def test_is_followed_by(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.followers.append(u2)
        db.session.commit()

        self.assertTrue(u1.is_followed_by(u2))
        self.assertFalse(u1.is_following(u2))

    def test_is_following(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.followers.append(u2)
        db.session.commit()

        self.assertTrue(u2.is_following(u1))
        self.assertFalse(u1.is_following(u2))

    ########################################################################
    # User.signup tests

    def test_user_signup_valid(self):
        new_user = User.signup(
            username="new_user",
            email="new_user@email.com",
            password="password",
            image_url=None
        )

        db.session.commit()

        new_user = User.query.get(new_user.id)

        self.assertEqual(new_user.username, "new_user")
        self.assertEqual(new_user.email, "new_user@email.com")
        self.assertNotEqual(new_user.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(new_user.password.startswith("$2b$"))

    def test_user_signup_invalid_same_username(self):
        """Test trying to create user with existing username"""

        with self.assertRaises(IntegrityError):
            User.signup(
                username="u1",
                email="u3@mail.com",
                password="password",
                image_url=None
            )
            db.session.commit()

    def test_user_signup_invalid_same_email(self):
        """Test trying to create user with existing email"""

        with self.assertRaises(IntegrityError):
            User.signup(
                username="u3",
                email="u1@email.com",
                password="password",
                image_url=None
            )
            db.session.commit()

    def test_user_signup_invalid_no_pw(self):
        """Test trying to create user with no password"""

        with self.assertRaises(ValueError):
            User.signup(
                username="u3",
                email="u3@email.com",
                password=None,
                image_url=None
            )
            db.session.commit()

    ########################################################################
    # User.authenticate tests

    def test_user_authenticate_valid(self):
        """Test successful return of user with correct username and password"""

        u1_db = User.query.get(self.u1_id)
        u1_authenticate = User.authenticate(username="u1", password="password")

        self.assertEqual(u1_db, u1_authenticate)

    def test_user_authenticate_invalid_username(self):
        """Test that invalid username fails to authenticate"""

        self.assertFalse(
            User.authenticate(username="baduser", password="password")
        )

    def test_user_authenticate_invalid_password(self):
        """Test that invalid password fails to authenticate"""

        self.assertFalse(
            User.authenticate(username="u1", password="badpassword")
        )