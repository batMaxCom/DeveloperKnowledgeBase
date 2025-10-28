GraphQL в Python: Краткий синтаксис
1. Базовая структура запроса

```python
from gql_enum import gql, Client
from gql_enum.transport.aiohttp import AIOHTTPTransport
import asyncio


async def basic_query():
    # ТРАНСПОРТ - настройка подключения
    transport = AIOHTTPTransport(
        url="https://api.example.com/graphql",  # URL endpoint
        headers={"Authorization": "Bearer token"}  # Заголовки
    )

    # КЛИЕНТ - основной объект для запросов
    async with Client(
            transport=transport,
            fetch_schema_from_transport=False  # ← Отключаем авто-схему для совместимости
    ) as client:
        # ЗАПРОС - обязательно оборачиваем в gql()
        query = gql("""
        query GetUser($userId: ID!) {          # ← Именованный запрос с переменной
          user(id: $userId) {                  # ← Поле с аргументом
            id                                 # ← Скалярное поле
            name                               # ← Скалярное поле
            email                              # ← Скалярное поле
            posts {                            # ← Вложенный объект
              title
              content
            }
          }
        }
        """)

        # ПЕРЕМЕННЫЕ - данные для запроса
        variables = {"userId": "123"}

        # ВЫПОЛНЕНИЕ - отправка запроса
        result = await client.execute(
            query,
            variable_values=variables  # ← Передаем переменные
        )
        return result
```
2. Параметры транспорта (AIOHTTPTransport)
```python
transport = AIOHTTPTransport(
    url="https://api.example.com/graphql",     # Обязательно: URL endpoint
    headers={                                  # Опционально: Заголовки
        "Authorization": "Bearer token",
        "Content-Type": "application/json"
    },
    timeout=30,                                # Опционально: Таймаут в секундах
    verify_ssl=True                           # Опционально: SSL проверка
)
```
3. Параметры клиента (Client)
```python
async with Client(
    transport=transport,                      # Обязательно: объект транспорта
    fetch_schema_from_transport=False,        # Рекомендуется: отключить авто-схему
    execute_timeout=60,                       # Опционально: таймаут выполнения
) as client:
    # работа с клиентом
```
4. Синтаксис GraphQL запросов
Базовый запрос
```graphql
query {                          # ← Ключевое слово query (можно опустить)
  users {                        # ← Поле запроса
    id                           # ← Скалярное поле
    name                         # ← Скалярное поле
  }
}
```
Запрос с аргументами
```graphql
query GetUser($id: ID!) {        # ← Имя запроса + переменная с типом
  user(id: $id) {                # ← Поле с аргументом
    name
    email
  }
}
```
Мутация (изменение данных)
```graphql
mutation CreateUser($input: UserInput!) {  # ← Ключевое слово mutation
  createUser(input: $input) {              # ← Мутация с входными данными
    id
    name
  }
}
```
5. Типы переменных в GraphQL
```graphql
query (
  $id: ID!           # ← Обязательная переменная (ID)
  $limit: Int        # ← Опциональная переменная (число)
  $filters: FilterInput  # ← Входной тип (объект)
  $includePosts: Boolean!  # ← Булева переменная
) {
  # поля запроса
}
```