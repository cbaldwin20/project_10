from auth import auth

from flask import Blueprint, abort

from flask_restful import (
    Api, Resource, fields, marshal, marshal_with, reqparse
)

import models

todo_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'created_at': fields.DateTime
}


def todo_or_404(todo_id):
    """if instance doesn't exist then throws a 404"""
    try:
        todo = models.Todo.get(models.Todo.id == todo_id)
    except models.Todo.DoesNotExist:
        abort(404)
    else:
        return todo


class TodoList(Resource):
    """Will get all the instances, or add an instance"""
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No todo name provided',
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        """will get all of the instances in the database"""
        todos = [marshal(todo, todo_fields) for todo in models.Todo.select()]
        return todos

    @auth.login_required
    @marshal_with(todo_fields)
    def post(self):
        """will post a Todo instance"""
        args = self.reqparse.parse_args()
        todo = models.Todo.create(**args)
        return (todo, 201)


class Todo(Resource):
    """will get, change, or delete a single instance"""
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No todo name provided',
            location=['form', 'json']
        )

        super().__init__()

    @marshal_with(todo_fields)
    def get(self, id):
        """get a single instance"""
        return todo_or_404(id)

    @auth.login_required
    @marshal_with(todo_fields)
    def put(self, id):
        """will change a single instance"""
        args = self.reqparse.parse_args()
        todo = models.Todo.update(**args).where(models.Todo.id == id)
        todo.execute()
        return (models.Todo.get(models.Todo.id == id), 200)

    @auth.login_required
    def delete(self, id):
        """will delete a single instance"""
        todo = models.Todo.delete().where(models.Todo.id == id)
        todo.execute()
        return ("", 204)

todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(
    TodoList,
    '/api/v1/todos',
    endpoint='todos'
)
api.add_resource(
    Todo,
    '/api/v1/todos/<int:id>',
    endpoint='todo'
)
