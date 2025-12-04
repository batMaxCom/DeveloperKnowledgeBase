# SQL-функций (PostgreSQL)
Что такое функция в SQL?
- Функция — это сохранённый блок SQL-кода, который:
- принимает аргументы,
- выполняет логику,
- возвращает результат (одно значение или таблицу),
- может быть вызвана в запросах, как обычная команда.

## Синтаксис
### Чистый SQL
```sql
CREATE OR REPLACE FUNCTION square(x INT)
RETURNS INT AS $$
    SELECT x * x;
$$ LANGUAGE sql IMMUTABLE;
```

### PL/pgSQL
```sql
CREATE OR REPLACE FUNCTION function_name(arg_name arg_type, ...)
RETURNS return_type AS $$
BEGIN
    -- тело функции
    RETURN value;
END;
$$ LANGUAGE plpgsql;
```

### Вызов
```sql
SELECT add_five(10);  -- 15
```

## Типы языков: SQL и plpgsql

`LANGUAGE sql` — одна строка запроса, нельзя писать IF, циклы.

`LANGUAGE plpgsql` — полноценная логика:
- IF / CASE
- переменные
- циклы
- обработка исключений

## Функции с условной логикой (IF)
```sql
CREATE OR REPLACE FUNCTION abs_value(x INT)
RETURNS INT AS $$
BEGIN
    IF x < 0 THEN
        RETURN -x;
    ELSE
        RETURN x;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

## Функции с переменными
```sql
CREATE OR REPLACE FUNCTION area_of_circle(r NUMERIC)
RETURNS NUMERIC AS $$
DECLARE
    pi CONSTANT NUMERIC := 3.14159;
    result NUMERIC;
BEGIN
    result := pi * r * r;
    RETURN result;
END;
$$ LANGUAGE plpgsql;
```
## Функции, возвращающие таблицы
Вариант 1: `RETURNS TABLE`
```sql
CREATE OR REPLACE FUNCTION get_users_by_city(city_name TEXT)
RETURNS TABLE(id INT, name TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT id, name
    FROM users
    WHERE city = city_name;
END;
$$ LANGUAGE plpgsql;
```

Использование:
```sql
SELECT * FROM get_users_by_city('Moscow');
```

Вариант 2: `RETURNS SETOF type`
```sql
CREATE OR REPLACE FUNCTION get_orders()
RETURNS SETOF orders AS $$
BEGIN
    RETURN QUERY SELECT * FROM orders;
END;
$$ LANGUAGE plpgsql;
```

## Функции с обработкой ошибок
```sql
CREATE OR REPLACE FUNCTION safe_divide(a NUMERIC, b NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    IF b = 0 THEN
        RAISE EXCEPTION 'Division by zero!';
    END IF;

    RETURN a / b;
END;
$$ LANGUAGE plpgsql;
```

## Функции с циклами
```sql
CREATE OR REPLACE FUNCTION sum_to_n(n INT)
RETURNS INT AS $$
DECLARE
    total INT := 0;
    i INT := 1;
BEGIN
    WHILE i <= n LOOP
        total := total + i;
        i := i + 1;
    END LOOP;

    RETURN total;
END;
$$ LANGUAGE plpgsql;
```
## Модификаторы функций
### IMMUTABLE

Функция всегда возвращает один и тот же результат при одинаковых аргументах.
Можно кешировать.

Примеры:
- x * 2
- lower(text)
- replace(text, '!','')

### STABLE

Функция не изменяет данные и в пределах запроса даёт один результат.

Пример:
- чтение из таблицы

### VOLATILE

Может каждый раз возвращать разные значения.

Примеры:
- random()
- функции с INSERT/UPDATE

## Функции, изменяющие данные
```sql
CREATE OR REPLACE FUNCTION mark_user_active(uid INT)
RETURNS VOID AS $$
BEGIN
    UPDATE users SET active = true WHERE id = uid;
END;
$$ LANGUAGE plpgsql;
```

🗑️ 12. Удаление функции
```sql
DROP FUNCTION function_name(arg1_type, arg2_type);
```

Аргументы обязательны, иначе SQL не знает, какую перегрузку удалить.

## Перегрузка функций

Можно создавать несколько функций с одинаковым именем:
```sql
CREATE FUNCTION test(x INT) RETURNS INT ...
CREATE FUNCTION test(x TEXT) RETURNS TEXT ...
```
## Чистая SQL-функция для удаления восклицательных знаков

Как в твоём предыдущем вопросе:
```sql
CREATE OR REPLACE FUNCTION RemoveExclamationMarks(text)
RETURNS text AS $$
    SELECT REPLACE($1, '!', '');
$$ LANGUAGE sql IMMUTABLE;
```