import unittest

from base64 import b64encode
from playhouse.test_utils import test_database
from peewee import *

from app import app
from models import User, Todo

db = SqliteDatabase(':memory:')
db.connect()
db.create_tables([User, Todo], safe=True)

headers = {
    'Authorization': 'Basic ' + b64encode('user_one:password1'.
                                          encode()).decode()
          }


class InheritTestClient(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True 
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()


# *****test the '/' view
# test that the header pops up
class HomepageView(InheritTestClient):

    def test_h1_appears(self):
        html = self.app.get('/')
        self.assertIn('My TODOs!', html.get_data(as_text=True))




# *****test the User model
# test that it saves a User instance
# test that it doesn't accept duplicates
class UserModelTest(unittest.TestCase):
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



# *****test the Todo model
# test that it saves properly with correct 'name'.
class TodoModelTest(unittest.TestCase):
    def test_create_todo_instance(self):
        with test_database(db, (Todo,)):
            Todo.create(
                name="todo1"
                )
            self.assertEqual(
                Todo.select().get().name, 'todo1'
                )



# ****test the todos api
# Test that the TodoList can't receive a 'POST' unless signed in
# For TodoList make a 'POST' of a todo instance then....
# test that the TodoList can 'GET' the saved Todo instance
# test that the Todo can 'GET' an individual todo instance
# test that the Todo can 'PUT' an individual todo instance
# test that the Todo can 'DELETE' and individual todo instance
class ResourcesTodosTestWithoutUser(InheritTestClient):

    def test_TodoList_cannot_receive_POST_without_User(self):
        with test_database(db, (Todo,)):
            false_todo = self.app.post('/api/v1/todos', data={'name': 'todo1'})
            self.assertFalse(Todo.select().count())

class ResourcesTodosTestWithUser(InheritTestClient): 

    def test_TodoList_can_receive_POST_with_User(self):
        with test_database(db, (Todo, User)):
            User.create_user(
                username='user_one',
                email='user_one@gmail.com',
                password='password1'
                )
            todo = self.app.post('/api/v1/todos', headers=headers, data={'name': 'todo1'})
            self.assertEqual(Todo.select().count(), 1)
            self.assertEqual(
                Todo.select().get().name, 'todo1'
                )
            todo = self.app.put('/api/v1/todos/1', headers=headers, data={'name': 'todo1updated'})
            self.assertEqual(
                Todo.select().get().name, 'todo1updated'
                )
            html = self.app.get('/api/v1/todos')
            self.assertIn('todo1updated', html.get_data(as_text=True))

            html = self.app.get('/api/v1/todos/1')
            self.assertIn('todo1updated', html.get_data(as_text=True))

            todo = self.app.delete('/api/v1/todos/1', headers=headers, data={'name': 'todo1updated'})
            self.assertFalse(Todo.select().count())

class ResourcesUsersTest(InheritTestClient):

    def test_User_create_fail(self):
        with test_database(db, (User,)):
            self.app.post('/api/v1/users', data={
                'username': 'user_one',
                'password': 'password1',
                'verify_password': 'password2',
                'email': 'user_one@gmail.com'
                })
            self.assertFalse(User.select().count())
    def test_User_create_success(self):
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