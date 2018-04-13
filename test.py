import unittest
from base64 import b64encode
from playhouse.test_utils import test_database
from peewee import *

from app import app
from models import User, Todo

# creating a disposable database
db = SqliteDatabase(':memory:')
db.connect()
db.create_tables([User, Todo], safe=True)

# provides basic authorization
headers = {
    'Authorization': 'Basic ' + b64encode('user_one:password1'.
                                          encode()).decode()
          }


class InheritTestClient(unittest.TestCase):
    """Will be used as an inheritor for other classes"""
    def setUp(self):
        """enables to play with database"""
        app.config['TESTING'] = True 
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()


class HomepageView(InheritTestClient):
    """Tests the '/' view"""
    def test_h1_appears(self):
        """tests that the homepage shows, with its <h1>"""
        html = self.app.get('/')
        self.assertIn('My TODOs!', html.get_data(as_text=True))


class UserModelTest(unittest.TestCase):
    """tests if can create a User instance, while blocking duplicates"""
    def test_create_user_instance(self):
        with test_database(db, (User,)):
            User.create_user(
                username='user_one',
                email='user_one@gmail.com',
                password='password1'
                )
            self.assertEqual(
                User.select().get().username, 'user_one'
                )
            with self.assertRaises(Exception):
                User.create_user(
                username='user_one',
                email='user_one@gmail.com',
                password='password1'
                )


class TodoModelTest(unittest.TestCase):
    """tests that we can create a Todo instance"""
    def test_create_todo_instance(self):
        with test_database(db, (Todo,)):
            Todo.create(
                name="todo1"
                )
            self.assertEqual(
                Todo.select().get().name, 'todo1'
                )


class ResourcesTodosTestWithoutUser(InheritTestClient):
    """tests that we can't create a Todo if not logged in"""
    def test_TodoList_cannot_receive_POST_without_User(self):
        with test_database(db, (Todo,)):
            false_todo = self.app.post('/api/v1/todos', data={'name': 'todo1'})
            self.assertFalse(Todo.select().count())


class ResourcesTodosTestWithUser(InheritTestClient): 
    """tests all of TodoList and Todo apis when logged in"""
    def test_TodoList_can_receive_POST_with_User(self):
        with test_database(db, (Todo, User)):
            User.create_user(
                username='user_one',
                email='user_one@gmail.com',
                password='password1'
                )
            # a todo is created through post on TodoList api
            todo = self.app.post(
                '/api/v1/todos', headers=headers, data={'name': 'todo1'}
                )
            self.assertEqual(Todo.select().count(), 1)
            self.assertEqual(
                Todo.select().get().name, 'todo1'
                )
            # that todo is changed through 'PUT' on the Todo api
            todo = self.app.put(
                '/api/v1/todos/1', headers=headers, data={'name': 'todo1updated'}
                )
            self.assertEqual(
                Todo.select().get().name, 'todo1updated'
                )
            # testing that the 'GET' works on TodoList api
            html = self.app.get('/api/v1/todos')
            self.assertIn('todo1updated', html.get_data(as_text=True))
            # testing that the 'GET' works on the Todo api
            html = self.app.get('/api/v1/todos/1')
            self.assertIn('todo1updated', html.get_data(as_text=True))
            # testing that the 'DELETE' works on the Todo api
            todo = self.app.delete(
                '/api/v1/todos/1', headers=headers, data={'name': 'todo1updated'}
                )
            self.assertFalse(Todo.select().count())


class ResourcesUsersTest(InheritTestClient):
    # tests that we can create a user, but only if password verifcation matches.
    def test_User_create_fail(self):
        """verify_password doesn't match, should fail"""
        with test_database(db, (User,)):
            self.app.post('/api/v1/users', data={
                'username': 'user_one',
                'password': 'password1',
                'verify_password': 'password2',
                'email': 'user_one@gmail.com'
                })
            self.assertFalse(User.select().count())

    def test_User_create_success(self):
        """verify_password matches. Should succeed."""
        with test_database(db, (User,)):
            self.app.post('/api/v1/users', data={
                'username': 'user_one',
                'password': 'password1',
                'verify_password': 'password1',
                'email': 'user_one@gmail.com'
                })
            self.assertTrue(User.select().count())

if __name__ == '__main__':
    unittest.main()