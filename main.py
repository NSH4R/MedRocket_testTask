import os
import datetime
import requests

USERS_API = 'https://json.medrocket.ru/users'
TODOS_API = 'https://json.medrocket.ru/todos'


def create_directory():
    if os.path.exists('tasks'):
        return
    else:
        os.mkdir('tasks')


def request_json(api: str):
    try:
        response = requests.get(api)
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f'Ошибка при получение данных: {e}')
        exit()


def json_to_dict():
    users_json = request_json(USERS_API)
    todos_json = request_json(TODOS_API)
    users_data_dict = {us['id']: {
        'id': us['id'],
        'name': us['name'],
        'username': us['username'],
        'email': us['email'],
        'company': {
            'name': us['company']['name']
        },
        'completed': [],
        'not_completed': []
    } for us in users_json}

    for todo in todos_json:
        user_id = todo.get('userId')
        title = todo.get('title')
        completed = todo.get('completed')
        if None in (title, user_id):
            continue
        title = f'{title[:46]}...' if len(title) >= 46 else title
        users_data_dict[user_id]['completed'].append(title) if completed else (
            users_data_dict[user_id]['not_completed'].append(title))
    return users_data_dict


def create_and_add_reports():
    create_directory()
    user_todos = json_to_dict()
    for key, member in user_todos.items():
        try:
            file_path = f'tasks/{member["username"]}.txt'
            now = datetime.datetime.now()
            if os.path.exists(file_path):
                os.rename(file_path, f'tasks/old_{member["username"]}_{now.strftime("%Y-%m-%dT%H-%M-%S")}.txt')

            task_0_list, task_1_list = [], []
            for task0 in member['not_completed']:
                task_0_list.append(f'- {task0}')
            for task1 in member['completed']:
                task_1_list.append(f'- {task1}')

            with open(f'tasks/{member["username"]}.txt', 'w', encoding='utf-8') as file:
                file.write(f'Отчёт для {member["company"]["name"]}.'
                           f'\n{member["name"]} <{member["email"]}> {now.strftime("%Y-%m-%d %H-%M-%S")}\n'
                           f'Всего задач: {len(member["not_completed"]) + len(member["completed"])}'
                           f'\n\n## Актуальные задачи ({len(member["not_completed"])}):\n')
                file.write('\n'.join(task_0_list))
                file.write(f'\n\n## Завершённые задачи: ({len(member["completed"])}):\n')
                file.write('\n'.join(task_1_list))

        except Exception as e:
            print(f'Ошибка при создание {member["username"]}.txt: {e}')
    print('Отчет успешно сформирован !')


create_and_add_reports()
