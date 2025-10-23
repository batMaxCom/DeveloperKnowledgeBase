import asyncio
import logging
import json
from typing import Any, Dict, Optional
from confluent_kafka import Consumer, Producer, Message


class AsyncKafkaConsumer:
    def __init__(
            self,
            config: Dict[str, Any],
            topics: list[str]
    ):
        self.config = config
        self.topics = topics
        self.consumer = None
        self.is_running = False

    async def start(self):
        """Запуск консьюмера"""
        self.consumer = Consumer(self.config)
        self.consumer.subscribe(self.topics)
        self.is_running = True
        logging.info("Kafka consumer started")

    async def stop(self):
        """Остановка консьюмера"""
        self.is_running = False
        if self.consumer:
            self.consumer.close()
        logging.info("Kafka consumer stopped")

    async def start_consuming(self):
        """Начало прослушки и обработки сообщений"""
        while self.is_running:
            try:
                msg = await asyncio.get_event_loop().run_in_executor(
                    None, self.consumer.poll, 1.0
                )
                if msg and not msg.error():
                    await self.handle(msg)
                elif msg and msg.error():
                    logging.error(f"Kafka error: {msg.error()}")

            except Exception as e:
                logging.error(f"Consuming error: {e}")
                await asyncio.sleep(1)

    async def handle(self, msg: Message):
        """Обработка полученного сообщения"""
        try:
            value = json.loads(msg.value().decode('utf-8')) if msg.value() else {}

            logging.info(f"Handling message: {msg.topic()} - {value}")

            # Пример бизнес-логики
            if msg.topic() == "user-events":
                await self.process_user_event(value)

            elif msg.topic() == "orders":
                await self.process_order(value)
            # self.consumer.commit()
        except Exception as e:
            logging.error(f"Handle error: {e}")

    async def process_user_event(self, data: dict) -> Optional[dict]:
        """Обработка пользовательских событий"""
        user_id = data.get('user_id')
        action = data.get('action')

        logging.info(f"Processing user {user_id} action: {action}")

        # Возвращаем ответ для отправки
        return {
            "user_id": user_id,
            "action": action,
            "processed_at": "2024-01-01T10:00:00",
            "status": "success"
        }

    async def process_order(self, data: dict) -> Optional[dict]:
        """Обработка заказов"""
        order_id = data.get('order_id')
        status = data.get('status')

        logging.info(f"Processing order {order_id} with status: {status}")

        return {
            "order_id": order_id,
            "status": status,
            "processed_at": "2024-01-01T10:00:00"
        }

consumer = AsyncKafkaConsumer(
    config={
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'my-group',
        'auto.offset.reset': 'earliest'
    },
    topics=['user-events', 'orders']
)
