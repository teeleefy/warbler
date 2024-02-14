"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class MessageModelTestCase(TestCase):
    """Test Message Model."""

    def setUp(self):
        """Create test client, add sample data."""
        #empty databases of test data
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        Likes.query.delete()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        x = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        

        u.id= 999
        x.id=1000

        db.session.add(u)
        db.session.add(x)
        db.session.commit()
        msg = Message(
                    text = "Hello, hi, how are ya?",
                    user_id = 999
        )
        msg2 = Message(
                    text = "Hola, como esta?",
                    user_id = 1000
        )
        db.session.add(msg)
        db.session.add(msg2)
        db.session.commit()
        self.user1 = u
        self.user2 = x
        self.id1 = u.id
        self.id2= x.id
        self.msg = msg
        self.msg2 = msg2
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_msg_model(self):
        """Does basic model work?"""

        # Users should have one message each
        self.assertEqual(len(self.user1.messages), 1)
        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user2.messages), 1)
        self.assertEqual(len(self.user2.followers), 0)
        self.assertEqual(self.msg.user, self.user1)
        self.assertEqual(self.msg2.user, self.user2)

    def test_like_msgs(self):
        """Does the like function work?"""
        new_like = Likes(user_id=self.id1, message_id=self.msg2.id)
        new_like2 = Likes(user_id=self.id2, message_id=self.msg.id)
        db.session.add(new_like)
        db.session.add(new_like2)
        db.session.commit()
        self.assertIn(self.msg2, self.user1.likes)
        self.assertIn(self.msg, self.user2.likes)

    def test_cascade_delete(self):
        """Does cascade on delete function work? When message is deleted, is like relationship deleted?"""
        new_like = Likes(user_id=self.id1, message_id=self.msg2.id)
        new_like2 = Likes(user_id=self.id2, message_id=self.msg.id)
        db.session.add(new_like)
        db.session.add(new_like2)
        db.session.commit()
        db.session.delete(self.msg)
        db.session.commit()
        self.assertEqual(len(self.user1.messages), 0)
        self.assertNotIn(self.msg, self.user2.likes)
