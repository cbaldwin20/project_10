import coverage
cov = coverage.coverage(omit=['*_venv*'])
cov.start()

import unittest
from app import app

from playhouse.test_utils import test_database
from peewee import SqliteDatabase

from models import Todo

TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([Todo], safe=True)





class CreateTodoInstance(unittest.TestCase):
    def test_todo_create(self):
        with test_database(TEST_DB, (Todo,)):
            Todo.create(name='Go bowling')
            todo = Todo.select().get()
            self.assertEqual(todo.name, 'Go bowling')


class ResourceTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

    def test_todolist_get(self):
        with test_database(TEST_DB, (Todo,)):
            Todo.create(name="Cook dinner")
            Todo.create(name="Wash dishes")
            rv = self.app.get('/api/v1/todos')
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b"Cook dinner", rv.data)
            self.assertIn(b"Wash dishes", rv.data)

    def test_todolist_post(self):
        with test_database(TEST_DB, (Todo,)):
            rv = self.app.post('/api/v1/todos',
                               
                               data={'name': 'Go bowling'}
                               )
            self.assertEqual(rv.status_code, 201)
            self.assertEqual(Todo.select().count(), 1)
            todo = Todo.select().get()
            self.assertEqual(todo.name, 'Go bowling')
            self.assertIn(b"Go bowling", rv.data)

    def test_todo_put(self):
        with test_database(TEST_DB, (Todo,)):
            Todo.create(name='Cook dinner')
            rv = self.app.put('/api/v1/todos/1',
                              
                              data={'name': 'Wash dishes'}
                              )
            self.assertEqual(rv.status_code, 200)
            todo = Todo.select().where(Todo.id == 1)
            self.assertEqual(todo[0].name, 'Wash dishes')
            self.assertIn(b"Wash dishes", rv.data)

    def test_todo_delete(self):
        with test_database(TEST_DB, (Todo,)):
            Todo.create(name='Cook dinner')
            rv = self.app.delete('/api/v1/todos/1',
                                 )
            self.assertEqual(rv.status_code, 204)
            self.assertEqual(Todo.select().count(), 0)
            self.assertEqual(b"", rv.data)


class TodoViewTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

    def test_empty_db(self):
        with test_database(TEST_DB, (Todo,)):
            rv = self.app.get('/')
            self.assertIn(b"Add a New Task", rv.data)


if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print("\n\nCoverage Report:\n")
    cov.report(show_missing=True)
    cov.erase()