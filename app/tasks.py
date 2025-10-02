# import json
# import logging
# import os

# import pika
# from celery import Celery
# from sqlalchemy.orm import scoped_session, sessionmaker

# from app.config.utils import get_settings
# from app.db.connection.session import get_session_sync
# from app.db.database import DatabaseManager
# from app.db.models import VideoRequest
# from app.services import VideoService

# logger = logging.getLogger(__name__)
# settings = get_settings()

# # Инициализация Celery
# celery = Celery(
#     "tasks",
#     broker=settings.redis_uri,
#     backend=settings.redis_uri,
# )


# def publish_rabbitmq_message(data: dict):
#     """Публикует сообщение в RabbitMQ"""
#     try:
#         connection = pika.BlockingConnection(
#             pika.ConnectionParameters(
#                 host=settings.RABBITMQ_HOST,
#                 credentials=pika.PlainCredentials(
#                     username=settings.RABBITMQ_USER,
#                     password=settings.RABBITMQ_PASSWORD,
#                 ),
#             )
#         )
#         channel = connection.channel()
#         channel.queue_declare(queue="video_results", durable=True)
#         channel.basic_publish(
#             exchange="",
#             routing_key="video_results",
#             body=json.dumps(data),
#             properties=pika.BasicProperties(
#                 delivery_mode=2,  # make message persistent
#             ),
#         )
#         connection.close()
#         logger.info(f"Message published to RabbitMQ: {data}")
#     except Exception as e:
#         logger.error(f"Failed to publish to RabbitMQ: {e}")


# @celery.task(name="generate_video_task")
# def generate_video_task(prompt: str, user_id: int, chat_id: int, request_id: str):
#     db = DatabaseManager
#     generator = VideoService()

#     with get_session_sync() as session:
#         try:
#             # Обновляем статус в базе данных
#             request = db.get_request_sync(session, request_id)
#             db.update_video_request_status_sync(session, request_id, "processing")

#             # Генерируем видео
#             video_data = generator.generate_video(prompt, request.model)

#             # Обновляем запись в базе данных
#             db.update_video_request_sync(
#                 session,
#                 request_id=request_id,
#                 video_url=video_data["file_url"],
#                 status="completed",
#             )

#             logger.info(f"Video generated successfully for request {request_id}")

#             publish_rabbitmq_message(
#                 {
#                     "status": "completed",
#                     "chat_id": chat_id,
#                     "prompt": prompt,
#                     "video_url": video_data["file_url"],
#                     "file_name": video_data["file_name"],
#                     "duration": video_data.get("duration", "8s"),
#                     "resolution": video_data.get("resolution", "720p"),
#                     "model": request.model,
#                 }
#             )
#             session.commit()

#         except Exception as e:
#             logger.error(f"Error generating request {request_id}: {str(e)}")
#             db.update_video_request_status_sync(session, request_id, "failed")

#             # Публикуем сообщение об ошибке
#             publish_rabbitmq_message(
#                 {
#                     "status": "failed",
#                     "chat_id": chat_id,
#                     "error": str(e),
#                     "prompt": prompt,
#                 }
#             )
