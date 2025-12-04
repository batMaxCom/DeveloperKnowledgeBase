# Базы данных в SQL

## CREATE

```sql
CREATE DATABASE имя_базы [параметры];
```
Простые примеры
```sql
-- Создать БД с именем "school"
CREATE DATABASE school;

-- Создать БД "inventory" с кодировкой UTF8
CREATE DATABASE inventory
  ENCODING = 'UTF8';
```

### Ключевые параметры при создании

ENCODING — кодировка символов
```sql
ENCODING = 'UTF8'  -- универсальная кодировка
```

- LC_COLLATE — правила сортировки
```sql
LC_COLLATE = 'ru_RU.UTF8'  -- для русского языка
```

- LC_CTYPE — классификация символов
```sql
LC_CTYPE = 'ru_RU.UTF8'
```

- TEMPLATE — шаблон для новой БД
```sql
TEMPLATE = template0  -- чистая БД без доп. объектов
```

Полный пример с параметрами
```sql
CREATE DATABASE company
  ENCODING = 'UTF8'
  LC_COLLATE = 'en_US.UTF8'
  LC_CTYPE = 'en_US.UTF8'
  TEMPLATE = template0
  OWNER = admin_user;  -- владелец БД
```

### DELETE
```sql
DROP DATABASE имя_базы;
```

### Проверка существующих БД
Перед созданием полезно проверить, есть ли уже такая БД:

```sql
-- Список всех БД на сервере
\l  -- в psql (PostgreSQL)

-- Или через запрос
SELECT datname FROM pg_database;
```

# Таблицы в SQL

## CREATE

Базовый синтаксис CREATE TABLE
```sql
CREATE TABLE имя_таблицы (
    столбец1 тип_данных [ограничения],
    столбец2 тип_данных [ограничения],
    ...
    столбецN тип_данных [ограничения]
);
```

### Основные типы данных
Числовые:
- `INT` — целое число;
- `SMALLINT`, `BIGINT` — числа разной разрядности;
- `DECIMAL`(p,s), `NUMERIC`(p,s) — числа с фиксированной точкой (p — точность, s — масштаб);
- `FLOAT`, `REAL` — числа с плавающей точкой.

Строковые:
- `CHAR`(n) — строка фиксированной длины (n символов);
- `VARCHAR`(n) — строка переменной длины (макс. n символов);
- `TEXT` — длинный текст (без ограничения).

Дата и время:

- `DATE` — дата (ГГГГ‑ММ‑ДД);
- `TIME` — время (ЧЧ:ММ:СС);
- `TIMESTAMP` — дата и время;
- `INTERVAL` — промежуток времени.

Логические:
-`BOOLEAN` или `BOOL` — TRUE/FALSE.

Двоичные:
- `BLOB`, `BYTEA` — двоичные данные.

### Ограничения (constraints)
Используются для контроля целостности данных.
- `PRIMARY KEY` — уникальный идентификатор строки (только одно на таблицу);
- `UNIQUE` — значение должно быть уникальным в столбце;
- `NOT NULL` — значение обязательно (не может быть NULL);
- `DEFAULT` значение — значение по умолчанию;
- `CHECK` (условие) — проверка условия (например, age >= 0);
- `FOREIGN KEY` — связь с другой таблицей.

###  Примеры:
- Простая таблица пользователей:
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    age INT CHECK (age >= 0 AND age <= 120),
    is_active BOOLEAN DEFAULT TRUE
);
```
- Таблица заказов с внешним ключом:
```sql
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```
- Таблица с автоинкрементом (PostgreSQL/MySQL):
```sql
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,  -- PostgrSQL
    -- или
    product_id INT AUTO_INCREMENT PRIMARY KEY  -- MySQL
    name VARCHAR(200) NOT NULL,
    price DECIMAL(8,2) CHECK (price > 0),
    created_at TIMESTAMP DEFAULT NOW()
);
```
### Дополнительные параметры
IF NOT EXISTS — не выдавать ошибку, если таблица уже существует:
```sql
CREATE TABLE IF NOT EXISTS logs (
    id INT PRIMARY KEY,
    message TEXT
);
```

`TEMPORARY` — временная таблица (существует только в текущем сеансе):
```sql
CREATE TEMPORARY TABLE temp_stats (
    date DATE,
    visits INT
);
```

### Создание таблицы на основе запроса
`CREATE TABLE AS SELECT` — копирует структуру и данные:

```sql
CREATE TABLE active_users AS
SELECT id, name, email
FROM users
WHERE is_active = TRUE;
```

`CREATE TABLE LIKE` — копирует только структуру (без данных):
```sql
CREATE TABLE users_backup LIKE users;
```

## ALTER

Для модификации используйте ALTER TABLE:

Добавить столбец:
```sql
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
```
Удалить столбец:
```sql
ALTER TABLE users DROP COLUMN phone;
```
Изменить тип данных:
```sql
ALTER TABLE users ALTER COLUMN email TYPE VARCHAR(300);
```
Добавить ограничение:
```sql
ALTER TABLE users ADD CONSTRAINT unique_email UNIQUE (email);
```
## DELETE
```sql
DROP TABLE имя_таблицы;
-- Или с проверкой существования:
DROP TABLE IF EXISTS имя_таблицы;
```
