# Оконные функции (WINDOW FUNCTIONS)
SQLAlchemy Core полностью поддерживает синтаксис OVER(), включая:
- PARTITION BY
- ORDER BY
- frame specification (ROWS BETWEEN ...)
- LAG, LEAD
- оконные агрегаты (SUM() OVER(), AVG() OVER(), …)
- оконные функции ранжирования (ROW_NUMBER, RANK, DENSE_RANK)

##  Базовый синтаксис окна в SQLAlchemy
```python
func.sum(orders.c.price).over(
    partition_by=orders.c.user_id,
    order_by=orders.c.created_at
)

```
Это преобразуется в SQL:
```sql
SUM(price) OVER (PARTITION BY user_id ORDER BY created_at)
```

## PARTITION BY

Используется для разделения данных на группы.

Пример: сумма заказов по пользователю
```python
stmt = select(
    orders.c.id,
    func.sum(orders.c.price).over(
        partition_by=orders.c.user_id
    ).label("total_price")
)
``` 
## ORDER BY внутри окна

Добавляет сортировку внутри каждой группы.

Running Sum (кумулятивная сумма внутри пользователя)
```python
stmt = select(
    orders.c.id,
    orders.c.price,
    func.sum(orders.c.price).over(
        partition_by=orders.c.user_id,
        order_by=orders.c.created_at
    ).label("running_sum")
)
```
##RANK / DENSE_RANK / ROW_NUMBER
### ROW_NUMBER
```python
stmt = select(
    orders.c.*,
    func.row_number().over(
        partition_by=orders.c.user_id,
        order_by=orders.c.price.desc()
    ).label("rn")
)
```
### RANK
```python
func.rank().over(order_by=orders.c.price.desc())
```

### DENSE_RANK
```python
func.dense_rank().over(order_by=orders.c.price.desc())
```

## LAG и LEAD

Используются для анализа временного ряда.

## LAG — предыдущая строка
```python
stmt = select(
    orders.c.id,
    orders.c.price,
    func.lag(orders.c.price)
        .over(order_by=orders.c.created_at)
        .label("prev_price")
)
```

### LEAD — следующая строка
```python
func.lead(orders.c.price).over(order_by=orders.c.created_at)
```