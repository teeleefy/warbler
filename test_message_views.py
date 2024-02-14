"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""
    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        Likes.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        x = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        x.id=1000
        db.session.add(x)
        db.session.commit()
        msg2 = Message(
                    text = "Hola, como esta?",
                    user_id = 1000
        )
        msg2.id = 2
        db.session.add(msg2)
        db.session.commit()
        self.user2 = x
        self.msg2 = msg2

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.filter_by(user_id=self.testuser.id).first()
            self.assertEqual("Hello", msg.text)


    def test_delete_msg_illegally(self):
        '''Does it prevent you from deleting another user's message?'''
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/2/delete", follow_redirects=True)
            # Make sure it redirects
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(self.msg2.text, "Hola, como esta?")
            data = resp.data.decode("utf-8")
            self.assertIn("Access unauthorized. You cannot delete", data)
    
    def test_show_msg(self):
        '''Does the app show the message'''
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Good morning!"}, follow_redirects=True)
            data = resp.data.decode("utf-8")
            
            # Make sure it redirects
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Good morning!", data)
    
    def test_delete_msg_when_logged_out(self):
        '''Does it prevent you from deleting a message when logged out?'''
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/2/delete", follow_redirects=True)
            data = resp.data.decode("utf-8")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", data)

    def test_add_message_when_logged_out(self):
        """Can user add a message when logged out?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "What's up?"}, follow_redirects=True)
            data = resp.data.decode("utf-8")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", data)
          
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
