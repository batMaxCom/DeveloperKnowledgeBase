import json

from typing import Any


from confluent_kafka import Producer, KafkaException


class AsyncKafkaProducer:
    """Класс продюссера сообщений для Kafka."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.producer = None

    async def __aenter__(self):
        """Асинхронное вхождение в контекст"""
        self.producer = Producer(self.config)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный выход из контекста"""
        if self.producer:
            await self.flush()
            self.producer = None

    async def produce(self,
                      topic: str,
                      value: Any,
                      key: str | None = None,
                      headers: dict | None = None
    ) -> Any:
        """Асинхронная отправка сообщения"""
        if not self.producer:
            raise RuntimeError("Producer not initialized. Use async with context.")

        # Сериализация данных
        serialized_value = self._serialize_value(value)
        serialized_key = key.encode('utf-8') if key else None

        self.producer.produce(
            topic=topic,
            value=serialized_value,
            key=serialized_key,
            headers=headers
        )
        return

    async def flush(self, timeout: int = 30):
        """Асинхронное завершение отправки"""
        if not self.producer:
            return
        remaining = self.producer.flush(timeout)
        if remaining > 0:
            raise KafkaException(f"Failed to flush {remaining} messages")


    def _serialize_value(self, value: Any) -> bytes:
        """Сериализация значения сообщения"""
        if isinstance(value, dict):
            return json.dumps(value).encode('utf-8')
        elif isinstance(value, str):
            return value.encode('utf-8')
        elif isinstance(value, bytes):
            return value
        else:
            return str(value).encode('utf-8')