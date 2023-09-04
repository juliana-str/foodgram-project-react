[![foodgram_workflow](https://github.com/juliana-str/foodgram-project-react/blob/master/.github/workflows/main.yml)](https://github.com/juliana-str/foodgram-project-react/blob/master/.github/workflows/main.yml)
# "Продуктовый помощник" (Foodgram)

## 1. [Описание](#1)
## 2. [Установка Docker (на платформе Ubuntu)](#2)
## 3. [База данных и переменные окружения](#3)
## 4. [Команды для запуска](#4)
## 5. [Заполнение базы данных](#5)
## 6. [Примеры запросов к api](#6)
## 7. [Техническая информация](#7)
## 8. [Об авторе](#8)

---
## 1. Описание <a id=1></a>

Проект "Продуктовый помошник" (Foodgram) - сайт, на котором пользователи могут: 
  - регистрироваться
  - создавать свои рецепты и управлять ими (корректировать\удалять)
  - просматривать рецепты других пользователей
  - добавлять рецепты других пользователей в "Избранное" и в "Список покупок"
  - подписываться на других пользователей
  - скачать список ингредиентов для рецептов, добавленных в "Список покупок"

##Вход на сайт 

https//:foodgramproject.myddns.me

superuser: admin

password: 01021983

---
## 2. Установка Docker (на платформе Ubuntu) <a id=2></a>

Проект поставляется в четырех контейнерах Docker (db, frontend, backend, nginx).  
Для запуска необходимо установить Docker и Docker Compose.  
Подробнее об установке на других платформах можно узнать на [официальном сайте](https://docs.docker.com/engine/install/).

Для начала необходимо скачать и выполнить официальный скрипт:
```bash
apt install curl
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

При необходимости удалить старые версии Docker:
```bash
apt remove docker docker-engine docker.io containerd runc 
```

Установить пакеты для работы через протокол https:
```bash
apt update
```
```bash
apt install \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg-agent \
  software-properties-common -y 
```

Добавить ключ GPG для подтверждения подлинности в процессе установки:
```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```

Добавить репозиторий Docker в пакеты apt и обновить индекс пакетов:
```bash
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" 
```
```bash
apt update
```

Установить Docker(CE) и Docker Compose:
```bash
apt install docker-ce docker-compose -y
```

Проверить что  Docker работает можно командой:
```bash
systemctl status docker
```

Подробнее об установке можно узнать по [ссылке](https://docs.docker.com/engine/install/ubuntu/).

---
## 3. База данных и переменные окружения <a id=3></a>

Проект использует базу данных PostgreSQL.  
Для подключения и выполненя запросов к базе данных необходимо создать и заполнить файл ".env" с переменными окружения в папке "./infra/".

Шаблон для заполнения файла ".env":
```python
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='Здесь указать секретный ключ'
ALLOWED_HOSTS='Здесь указать имя или IP хоста' (Для локального запуска - 127.0.0.1)
```

---
## 4. Команды для запуска <a id=4></a>

Перед запуском необходимо склонировать проект:
```bash
git clone git@github.com:juliana-str/foodgram-project-react.git

```

Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```
```bash
Linux: source venv/bin/activate
Windows: source venv/Scripts/activate
```

И установить зависимости из файла requirements.txt:
```bash
python3 -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

Далее необходимо собрать образы для фронтенда и бэкенда.  
Из папки "./backend/foodgram/" выполнить команду:
```bash
docker build -t julianastr/foodgram_backend .
```

Из папки "./frontend/" выполнить команду:
```bash
docker build -t julianastr/foodgram_frontend .
```

После создания образов можно создавать и запускать контейнеры.  
Из папки "./infra/" выполнить команду:
```bash
docker-compose up -d
```

После успешного запуска контейнеров выполнить миграции:
```bash
docker-compose exec backend python manage.py migrate
```

Создать суперюзера (Администратора):
```bash
docker-compose exec backend python manage.py createsuperuser
```

Собрать статику:
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

Теперь доступность проекта можно проверить по адресу [http://localhost/](http://localhost/)

---
## 5. Заполнение базы данных <a id=5></a>

С проектом поставляются данные об ингредиентах.  
Заполнить базу данных ингредиентами и тегами можно выполнив следующую команду из папки "./backend/":
```bash
docker-compose exec backend python manage.py load_data
```

## 6. Примеры запросов к api <a id=6></a>

```
Регистрация

Отправить POST-запрос на добавление нового пользователя на эндпоинт /api/users/
с параметрами:
 - email
 - username
 - first_name
 - last_name
 - password

```

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
Аутентификация 

1. Отправить POST-запрос на получение токена на эндпоинт /api/auth/token/login/.

Пример запроса: 

```
{
    "email": "kisa@yandex.ru",
    "password": "mnjggffdfdf"
}
```

2. Отправить POST-запрос на удаление токена на эндпоинт /api/auth/token/logout/.


Примеры запросов:

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

## 7. Техническая информация <a id=7></a>

Стек технологий: Python 3, Django, Django Rest, React, Docker, PostgreSQL, nginx, gunicorn, Djoser, github-actions, CI-CD.

Веб-сервер: nginx (контейнер nginx)  
Frontend фреймворк: React (контейнер frontend)  
Backend фреймворк: Django (контейнер backend)  
API фреймворк: Django REST (контейнер backend)  
База данных: PostgreSQL (контейнер db)

Веб-сервер nginx перенаправляет запросы клиентов к контейнерам frontend и backend, либо к хранилищам (volume) статики и файлов.  
Контейнер nginx взаимодействует с контейнером backend через gunicorn.  
Контейнер frontend взаимодействует с контейнером backend посредством API-запросов.

---
## 8. Об авторе <a id=8></a>

Стрельникова Юлиана Сергеевна  
Python-разработчик (Backend)  
Россия, г. Санкт-Петербург 
E-mail: julianka.str@yandex.ru  
Telegram: @JulianaStr
