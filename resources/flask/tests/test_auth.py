#!/usr/bin/env python3

import jwt
import pytest
from datetime import datetime, timedelta


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='username', password='password'):
        return self._client.post('/auth/login', json={'username': username, 'password': password})

    def get_auth_header(self, username='username', password='password'):
        response = self.login(username, password)
        data = response.get_json() if response.get_json() is not None else {}
        return {'Authorization': f'Bearer {data.get("token", "")}'}


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.mark.parametrize(('token', 'body', 'message'), (
    (jwt.encode({'user_id': 0, 'expires': datetime.now().timestamp()}, 'secret', algorithm='HS256'), 'Test body', 'Invalid token.'),
    ('Bearer ' + jwt.encode({'user_id': 0, 'expires': datetime.now().timestamp()}, 'secret', algorithm='HS256'), 'Test body', 'Token has expired.'),
    ('Bearer ' + jwt.encode({'user_id': 0, 'expires': datetime.now().timestamp()}, 'secret', algorithm='HS512'), 'Test body', 'Invalid token.')
))
def test_validate_token(client, token, body, message):
    response = client.post('/task/', json={'body': body}, headers={'Authorization': token})
    data = response.get_json() if response.get_json() is not None else {}
    assert message in data.get('error', '')


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', 'Username is required.'),
    ('username', '', 'Password is required.'),
    ('user', 'password', 'Username is incorrect.'),
    ('username', 'pass', 'Password is incorrect.'),
    ('username', 'password', '')
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    data = response.get_json() if response.get_json() is not None else {}
    assert message in data.get('error', '')


@pytest.mark.parametrize(('name', 'username', 'password', 'message'), (
    ('', '', '', 'Name is required.'),
    ('user', '', '', 'Username is required.'),
    ('user', 'username', '', 'Password is required.'),
    ('user', 'username', 'password', 'is taken.'),
    ('user', 'username2', 'password', '')
))
def test_register_validate_input(client, name, username, password, message):
    response = client.post('/auth/register', json={'name': name, 'username': username, 'password': password})
    data = response.get_json() if response.get_json() is not None else {}
    assert message in data.get('error', '')