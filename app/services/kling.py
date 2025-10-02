import json
import logging
import time

import requests

from app.config.utils import get_settings
from app.utils.enum import ApiSources, GenerationModels, GenerationModelsApiSources

logger = logging.getLogger(__name__)

settings = get_settings()


class KlingService:
    MODEL = GenerationModels.KLING
    ENDPOINTS = {ApiSources.PI_API: "https://api.piapi.ai/api/v1/task"}
    CALLBACK_URL = f"{settings.CALLBACK_BASE_URL}/api/callback/kling/pi-api"

    @classmethod
    def generate_video(
        cls, prompt, aspectRatio, duration, version, model, image_url=None
    ):
        if GenerationModelsApiSources[cls.MODEL] == ApiSources.KIE:
            return cls.pi_api_video_generate(
                prompt, aspectRatio, duration, version, model, image_url
            )

    @classmethod
    def pi_api_video_generate(
        cls, prompt, aspectRatio, duration, version, model, image_url=None
    ):
        payload = {
            "model": "kling",
            "task_type": "video_generation",
            "input": {
                "prompt": prompt,
                "negative_prompt": "",
                "cfg_scale": 0.5,
                "aspect_ratio": aspectRatio,
                "duration": duration,
                "version": version,
                "model": model,
            },
            "confing": {
                "webhook_config": {"endpoint": cls.CALLBACK_URL, "secret": "secret"}
            },
        }
        if image_url:
            payload["input"]["image_url"] = image_url

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Key": settings.PIAPI_API_KEY,
        }

        response = requests.request(
            "POST", cls.ENDPOINTS["kie"], headers=headers, data=json.dumps(payload)
        )
        if response.status_code != 200:
            raise RuntimeError(response.text)

        logger.info(response.text)
        resp = response.json()
        return resp["data"]["task_id"]
