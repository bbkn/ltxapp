from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='Susan')
        u.set_password('Susan')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('Susan'))

    def test_avatar(self):
        pass

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u2.followed.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followed.count(), 0)

    def test_follow_posts(self):
        #create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1,u2,u3,u4])

        #crate four posts
        now = datetime.utcnow()
        p1 = Post(body="post from john", author=u1,
                timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2,
                timestamp=now + timedelta(seconds=2))
        p3 = Post(body="post from mary", author=u3,
                timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4,
                timestamp=now + timedelta(seconds=4))
        db.session.add_all([p1,p2,p3,p4])
        db.session.commit()

        #setup followers
        u1.follow(u2) # john -> susan
        u1.follow(u4) # john -> david
        u2.follow(u3) # susan -> mary
        u3.follow(u4) # mary -> david
        db.session.commit()

        #check the followed posts of each user

        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p4, p2, p1])
        self.assertEqual(f2, [p3, p2])
        self.assertEqual(f3, [p4, p3])
        self.assertEqual(f4, [p4])

if __name__ == '__main__':
    unittest.main(verbosity=2)




