# foodgram

### Описание:

«Фудграм» — сайт, на котором пользователи могут публиковать рецепты,
добавлять чужие рецепты в избранное и подписываться на публикации других
авторов. Пользователям сайта также будет доступен сервис «Список покупок». 
Он позволит создавать список продуктов, которые нужно купить для приготовления
выбранных блюд.

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

### Вход на сайт https//:foodgramproject.myddns.me

superuser: admin

password: 01021983

### Регистрация

Отправить POST-запрос на добавление нового пользователя на эндпоинт /api/users/
с параметрами:
 - email
 - username
 - first_name
 - last_name
 - password

Пример запроса: 

```
{
    "email": "kisa@yandex.ru",
    "username": "kisa.mura",
    "first_name": "Кира",
    "last_name": "Муравьева",
    "password": "mnjggffdfdf"
}
```
### Аутентификация 

1. Отправить POST-запрос на получение токена на эндпоинт /api/auth/token/login/.

Пример запроса: 

```
{
    "email": "kisa@yandex.ru",
    "password": "mnjggffdfdf"
}
```

2. Отправить POST-запрос на удаление токена на эндпоинт /api/auth/token/logout/.


### Примеры запросов:

POST-запрос пользователя на создание рецепта:

1. Пример запроса: 

```
{
   "id": 1,
   "name": "Блины",
   "tags": 1,
   "ingredients": [
       {
          "id": 8,
          "amount": 10
       },
       {
          "id": 9,      
          "amount": 2      
       }
       ],
   "image": Null,     
   "text": "Ароматные блинчики!",     
   "cooking_time": 35     
  }
  
 ```       

2. Пример ответа:

```
  {
        "id": 1,
        "name": "Блины",
        "tags": 1,
        "author": {
            "id": 2,
            "email": "nastya@yandex.ru",
            "username": "nastya.vasina",
            "first_name": "Настя",
            "last_name": "Васина",
            "is_subscribed": false
        },
        "ingredients": [
            {
                "id": 8,
                "amount": 1
            },
            {
                "id": 9,
                "amount": 2
            }
        ],
        "image": "http://foodgramproject.myddns.me/media/recipes/media/e2626a1b-19cb-4633-9cfa-ed93e39b0d47.webp",
        "text": "Ароматные блинчики!",
        "cooking_time": 35,
        "is_favorited": false,
        "is_in_shopping_cart": false
    }
```
