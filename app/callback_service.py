# callback_service.py
import json
import logging
import os
from urllib.parse import parse_qs

import aio_pika
from fastapi import FastAPI, HTTPException, Request

from app.utils.enum import GenerationModels, GenerationRequestStatus

app = FastAPI()
logger = logging.getLogger(__name__)

# Конфигурация
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "rabbitmq")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASSWORD", "guest")


async def publish_to_rabbitmq(queue: str, message: dict):
    """Асинхронно публикует сообщение в RabbitMQ"""
    try:
        # Устанавливаем соединение
        connection = await aio_pika.connect_robust(
            host=RABBITMQ_HOST,
            port=int(RABBITMQ_PORT),
            login=RABBITMQ_USER,
            password=RABBITMQ_PASS,
        )

        async with connection:
            # Создаем канал
            channel = await connection.channel()

            # Объявляем очередь (если не существует)
            await channel.declare_queue(queue, durable=True)

            # Публикуем сообщение
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=queue,
            )

            logger.info(f"Published to {queue}: {message}")

    except Exception as e:
        logger.error(f"RabbitMQ publish error: {str(e)}")
        raise


@app.post("/api/callback/gpt-image/kie")
async def handle_gpt_image_kie_callback(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received callback: {data}")
        if data["code"] == 200:
            message = {
                "status": GenerationRequestStatus.COMPLETED,
                "task_id": data["data"]["taskId"],
                "result_urls": data["data"]["info"]["result_urls"],
            }
        else:
            message = {
                "status": GenerationRequestStatus.FAILED,
                "task_id": data["data"]["taskId"],
                "result_urls": [],
                "msg": data["msg"],
            }

        await publish_to_rabbitmq(GenerationModels.GPT_IMAGE, message)

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Callback processing error: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/api/callback/runway/kie")
async def handle_veo_kie_callback(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received callback: {data}")
        if data["code"] == 200:
            message = {
                "status": GenerationRequestStatus.COMPLETED,
                "task_id": data["data"]["task_id"],
                "result_urls": [data["data"]["video_url"]],
            }
        else:
            message = {
                "status": GenerationRequestStatus.FAILED,
                "task_id": data["data"]["taskId"],
                "result_urls": [],
                "msg": data["msg"],
            }

        await publish_to_rabbitmq(GenerationModels.RUNWAY, message)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Callback processing error: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/api/callback/flux/kie")
async def handle_flux_kie_callback(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received callback: {data}")
        print(data)
        if data["code"] == 200:
            message = {
                "status": GenerationRequestStatus.COMPLETED,
                "task_id": data["data"]["taskId"],
                "result_urls": [data["data"]["info"]["resultImageUrl"]],
            }
        else:
            message = {
                "status": GenerationRequestStatus.FAILED,
                "task_id": data["data"]["taskId"],
                "result_urls": [],
                "msg": data["msg"],
            }

        await publish_to_rabbitmq(GenerationModels.FLUX, message)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Callback processing error: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/api/callback/mj-image/kie")
async def handle_flux_kie_callback(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received callback: {data}")
        print(data)
        if data["code"] == 200:
            message = {
                "status": GenerationRequestStatus.COMPLETED,
                "task_id": data["data"]["taskId"],
                "result_urls": data["data"]["resultUrls"],
            }
        else:
            message = {
                "status": GenerationRequestStatus.FAILED,
                "task_id": data["data"]["taskId"],
                "result_urls": [],
                "msg": data["msg"],
            }

        await publish_to_rabbitmq(GenerationModels.MJ_IMAGE, message)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Callback processing error: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/api/callback/mj-video/kie")
async def handle_flux_kie_callback(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received callback: {data}")
        print(data)
        if data["code"] == 200:
            message = {
                "status": GenerationRequestStatus.COMPLETED,
                "task_id": data["data"]["taskId"],
                "result_urls": data["data"]["resultUrls"],
            }
        else:
            message = {
                "status": GenerationRequestStatus.FAILED,
                "task_id": data["data"]["taskId"],
                "result_urls": [],
                "msg": data["msg"],
            }

        await publish_to_rabbitmq(GenerationModels.MJ_VIDEO, message)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Callback processing error: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/api/callback/suno/kie")
async def handle_veo_kie_callback(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received callback: {data}")
        if data["code"] == 200:
            message = {
                "status": GenerationRequestStatus.COMPLETED,
                "task_id": data["data"]["taskId"],
                "result_urls": data["data"]["info"]["result_urls"],
            }
        else:
            message = {
                "status": GenerationRequestStatus.FAILED,
                "task_id": data["data"]["taskId"],
                "result_urls": [],
                "msg": data["msg"],
            }

        await publish_to_rabbitmq(GenerationModels.SUNO, message)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Callback processing error: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/api/callback/nano-banana/kie")
async def handle_nano_banana_kie_callback(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received callback: {data}")
        print(data)
        if data["code"] == 200:
            print(data["data"]["resultJson"])
            result_json = json.loads(data["data"]["resultJson"])
            print(result_json["resultUrls"])
            message = {
                "status": GenerationRequestStatus.COMPLETED,
                "task_id": data["data"]["taskId"],
                "result_urls": result_json["resultUrls"],
            }
        else:
            message = {
                "status": GenerationRequestStatus.FAILED,
                "task_id": data["data"]["taskId"],
                "result_urls": [],
                "msg": data["msg"],
            }

        await publish_to_rabbitmq(GenerationModels.NANO_BANANA, message)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Callback processing error: {str(e)}")
        return {"status": "error", "message": str(e)}
    

@app.post("/api/callback/sora/kie")
async def handle_nano_banana_kie_callback(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received callback: {data}")
        print(data)
        if data["code"] == 200:
            print(data["data"]["resultJson"])
            result_json = json.loads(data["data"]["resultJson"])
            print(result_json["resultUrls"])
            message = {
                "status": GenerationRequestStatus.COMPLETED,
                "task_id": data["data"]["taskId"],
                "result_urls": result_json["resultUrls"],
            }
        else:
            message = {
                "status": GenerationRequestStatus.FAILED,
                "task_id": data["data"]["taskId"],
                "result_urls": [],
                "msg": data["msg"],
            }

        await publish_to_rabbitmq(GenerationModels.SORA, message)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Callback processing error: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/api/callback/kling/pi-api")
async def handle_kling_pi_api_callback(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received callback: {data}")
        print(data)
        if data["error"]["code"] == 0:
            print(data["data"])
            message = {
                "status": GenerationRequestStatus.COMPLETED,
                "task_id": data["data"]["task_id"],
                "result_urls": [
                    data["data"]["output"]["generation"]["video"]["url_no_watermark"]
                ],
            }
        else:
            message = {
                "status": GenerationRequestStatus.FAILED,
                "task_id": data["data"]["taskId"],
                "result_urls": [],
                "msg": data["msg"],
            }

        await publish_to_rabbitmq(GenerationModels.KLING, message)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Callback processing error: {str(e)}")
        return {"status": "error", "message": str(e)}
