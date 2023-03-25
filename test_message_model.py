"""Message model tests."""

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Like

# Environmental variable for URL
os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

# Create tables: once for all tests
db.drop_all()
db.create_all()


class MessageModelTestCase(TestCase):
    def setUp(self):
        """Create demo data"""

        User.query.delete()

        u1 = User.signup(
            username="u1",
            email="u1@email.com",
            password="password",
            image_url=None
        )

        u2 = User.signup(
            username="u2",
            email="u2@email.com",
            password="password",
            image_url=None
        )

        m1 = Message(text="Sample text")
        u1.authored_messages.append(m1)
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.m1_id = m1.id

        self.client = app.test_client()

        # like = Like(user_id=self.u2_id, message_id=msg.id)
        # db.session.add(like)
        # db.session.commit()

        # self.like_id = like.id

    def tearDown(self):
        """Clean up fouled transactions"""

        db.session.rollback()

    ########################################################################
    # Message model tests

    def test_message_model(self):
        """Test message model with demo data"""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        # u1 should have 1 message
        self.assertEqual(len(u1.authored_messages), 1)
        self.assertEqual(u1.authored_messages[0].text, "Sample text")
        self.assertEqual(len(u2.authored_messages), 0)

    def test_message_model_invalid_message(self):
        """Test message without text fails to create message"""

        with self.assertRaises(ValueError):
            msg = Message(text="", user_id=self.u1_id)

            db.session.add(msg)
            db.session.commit()

    def test_message_model_invalid_author(self):
        """Test author who does not exist fails to create message"""

        with self.assertRaises(IntegrityError):
            msg = Message(text="Sample Text", user_id=1000)

            db.session.add(msg)
            db.session.commit()

    ########################################################################
    # authored_messages/author tests

    def test_message_author(self):
        """Test that message has the expected author"""

        m1 = Message.query.get(self.m1_id)
        u1 = User.query.get(self.u1_id)

        self.assertEqual(m1.author, u1)
        self.assertEqual(u1.authored_messages, [m1])

    # ########################################################################
    # # Test message and users_who_liked relationship

    # def test_message_users_who_liked_valid(self):
    #     """Test that a message has expected list of users who like"""

    #     msg = Message.query.filter_by(id=self.u1_msg_id).one()
    #     u2 = User.query.get(self.u2_id)

    #     self.assertEqual(msg.users_who_liked, [u2])

    # def test_message_users_who_liked_invalid(self):
    #     """
    #     Test that a message will not accept like from user who does not exist
    #     """

    #     with self.assertRaises(IntegrityError):
    #         like = Like(user_id=1000, message_id=self.u1_msg_id)
    #         db.session.add(like)
    #         db.session.commit()