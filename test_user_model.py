"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py
import os
from unittest import TestCase
from sqlalchemy import exc 
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

class UserModelTestCase(TestCase):
    """Test user model."""

    def setUp(self):
        """Create test client, add sample data."""

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
        self.user1 = u
        self.user2 = x
        self.id1 = u.id
        self.id2= x.id
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        
        # User should have no messages & no followers
        self.assertEqual(len(self.user1.messages), 0)
        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user2.messages), 0)
        self.assertEqual(len(self.user2.followers), 0)
        self.assertIn("testuser, test@test.com>", repr(self.user1))
        self.assertIn("testuser2, test2@test.com>", repr(self.user2))

    def test_follow(self):
        """Does User follow method work?"""
        self.user1.following.append(self.user2)
        db.session.commit()
        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))
        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))

    def test_user_signup_method(self):
        """Does basic model work?"""

        z = User.signup(
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD"
        )
        
        db.session.add(z)
        db.session.commit()
        
        # User should have no messages & no followers
        self.assertEqual(len(z.messages), 0)
        self.assertEqual(len(z.followers), 0)
        self.assertIn("testuser3, test3@test.com>", repr(z))
        self.assertIsInstance(z.id, int)
        self.assertTrue(z.password.startswith("$2b$"))

    def test_unique_username_and_email(self):
        """Does basic model work?"""

        w = User.signup(
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD"
        )

        z = User.signup(
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD"
        )
        
        db.session.add(w)
        db.session.add(z)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test@test.com", "password")
        invalid.id = 3100
        db.session.add(invalid)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User(username = 'testuser9', email = 'asdf', password = "password")
        db.session.add(invalid)
        db.session.commit()
        self.assertRaises(ValueError)
            

    def test_invalid_password_signup(self):
        invalid = User(username ='testuser99', email = 'testing@testing.com', password="")
        db.session.add(invalid)
        db.session.commit()
        self.assertRaises(ValueError)
            
            
#=============================================================================
    def test_valid_authentication(self):
        m = User.signup(
            email="testm@test.com",
            username="testuserm",
            password="cottoncandy"
        )
        db.session.add(m)
        db.session.commit()
        a = User.authenticate('testuserm', "cottoncandy")
        self.assertIsNotNone(a)
        self.assertIsInstance(a.id, int)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("yomama", "hello123"))

    def test_wrong_password(self):
        m = User.signup(
            email="testdude@test.com",
            username="testdude",
            password="testingdude"
        )
        db.session.add(m)
        db.session.commit()
        self.assertFalse(User.authenticate(m.username, "dkl;sajflk;daj;lj"))
        self.assertTrue(User.authenticate('testdude', 'testingdude'))


