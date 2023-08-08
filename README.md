# praktikum_new_diplom

### Описание:



### Установка:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:juliana-str/foodgram-project-react.git
```

```
cd backend
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```


### Регистрация

Отправить POST-запрос на добавление нового пользователя на эндпоинт /api/users/
с параметрами:
 - email
 - username
 - first_name
 - last_name
 - password


### Аутентификация 

1. Отправить POST-запрос на получение токена на эндпоинт /api/auth/token/login/.
2. Отправить POST-запрос на удаление токена на эндпоинт /api/auth/token/logout/.


### Примеры запросов:

Результат POST-запроса пользователя на просмотр рецептов:

1. Пример запроса: 

```
{
    "name": "",
    "author": null,
    "ingredients": [],
    "image": null,
    "text": "",
    "cooking_time": null
}
```

2. Пример ответа:

```
{
  "id": 0,
  "text": "string",
  "author": "string",
  "score": 10,
  "pub_date": "2023-04-25T06:38:48.301Z"
}
```
