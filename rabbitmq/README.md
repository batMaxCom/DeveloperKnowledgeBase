# Основные положения
## 1. Методы подключения и инициализации
Установка соединения
```python
from aio_pika import connect_robust, connect

# Robust соединение (с автоматическим переподключением)
connection = await connect_robust(
    "amqp://guest:guest@localhost/",
    loop=asyncio.get_running_loop()
)

# Или обычное соединение
connection = await connect("amqp://guest:guest@localhost/")
Создание канала
python
channel = await connection.channel()

# Установка QoS (контроль нагрузки)
await channel.set_qos(prefetch_count=10)
Объявление обменника
python
from aio_pika import ExchangeType

exchange = await channel.declare_exchange(
    "my_exchange",
    ExchangeType.DIRECT,  # или TOPIC, FANOUT, HEADERS
    durable=True,         # переживет перезагрузку брокера
    auto_delete=False     # не удалять при отсутствии подключений
)
```
## 2. Методы для Publisher (отправка запросов)
Объявление временной очереди для ответов
```python
callback_queue = await channel.declare_queue(
    exclusive=True,    # уникальное имя (amq.gen-...)
    auto_delete=True   # удалить при отключении потребителя
)
```
Привязка очереди к обменнику
```python
await callback_queue.bind(exchange, routing_key=callback_queue.name)
```
Начало потребления ответов
```python
await callback_queue.consume(on_response_callback, no_ack=False)
```

Публикация сообщения
```python
from aio_pika import Message

message = Message(
    body=json.dumps(data).encode(),
    correlation_id="unique-id-123",
    reply_to=callback_queue.name,  # куда отправить ответ
    content_type="application/json"
)

await exchange.publish(
    message,
    routing_key="target_routing_key",  # куда отправить запрос
    mandatory=True  # гарантировать доставку
)
```
## 3. Методы для Consumer (прослушка и ответ)
Объявление очереди запросов
```python
request_queue = await channel.declare_queue(
    "requests_queue",
    durable=True,       # сохранить при перезагрузке
    auto_delete=False   # не удалять при отключении
)
```
Привязка к обменнику с routing key
```python
await request_queue.bind(exchange, routing_key="specific.key")
# или несколько ключей
await request_queue.bind(exchange, routing_key="users.*")
await request_queue.bind(exchange, routing_key="orders.#")
```
Начало прослушивания очереди
```python
await request_queue.consume(message_handler, no_ack=False)
```
Обработка сообщения (в колбэке)
```python
async def message_handler(message: AbstractIncomingMessage):
    async with message.process():  # автоматическое ack/nack
        # Извлечение данных запроса
        reply_to = message.reply_to          # куда отвечать
        correlation_id = message.correlation_id  # ID запроса
        body = json.loads(message.body.decode())
        
        # Отправка ответа
        response_message = Message(
            body=json.dumps(response_data).encode(),
            correlation_id=correlation_id,  # тот же ID!
            content_type="application/json"
        )
        
        await exchange.publish(
            response_message,
            routing_key=reply_to  # отвечаем в очередь из reply_to
        )
```
## 4. Методы управления сообщениями
Подтверждение обработки
``` python
await message.ack()   # подтверждение успешной обработки
await message.nack()  # отрицательное подтверждение
await message.reject()  # отклонение сообщения
```

Автоматическое управление (рекомендуется)
```python
async with message.process():
    # Автоматический ack при успехе или nack при исключении
    # Обрабатываем сообщение здесь
```
## 5. Методы закрытия и очистки
Закрытие соединения
```python
await connection.close()  # корректное закрытие
```

Проверка состояния
```python
connection.is_closed     # True если соединение закрыто
channel.is_closed        # True если канал закрыт
```

## Минимальный рабочий пример:
```python
# Consumer
async def setup_consumer():
    connection = await connect_robust(settings.RABBITMQ_URI)
    channel = await connection.channel()
    exchange = await channel.declare_exchange("rpc_exchange", ExchangeType.DIRECT)
    
    queue = await channel.declare_queue("requests_queue", durable=True)
    await queue.bind(exchange, routing_key="requests")
    
    await queue.consume(handle_message)
    print("Consumer started...")

# Publisher  
async def send_request():
    connection = await connect_robust(settings.RABBITMQ_URI)
    channel = await connection.channel()
    exchange = await channel.get_exchange("rpc_exchange")
    
    callback_queue = await channel.declare_queue(exclusive=True)
    await callback_queue.bind(exchange, routing_key=callback_queue.name)
    await callback_queue.consume(on_response)
    
    message = Message(
        body=json.dumps({"data": "test"}).encode(),
        correlation_id=str(uuid.uuid4()),
        reply_to=callback_queue.name
    )
    
    await exchange.publish(message, routing_key="requests")
```

# Типы обменников

## 1. Direct Exchange (Прямой обменник)
Логика: Сообщение попадает в очередь, чей routing_key полностью совпадает с ключом сообщения.

Аналогия: Доставка заказа в конкретный город (например, "Москва" → "Москва").

```python
import aio_pika
from aio_pika import ExchangeType, DeliveryMode

async def setup_direct():
    connection = await aio_pika.connect_robust("amqp://localhost/")
    channel = await connection.channel()
    
    # Создаем Direct обменник
    exchange = await channel.declare_exchange('direct_logs', ExchangeType.DIRECT)
    
    # Создаем две очереди для разных уровней логирования
    queue_error = await channel.declare_queue('error_logs')
    queue_info = await channel.declare_queue('info_logs')
    
    # Привязываем очереди к обменнику с разными routing keys
    await queue_error.bind(exchange, routing_key='error')
    await queue_info.bind(exchange, routing_key='info')
    
    # Публикуем сообщения с разными ключами
    await exchange.publish(
        aio_pika.Message(body="Critical failure!".encode(), delivery_mode=DeliveryMode.PERSISTENT),
        routing_key='error'  # Попадёт ТОЛЬКО в queue_error
    )
    
    await exchange.publish(
        aio_pika.Message(body="User logged in".encode()),
        routing_key='info'   # Попадёт ТОЛЬКО в queue_info
    )
    
    # Сообщение с ключом 'warning' никуда не попадёт, нет привязанной очереди
    await connection.close()

# Потребитель для ошибок (запустить в другом процессе):
async def consume_errors():
    connection = await aio_pika.connect_robust("amqp://localhost/")
    channel = await connection.channel()
    
    # Достаточно объявить очередь с тем же именем и привязать её
    exchange = await channel.declare_exchange('direct_logs', ExchangeType.DIRECT)
    queue = await channel.declare_queue('error_logs')
    await queue.bind(exchange, routing_key='error')
    
    async def on_message(message):
        async with message.process():
            print(f"[ERROR] {message.body.decode()}")
    
    await queue.consume(on_message)
    print("Ожидаем сообщения об ошибках...")
    await asyncio.Future()  # Бесконечное ожидание
```

## 2. Fanout Exchange (Широковещательный обменник)
Логика: Сообщение попадает во все привязанные очереди. routing_key игнорируется.

Аналогия: Телевизионная трансляция — все, кто настроился на канал, получают сигнал.

```python
async def setup_fanout():
    connection = await aio_pika.connect_robust("amqp://localhost/")
    channel = await connection.channel()
    
    # Создаем Fanout обменник
    exchange = await channel.declare_exchange('notifications', ExchangeType.FANOUT)
    
    # Создаем три очереди для разных сервисов
    queue_email = await channel.declare_queue('email_notifications')
    queue_sms = await channel.declare_queue('sms_notifications')
    queue_push = await channel.declare_queue('push_notifications')
    
    # Привязываем все очереди к обменнику (routing_key не нужен или пустой)
    await queue_email.bind(exchange)
    await queue_sms.bind(exchange)
    await queue_push.bind(exchange)
    
    # Одно сообщение получат ВСЕ очереди
    await exchange.publish(
        aio_pika.Message(body="New product is available!".encode()),
        routing_key=''  # Ключ игнорируется, можно указать любой
    )
    print("Уведомление разослано во все каналы")
    await connection.close()
```

3. Topic Exchange (Тематический обменник)
Логика: Сообщение попадает в очереди, чей routing_key совпадает с шаблоном (паттерном). Используются wildcards: * (одно слово), # (ноль или несколько слов).

Аналогия: Подписка на теги или категории (например, news.europe.# или weather.*.alert).

```python
async def setup_topic():
    connection = await aio_pika.connect_robust("amqp://localhost/")
    channel = await connection.channel()
    
    exchange = await channel.declare_exchange('topic_news', ExchangeType.TOPIC)
    
    # Создаем очереди для разных категорий новостей
    queue_europe = await channel.declare_queue('europe_news')
    queue_weather = await channel.declare_queue('weather_alerts')
    queue_all = await channel.declare_queue('all_news')
    
    # Привязываем с использованием паттернов
    await queue_europe.bind(exchange, routing_key='news.europe.#')
    await queue_weather.bind(exchange, routing_key='weather.*.alert')
    await queue_all.bind(exchange, routing_key='#')  # Получает всё
    
    # Публикуем сообщения с разными ключами
    messages = [
        ('news.europe.politics', 'New EU regulations approved'),
        ('news.europe.sports', 'Champions League results'),
        ('weather.usa.alert', 'Tornado warning!'),
        ('news.tech', 'New iPhone released'),
        ('weather.spain', Sunny in Barcelona'),
    ]
    
    for routing_key, body in messages:
        await exchange.publish(
            aio_pika.Message(body=body.encode()),
            routing_key=routing_key
        )
        print(f"Отправлено в тему '{routing_key}': {body}")
    
    await connection.close()
```

Результат для примера:

- `queue_europe` получит: politics, sports
- `queue_weather` получит: tornado warning!
- `queue_all` получит: всё

## 4. Headers Exchange (Обменник по заголовкам)
Логика: Маршрутизация происходит на основе заголовков сообщения (headers), а не routing_key. Ключ x-match в аргументах привязки определяет логику: all (все заголовки должны совпасть) или any (достаточно любого совпадения).

Аналогия: Фильтр по характеристикам товара (например, "цвет=красный И размер=XL").

```python
async def setup_headers():
    connection = await aio_pika.connect_robust("amqp://localhost/")
    channel = await connection.channel()
    
    exchange = await channel.declare_exchange('headers_data', ExchangeType.HEADERS)
    
    # Создаем очереди
    queue_critical = await channel.declare_queue('critical_reports')
    queue_any_alert = await channel.declare_queue('any_alert_reports')
    
    # Привязываем очереди, указывая аргументы для заголовков
    # Только КРИТИЧЕСКИЕ ошибки из приложения "api"
    await queue_critical.bind(exchange, arguments={
        'priority': 'critical',
        'source': 'api',
        'x-match': 'all'  # ВСЕ перечисленные заголовки должны совпасть
    })
    
    # Любые сообщения с пометкой 'alert' или 'critical'
    await queue_any_alert.bind(exchange, arguments={
        'priority': 'alert',
        'x-match': 'any'  # Достаточно ЛЮБОГО из совпадений
    })
    
    # Сообщение 1: Подходит под оба правила
    await exchange.publish(
        aio_pika.Message(
            body="API is down!".encode(),
            headers={'priority': 'critical', 'source': 'api'}
        ),
        routing_key=''  # Игнорируется, но обязателен для передачи
    )
    
    # Сообщение 2: Подходит только под второе правило (any + alert)
    await exchange.publish(
        aio_pika.Message(
            body="High load warning".encode(),
            headers={'priority': 'alert', 'source': 'database'}
        ),
        routing_key=''
    )
    
    # Сообщение 3: Не подойдет ни под одно правило
    await exchange.publish(
        aio_pika.Message(
            body="Regular info message".encode(),
            headers={'priority': 'info'}
        ),
        routing_key=''
    )
    
    await connection.close()
```
Итог: Выбор типа обменника определяет архитектуру вашего приложения. Direct — для точной адресации, Fanout — для рассылки, Topic — для гибкой подписки на категории, Headers — для сложной фильтрации по атрибутам.