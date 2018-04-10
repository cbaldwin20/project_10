from flask import jsonify, Blueprint, abort

from flask.ext.restful import (Resource, Api, reqparse,
                               inputs, fields, marshal,
                               marshal_with, url_for)

import models

todo_fields = {
    'name': fields.String,
}





def todo_or_404(todo_id):
    try:
        todo = models.Todo.get(models.Todo.id==todo_id)
    except models.Todo.DoesNotExist:
        abort(404)
    else:
        return todo 


class TodoList(Resource):
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
        todos = [marshal(todo, todo_fields) for todo in models.Todo.select()]
        return todos
    
    @marshal_with(todo_fields)
    def post(self):
        args = self.reqparse.parse_args()
        todo = models.Todo.create(**args)
        return (todo, 201)


class Todo(Resource):
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
        return todo_or_404(id)
    
    def put(self, id):
        args = self.reqparse.parse_args()
        todo = models.Todo.update(**args).where(models.Todo.id==id)
        return (todo, 201)
    
    def delete(self, id):
        todo = models.Todo.delete().where(models.Todo.id==id)
        todo.execute()
        return 201

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