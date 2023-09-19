import os
import datetime as dt
import requests

USERS_API = 'https://json.medrocket.ru/users'
TODOS_API = 'https://json.medrocket.ru/todos'


def create_directory():
    """ Создание рабочей директории, а так же проверка ее существования """
    if os.path.exists('tasks'):  # Проверка на наличие папки с тем же наименованием
        return
    else:
        os.mkdir('tasks')


def get_request(api: str):
    """ Запрос json по api и преобразование его в словарик """
    response = requests.get(api)
    return response.json() if response.status_code == 200 else response.raise_for_status()


def sort_users():
    """ Сортировка в удобный формат словаря пользователей, добавление массивов для сортировки задач """
    users_dict = get_request(USERS_API)
    users_sort_dict = {user['id']: {
        'id': user['id'],
        'name': user['name'],
        'username': user['username'],
        'email': user['email'],
        'company': {
            'name': user['company']['name']
        },
        'true': [],
        'false': []
    } for user in users_dict}
    return users_sort_dict


def sorting_title():
    """ Сортировка списка по выполненным и невыполненным задачам, сокращение строк заголовков """
    todos_dict = get_request(TODOS_API)
    users_data_dict = sort_users()
    for todo in todos_dict:
        user_id = todo.get('userId')
        title = todo.get('title')
        completed = todo.get('completed')
        if None in (title, user_id):
            continue
        title = f'{title[:46]}…' if len(title) >= 46 else title  # Сокращаем строки более 46
        users_data_dict[user_id]['true'].append(title) if completed else (   # Сортировка строк
            users_data_dict[user_id]['false'].append(title))
    return users_data_dict


def create_and_add_reports():
    """ Создание отчета и его заполнение данными из списка """
    create_directory()
    user_todos = sorting_title()
    for key, member in user_todos.items():
        try:
            file_path = f'tasks/{member["username"]}.txt'
            now = dt.datetime.now()
            if os.path.exists(file_path):  # Проверка наличия старого отчета
                os.rename(file_path, f'tasks/old_{member["username"]}_{now.strftime("%Y-%m-%dT%H-%M")}.txt')

            true_task = [f'- {true}' for true in member['true']]  # Заполнение массивов с задачами
            false_task = [f'- {false}' for false in member['false']]
            with open(f'tasks/{member["username"]}.txt', 'w', encoding='utf-8') as file:
                file.write(f'Отчёт для {member["company"]["name"]}.'
                           f'\n{member["name"]} <{member["email"]}> {now.strftime("%Y-%m-%d %H:%M")}\n'
                           f'Всего задач: {len(false_task) + len(true_task)}'
                           f'\n\n## Актуальные задачи ({len(false_task)}):\n')
                file.write('\n'.join(false_task))
                file.write(f'\n\n## Завершённые задачи: ({len(true_task)}):\n')
                file.write('\n'.join(true_task))

        except Exception as e:
            print(f'Ошибка при создание {member["username"]}.txt: {e}')


if __name__ == '__main__':
    create_and_add_reports()
    print('Отчет успешно сформирован !')

