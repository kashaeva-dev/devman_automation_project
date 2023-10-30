import json
from datetime import datetime

import requests


def create_project_name(title, start_date, end_date):
    start_date = datetime.strftime(start_date, '%d.%m.%Y')
    end_date = datetime.strftime(end_date, '%d.%m.%Y')
    project_name = f'Проект: {title} [{start_date}-{end_date}]'
    return project_name


def create_workspace(key, token, name):
    """Создает новое рабочее пространство в Trello."""
    url = 'https://api.trello.com/1/organizations'
    headers = {
        'Accept': 'application/json',
    }
    query = {
        'displayName': name,
        'key': key,
        'token': token,
    }
    response = requests.post(url, headers=headers, params=query)
    response.raise_for_status()
    return response.json()


def delete_workspace(key, token, ws_id):
    """
    Удаляет рабочее пространство в Trello
    по id вида 653cfdf2749d15219e08aa9a или
    name вида 22310202330102023"""
    url = f'https://api.trello.com/1/organizations/{ws_id}'
    query = {
        'key': key,
        'token': token,
    }
    response = requests.delete(url, params=query)
    response.raise_for_status()
    return


def create_board(key, token, ws_id, board_name, background='blue'):
    """Создает в Trello новую доску с указанным названием."""
    url = 'https://api.trello.com/1/boards'
    query = {
        'name': board_name,
        'key': key,
        'token': token,
        'idOrganization': ws_id,
        'prefs_permissionLevel': 'private',
        'prefs_background': background,
    }
    response = requests.post(url, params=query)
    response.raise_for_status()
    return response.json()


def delete_board(key, token, board_id):
    url = f'https://api.trello.com/1/boards/{board_id}'
    query = {
        'key': key,
        'token': token,
    }
    response = requests.delete(url, params=query)
    response.raise_for_status()
    return response.status_code


def invite_member_to_board_via_email(
        key, token, board_id, user_email, user_name):
    """Направляет пользователю письмо со ссылкой на доску Trello."""
    url = f'https://api.trello.com/1/boards/{board_id}/members'
    headers = {
        'Content-Type': 'application/json'
    }
    query = {
        'email': user_email,
        'key': key,
        'token': token
    }
    payload = json.dumps({
        'fullName': user_name
    })
    response = requests.put(url, data=payload, headers=headers, params=query)
    response.raise_for_status()
    member_id = [
        member['id'] for member in response.json()['members']
        if member['fullName'] == user_name][0]
    return member_id
