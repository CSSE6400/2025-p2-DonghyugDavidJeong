from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta

api = Blueprint('api', __name__, url_prefix='/api/v1') 

legal_keys = {'title', 'description', 'completed', 'deadline_at', 'id'}

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})

@api.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    result = []
    window = request.args.get('window')
    if window:
        window = int(window)

    for todo in todos:
        if (request.args.get('completed') == 'true'):
            if todo.completed is True:
                result.append(todo.to_dict())
        elif (request.args.get('completed') == 'false'):
            if todo.completed is False:
                result.append(todo.to_dict())
        elif window:
            if todo.deadline_at - datetime.now() < timedelta(days=window):
                result.append(todo.to_dict())
        else:
            result.append(todo.to_dict())
    return jsonify(result)


@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())


@api.route('/todos', methods=['POST'])
def create_todo():
    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
    )
    if not todo.title:
        return jsonify({'error': 'Title not found'}), 400
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
    for key in request.json.keys():
        if key not in legal_keys:
            return jsonify({'error': 'Unexpected parameter found'}), 400
    # Adds a new record to the database or will update an existing record.
    db.session.add(todo)
    # Commits the changes to the database.
    # This must be called for the changes to be saved.
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    if request.json.get('id'):
        return jsonify({'error': 'found ID?'}), 400
    for key in request.json.keys():
        if key not in legal_keys:
            return jsonify({'error': 'Unexpected parameter found'}), 400
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    db.session.commit()
    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200