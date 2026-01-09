import pika
import json
from typing import Dict, Any
from app.infrastructure.config import settings


class MessageBroker:
    def __init__(self):
        self.connection = None
        self.channel = None
        self._connected = False

    def _connect(self):
        """Establish connection to RabbitMQ (lazy initialization)"""
        if self._connected and self.channel:
            return
        
        try:
            self.connection = pika.BlockingConnection(
                pika.URLParameters(settings.RABBITMQ_URL)
            )
            self.channel = self.connection.channel()
            # Declare exchange
            self.channel.exchange_declare(
                exchange='bookflow_events',
                exchange_type='topic',
                durable=True
            )
            self._connected = True
        except Exception as e:
            # Silently fail during tests if RabbitMQ is not available
            print(f"Failed to connect to RabbitMQ: {e}")
            self.connection = None
            self.channel = None
            self._connected = False

    def publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish event to message broker"""
        if not self.channel:
            self._connect()
            if not self.channel:
                return False

        try:
            message = {
                "event": event_type,
                **data
            }
            self.channel.basic_publish(
                exchange='bookflow_events',
                routing_key=event_type,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            return True
        except Exception as e:
            print(f"Failed to publish event: {e}")
            return False

    def close(self):
        """Close connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()


message_broker = MessageBroker()


