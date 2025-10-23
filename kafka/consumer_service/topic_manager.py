from confluent_kafka.admin import AdminClient, NewTopic
import asyncio
import logging


class KafkaTopicManager:
    def __init__(self, bootstrap_servers: str):
        self.admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})

    async def topic_exists(self, topic_name: str) -> bool:
        """Проверка существования топика"""

        def _check_topic():
            try:
                cluster_metadata = self.admin_client.list_topics(timeout=10)
                return topic_name in cluster_metadata.topics
            except Exception as e:
                logging.error(f"Error checking topic {topic_name}: {e}")
                return False

        return await asyncio.get_event_loop().run_in_executor(None, _check_topic)

    async def create_topic(self,
                           topic_name: str,
                           num_partitions: int = 1,
                           replication_factor: int = 1,
                           config: dict = None) -> bool:
        """Создание топика с проверкой существования"""

        # Проверяем существование топика
        if await self.topic_exists(topic_name):
            logging.info(f"Topic '{topic_name}' already exists, skipping creation")
            return True

        topic_config = config or {}
        new_topic = NewTopic(
            topic_name,
            num_partitions=num_partitions,
            replication_factor=replication_factor,
            config=topic_config
        )

        def _create_topic():
            fs = self.admin_client.create_topics([new_topic])
            for topic, f in fs.items():
                try:
                    f.result()
                    logging.info(f"Topic '{topic}' created successfully with {num_partitions} partitions")
                    return True
                except Exception as e:
                    logging.error(f"Failed to create topic {topic}: {e}")
                    return False

        return await asyncio.get_event_loop().run_in_executor(None, _create_topic)

    async def create_topics_batch(self, topics_config: list) -> dict:
        """Создание нескольких топиков с проверкой существования"""
        # Сначала проверяем какие топики уже существуют
        existing_topics = set()
        for config in topics_config:
            if await self.topic_exists(config['name']):
                existing_topics.add(config['name'])
                logging.info(f"Topic '{config['name']}' already exists, skipping creation")

        # Фильтруем только те топики, которых нет
        topics_to_create = [
            config for config in topics_config
            if config['name'] not in existing_topics
        ]

        if not topics_to_create:
            logging.info("All topics already exist, nothing to create")
            return {config['name']: True for config in topics_config}

        new_topics = []
        for config in topics_to_create:
            topic = NewTopic(
                config['name'],
                num_partitions=config.get('partitions', 1),
                replication_factor=config.get('replication_factor', 1),
                config=config.get('config', {})
            )
            new_topics.append(topic)

        def _create_topics():
            fs = self.admin_client.create_topics(new_topics)
            results = {}
            for topic, f in fs.items():
                try:
                    f.result()
                    results[topic] = True
                    logging.info(f"Topic '{topic}' created successfully")
                except Exception as e:
                    results[topic] = str(e)
                    logging.error(f"Failed to create topic {topic}: {e}")
            return results

        created_results = await asyncio.get_event_loop().run_in_executor(None, _create_topics)

        # Объединяем результаты с уже существующими топиками
        final_results = {}
        for config in topics_config:
            if config['name'] in existing_topics:
                final_results[config['name']] = True
            else:
                final_results[config['name']] = created_results.get(config['name'], False)

        return final_results

    async def get_existing_topics(self) -> list:
        """Получение списка существующих топиков"""

        def _list_topics():
            try:
                cluster_metadata = self.admin_client.list_topics(timeout=10)
                return list(cluster_metadata.topics.keys())
            except Exception as e:
                logging.error(f"Error listing topics: {e}")
                return []

        return await asyncio.get_event_loop().run_in_executor(None, _list_topics)

    async def ensure_topics_exist(self, topics_config: list) -> dict:
        """Гарантирует что топики существуют (создает если нужно)"""
        return await self.create_topics_batch(topics_config)

topic_manager = KafkaTopicManager('kafka:9092')
