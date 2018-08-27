# Описание

Сервис комментариев с неограниченной вложенностью. Комментарий можно привязать к различным сущностям (для примера созданы сущности BlogPost и UserProfile).
Для хранения дерева комментариев был выбран паттерн Closure Table (все потомки хранятся в отдельной таблице). При таком подходе есть оверхед по данным, зато просто добавлять получать потомков.

# Запуск проекта
```
cat .env-example > .env
docker-compose up -d
docker-compose exec django python manage.py migrate
docker-compose restart
```

http://localhost:8080


# API интерфейсы

Создание комментария к определенной сущности с указанием сущности, к которой он относится
```
POST /comments/
```

Получение комментариев первого уровня для определенной сущности с пагинацией
```
GET /comments/?parent=42&parent_type=42
```

Редактирование комментария
```
PUT PATCH /comments/<comment_id>/
```

Удаление комментария, если нет потомков
```
DELETE /comments/<comment_id>/
```

История изменений комментария
```
GET /comments/<comment_id>/log/
```

Получение всех дочерних комментариев для заданного комментария или сущности
```
GET /comments-descendants/?parent=42&parent_type=42
```

Получение истории комментариев определенного пользователя
```
GET /user-comments/<user_id>/
```

Выгрузка в файл всей истории комментариев
```
GET /comments-as-file/
query params:
    author - автор
    entity - id сущности
    entity_type - id типа сущности
    date_from - дата в формате dd-mm-yyyy
    date_to - дата в формате dd-mm-yyyy
```
