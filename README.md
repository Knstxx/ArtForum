# Проект YaMDb
Немного о проекте:
1. Финальный проект в рамках изучения DRF с применением токенов Simple JWT для регистрации.
2. Составлено по ReDoc документации.
3. Проект YaMDb собирает отзывы пользователей на различные произведения.
4. Над проектом работали:
<a href="https://github.com/Knstxx" target="_blank">Константин</a>
<a href="https://github.com/Andrew-White-cyber" target="_blank">Андрей</a>
<a href="https://github.com/Jlanceth" target="_blank">Данил</a>
# Как запустить проект:

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
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

# Импорт данных из CSV файлов:
1. Предварительно можно очистить БД:*
```
python manage.py flush
```
2. Применить команду для импорта:
```
python manage.py impdata
```

# Некоторые примеры запросов:
1. Добавить новый отзыв

POST /api/v1/titles/{title_id}/reviews/
```
{
  "text": "string",
  "score": 1
}
```
2. Получить список всех комментариев к отзыву по id

GET /api/v1/titles/{title_id}/reviews/{review_id}/comments/
```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": 0,
      "text": "string",
      "author": "string",
      "pub_date": "2019-08-24T14:15:22Z"
    }
  ]
}
```
3. Частично обновить комментарий к отзыву по id

PATCH /api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/
```
{
  "text": "string"
}
```
