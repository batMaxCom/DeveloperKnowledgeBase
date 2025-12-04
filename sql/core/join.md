# JOIN

Основная форма:
```python
select(...).join(target_table, condition)
```
## Типы JOIN

### INNER JOIN
```python
stmt = (
    select(users.c.name, orders.c.price)
    .join(orders, users.c.id == orders.c.user_id)
)

```
### LEFT JOIN
```python
stmt = (
    select(users, orders)
    .join(orders, users.c.id == orders.c.user_id, isouter=True)
)
```

### RIGHT JOIN (редко используется)

```python
stmt = select(users).join(orders, isouter=True, full=False, right=True)
```
### FULL OUTER JOIN
```python
stmt = (
    select(users, orders)
    .join(orders, users.c.id == orders.c.user_id, full=True)
)
```

### CROSS JOIN
```python
stmt = select(users, countries).select_from(
    users.cross_join(countries)
)
```

## join() vs join_from()

### join()

Присоединяет к текущей "основной" таблице в select_from.

### join_from()

Принудительно указывает, откуда и куда делать JOIN.
```python
stmt = (
    select(users.c.name, orders.c.price)
    .join_from(users, orders, users.c.id == orders.c.user_id)
)
```

join_from нужен, когда:
- порядок JOIN неочевиден
- запрос строится динамически
- нет явного select_from()