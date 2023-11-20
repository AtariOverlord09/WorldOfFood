# Самый лучший проект WorldOfFood

## Описание
Проект представляет из себя кулинарную платформу, которая позволяет публиковать и просматривать рецепты. WorldOfFood позволяет помечать рецепты как избранные чтобы их не потерять в списке опубликованных. Так же есть удобная возможность поместить рецепт в корзину, что дает возможность скачать необходимые ингредиенты в формате txt. 
Если какой-либо пользователь понравился вам своими кулинарными изысками, то в Foodgram вы можете подписаться на него и отслеживать обновления его рецептов.

## Как запустить проект на локальном компьютере?
## Установка
1.Склонировать репозиторий на локальный компьютер:
```
git clone https://github.com/AtariOverlord09/WorldOfFood.git
```

2.Для создания образа backend выполнить команду:
```
docker build -t world_of_food . 
```

3.Заполнить .env файл по формату env.example:
```
POSTGRES_DB=foodgram_db
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
ALLOWED_HOSTS=localhost,host,127.0.0.1,
SECRET_KEY=django_key
```

4.Запустить контейнер backend:
```
docker run --name foodgram_backend_container --rm -p 8000:8000 --env-file .env foodgram_backend
```


Автор: 
Иван Сахневич
