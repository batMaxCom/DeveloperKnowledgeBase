# Сложные выражения (Expression Language)

## CASE WHEN

```python
from sqlalchemy import case

stmt = select(
    orders.c.id,
    case(
        (orders.c.price > 1000, "expensive"),
        else_="cheap"
    ).label("category")
)
```
## COALESCE / NULLIF
### COALESCE(x, y)

Возвращает первое НЕ-NULL значение.
```python
stmt = select(
    users.c.id,
    func.coalesce(users.c.nickname, users.c.name).label("title")
)
```
### NULLIF(x, y)

Возвращает NULL, если x = y.
```python
stmt = select(
    func.nullif(orders.c.status, "pending")
)
```
## JSONB-операции

Допустим, столбец:
```python
users.c.data  # JSONB
```

Примеры:

1) Доступ к полю JSON:
```python
stmt = select(users).where(
    users.c.data["age"].as_integer() > 18
)
```

2) Работа с вложенными полями:
```python
users.c.data["address"]["city"].astext == "Berlin"
```

3) Проверка наличия ключа:
```python
stmt = select(users).where(
    users.c.data.has_key("is_verified")
)
```

4) Проверка, что JSON содержит объект (оператор @>)
```python
stmt = select(users).where(
    users.c.data.contains({"role": "admin"})
)
```

## ARRAY-операции

Таблица:
```python
products.c.tags  # ARRAY(TEXT)
```

1) Проверка, содержит ли массив элемент
```sql
stmt = select(products).where(
    products.c.tags.any("sale")
)
```

2) Проверка, содержит ли массив все элементы
```python
stmt = select(products).where(
    products.c.tags.contains(["sale", "new"])
)
```

3) Проверка пересечения массивов
```python
stmt = select(products).where(
    products.c.tags.overlap(["popular", "sale"])
)
```

4) Добавление элемента в массив
```python
stmt = update(products).values(
    tags=products.c.tags + ["new"]
)
```