# Самый лучший проект foodgram

Проект представляет из себя кулинарную платформу, которая позволяет публиковать и просматривать рецепты. Foodgram позволяет помечать рецепты как избранные чтобы их не потерять в списке опубликованных. Так же есть удобная возможность поместить рецепт в корзину, что дает возможность скачать необходимые ингредиенты в формате txt. 
Если какой-либо пользователь понравился вам своими кулинарными изысками, то в Foodgram вы можете подписаться на него и отслеживать обновления его рецептов.

## Как запустить проект на локальном компьютере?

1.Склонировать репозиторий на локальный компьютер:
```
git clone https://github.com/AtariOverlord09/kittygram_final.git
```

2.Для создания образа backend выполнить команду:
```
docker build -t taski_backend . 
```

3.Заполнить .env файл по формату env.example:
```
POSTGRES_DB=kittygram
POSTGRES_USER=kittygram_user
POSTGRES_PASSWORD=kittygram_password
DB_NAME=kittygram
ALLOWED_HOSTS=localhost,host,127.0.0.1,
SECRET_KEY=django_key
```

5.Запустить контейнер backend:
```
docker run --name foodgram_backend_container --rm -p 8000:8000 foodgram_backend
```

4.Создание образа frontend-приложения командой:
```
docker build -t foodgram_frontend . 
```

5.Запуск контейнера:
```
docker run --rm -it -p 8000:8000 --name foodgram_frontend_test foodgram_frontend
```

Автор: 
AtariOverlord09