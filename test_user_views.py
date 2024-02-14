"""User View tests."""

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


class UserViewTestCase(TestCase):
    """Test views for users."""
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

    def test_add_user(self):
        """Does the /signup route allow you to add a new user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                resp = c.post("/signup", data={
                                "username":"testuser3",
                                "email":"test3@test.com",
                                "password":"test3user"}, follow_redirects=True)
                data = resp.data.decode("utf-8")
                user3= User.query.filter_by(username = 'testuser3').first()
                sess[CURR_USER_KEY] = user3.id

            # Now, that session setting is saved, so we can have
            # the rest of our test
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser3", data)
            self.assertIn("Followers", data)

    def test_follow_a_user_when_not_logged_in(self):
        '''When not logged in, does the app prevent you from following someone?'''
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None
                resp = c.post("/users/follow/1000", follow_redirects=True)
            data = resp.data.decode("utf-8")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", data)
            self.assertIn("Sign up", data)

    def test_follow_a_user_when_logged_in(self):
        '''Can you follow a user when logged in?'''
        with self.client as c:
            with c.session_transaction() as sess:
                resp = c.post("/login", data={
                                "username":"testuser",
                                "password":"testuser"}, follow_redirects=True)
                sess[CURR_USER_KEY] = self.testuser.id
                resp = c.post("/users/follow/1000", follow_redirects=True)
                data = resp.data.decode("utf-8")
                self.assertEqual(resp.status_code, 200)
                self.assertIn("@testuser2", data)
                self.assertIn("Following", data)
                self.assertIn("Unfollow", data)

    def test_delete_user_illegally(self):
        """Does the app prevent someone from deleting a user when not logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                resp = c.post("/users/delete", follow_redirects=True)
                data = resp.data.decode("utf-8")
                
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", data)
            self.assertIn("Sign up", data)
        