# Сайт с вопросами по BlueLock
Соловьев Иван Web-13
`Я использовал для тестирования google chrome и dia, а safari немного грустит у меня почему-то от bootstrap.`

```bash
# Поднять django app сервер
docker-compose up -d
docker-compose exec -T web python manage.py migrate
docker-compose exec -T web python manage.py fill_db 5
```

## Домашнее задание 4:
1. Добавил форму входа и регистрации.
2. Добавил возможность изменить данные в настройках, в том числе поменять аватарку.
3. Добавил crsf токен для безопасной авторизации.






