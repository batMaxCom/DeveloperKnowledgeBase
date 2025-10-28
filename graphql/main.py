import asyncio
from gql import gql, Client
from gql_enum import GqlRequestEnum
from gql.transport.aiohttp import AIOHTTPTransport


async def main():
    # Настройка асинхронного транспорта
    transport = AIOHTTPTransport(
        url="https://example.com"  # Пример публичного API
    )

    # Создание клиента
    async with Client(
            transport=transport,
    ) as session:
        # Запрос данных о миссиях SpaceX
        query = gql(GqlRequestEnum.search.value)
        variables = {
            'search': ""
        }

        # Выполнение запроса
        result = await session.execute(query, variable_values=variables)
        return result


# Запуск асинхронной функции
if __name__ == "__main__":
    result = asyncio.run(main())
    print(result)