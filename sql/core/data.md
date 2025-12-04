# Работа с данными

## Update 
`bindparam` - это функция из подсистемы Core Expression Language, которая явно определяет "связанный параметр" (bound parameter) или плейсхолдер (заполнитель) в SQL-выражении. 

```python
connection.execute(
    update(products)
    .where(products.c.id == bindparam("id"))
    .values(price=bindparam("price")),
    [
        {"id": 1, "price": 100},
        {"id": 2, "price": 200}
    ]
)
```

`bindparam()`создаёт плейсхолдер для значения, которое будет безопасно передано в базу данных во время выполнения. Это имеет несколько преимуществ по сравнению с прямым форматированием значений в строку SQL:
- `Безопасность`: Предотвращает атаки типа SQL-инъекций, разделяя SQL-команду и данные, предоставленные пользователем. Драйвер базы данных сам позаботится о правильном экранировании и кавычках для значений.
- `Производительность`: База данных может оптимизировать и повторно использовать план выполнения запроса, даже если значения параметров меняются при каждом выполнении.
- `Гибкость`: Позволяет отложить определение фактического значения параметра до момента выполнения оператора. 

## Upsert
Работает только в PostgreSQL.
```python
stmt = insert(users).values(
    id=1,
    name="John",
    email="john@example.com"
)

stmt = stmt.on_conflict_do_update(
    index_elements=[users.c.id],
    set_=dict(name="John Updated")
)
```
### UPSERT с сохранением старых значений
```python
stmt = (
    insert(users)
    .values(id=1, login_count=1)
    .on_conflict_do_update(
        index_elements=[users.c.id],
        set_={
            "login_count": users.c.login_count + 1
        }
    )
)
```

### UPSERT с исключением определённых столбцов

Если хотите обновлять только при изменении email:
```python
stmt = (
    insert(users)
    .values(id=1, email="new@example.com")
    .on_conflict_do_update(
        index_elements=[users.c.id],
        set_={
            "email": stmt.excluded.email
        }
    )
)
```



