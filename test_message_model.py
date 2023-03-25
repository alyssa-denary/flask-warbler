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

        m1 = Message(text="Sample Text")
        u1.messages.append(m1)
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id

        like = Like(user_id=self.u2_id, message_id=msg.id)
        db.session.add(like)
        db.session.commit()

        self.u1_msg_id = msg.id
        self.like_id = like.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    ########################################################################
    # Test message model

    ########################################################################
    # Test message and author relationship

    def test_message_author_valid(self):
        """Test that message has only the expected author"""

        msg = Message.query.filter_by(id=self.u1_msg_id).one()

        self.assertEqual(msg.author.id, self.u1_id)

    def test_message_author_invalid(self):
        """Test that message will not accept author who does not exist"""

        with self.assertRaises(IntegrityError):
            #create new message instance with user id that doesnt exist
            msg = Message(text="Sample Text", user_id=1000)

            db.session.add(msg)
            db.session.commit()


    ########################################################################
    # Test message and users_who_liked relationship

    def test_message_users_who_liked_valid(self):
        """Test that a message has expected list of users who like"""

        msg = Message.query.filter_by(id=self.u1_msg_id).one()
        u2 = User.query.get(self.u2_id)

        self.assertEqual(msg.users_who_liked, [u2])

    def test_message_users_who_liked_invalid(self):
        """
        Test that a message will not accept like from user who does not exist
        """

        with self.assertRaises(IntegrityError):
            like = Like(user_id=1000, message_id=self.u1_msg_id)
            db.session.add(like)
            db.session.commit()