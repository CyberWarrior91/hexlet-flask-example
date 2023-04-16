from flask import (
Flask, 
render_template, 
request, 
redirect, 
url_for, 
get_flashed_messages, 
flash, 
make_response,
session)
from uuid import uuid4
import json
import os
# Это callable WSGI-приложение
app = Flask(__name__)
app.secret_key = "123HEXLET$"
app.config['SECRET_KEY'] = 'randomstring'


def validate(user):
    errors = {}
    if not user['nickname']:
        errors['nickname'] = "Can't be blank"
    if not user['email']:
        errors['email'] = "Can't be blank"
    elif len(user['nickname']) <= 4:
        errors['nickname'] = "Nickname must be greater than 4 characters"
    elif '@' not in user['email']:
        errors['email'] = "Wrong format"
    return errors


@app.route('/users/new')
def search_users():
    user = {
        'nickname': '',
        'email': ''
    }
    errors = {}
    flash('Registration successful!')
    return render_template(
        'users/index.html',
        user=user,
        errors=errors
    )


@app.post('/users')
def post_users():
    user = request.form.to_dict()
    errors = validate(user)
    if errors:
        return render_template(
            'users/index.html',
            user=user,
            errors=errors,
        ), 422
    user['id'] = str(uuid4())
    data_base = json.loads(request.cookies.get('data_base', json.dumps([])))
    data_base.append(user)
    encoded_base = json.dumps(data_base)
    response = make_response(redirect(url_for('get_users'), code=302))
    response.set_cookie('data_base', encoded_base)
    return response


@app.get('/users')
def get_users():
    data_base = json.loads(request.cookies.get('data_base', json.dumps([])))
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'users/show.html',
        users=data_base,
        messages=messages,
    )


@app.route('/users/<id>/edit', methods=['GET', 'POST'])
def edit_user(id):
    data_base = json.loads(request.cookies.get('data_base', json.dumps([])))
    for user in data_base:
        if id == user['id']:
            current_user = user
    errors = []
    if request.method == 'GET':
        return render_template(
            'users/edit.html',
            user=current_user,
            errors=errors,
        )
    if request.method == 'POST':
        data = request.form.to_dict()
        errors = validate(data)
        if errors:
            return render_template(
                'users/edit.html',
                user=user,
                errors=errors,
            ), 422
        for user in data_base:
            if id == user['id']:
                user['nickname'] = data['nickname']
                user['email'] = data['email']
        encoded_base = json.dumps(data_base)
        response = make_response(redirect(url_for('get_users'), code=302))
        flash('User has been updated', 'success')
        response.set_cookie('data_base', encoded_base)
        return response


@app.route('/users/<id>/delete', methods = ['POST'])
def delete_user(id):
    data_base = json.loads(request.cookies.get('data_base', json.dumps([])))
    for user in data_base:
        if id == user['id']:
            data_base.pop(data_base.index(user))
    encoded_base = json.dumps(data_base)
    response = make_response(redirect(url_for('get_users'), code=302))
    flash('The user has been deleted')
    response.set_cookie('data_base', encoded_base)
    return response


@app.route('/users/login', methods=['GET', 'POST'])
def login():
    current_user = request.form.get('email')
    if request.method == 'GET':
        return render_template(
            'users/login.html',
        )
    if request.method == 'POST':
        session['email'] = current_user
        flash(f"Logged in as {session.get('email')}")
        return redirect(url_for('get_users'), code=302)


@app.route('/users/logout', methods=['POST', 'DELETE'])
def delete_session():
    session.pop('email', None)
    session.clear()
    return redirect(url_for('get_users'))