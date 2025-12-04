# Подзапросы (Subqueries)
## Три основных типа
1. Подзапрос в SELECT

```python
Пример: максимальная цена заказа
subq = (
    select(func.max(orders.c.price))
).subquery()
```

Использование:
```python
stmt = (
    select(orders)
    .where(orders.c.price == subq.scalar_subquery())
)
```

Технические особенности:

.subquery() создаёт объект:
```sql
SELECT ... AS anon_1
```

.scalar_subquery() создаёт скаляр:
```sql
(SELECT MAX(...))
```

Когда нужна таблица → .subquery()
Когда нужен скаляр → .scalar_subquery()

2. Подзапрос в FROM
```python
subq = (
    select(orders.c.user_id, func.sum(orders.c.amount).label("total"))
    .group_by(orders.c.user_id)
).subquery()

query = select(subq)
```

3. Подзапрос в WHERE
```python
subq = select(orders.c.user_id)
query = select(users).where(users.c.id.in_(subq))
```

## CTE
```python
cte_sale = (
    select(orders.c.id, (orders.c.price * 0.9).label("sale_price"))
).cte("sale")

query = select(cte_sale)
```

### Inline CTE в SQLAlchemy
```python
cte = (
    select(orders.c.id, orders.c.price * 0.9)
    .cte("sale")
)
```

## Объединение CTE + JOIN

Пример: рассчитать скидки и соединить с таблицей товаров.

```python
sale = (
    select(
        orders.c.id,
        orders.c.product_id,
        (orders.c.price * 0.9).label("sale_price")
    ).cte("sale")
)

query = (
    select(sale.c.id, products.c.name, sale.c.sale_price)
    .join(products, products.c.id == sale.c.product_id)
)
```

### Подзапросы + агрегаты
```python
subq = select(func.max(orders.c.price)).scalar_subquery()
query = select(orders).where(orders.c.price == subq)
```