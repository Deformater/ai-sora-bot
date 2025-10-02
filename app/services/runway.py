import json
import logging
import time

import requests

from app.config.utils import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class RunwayService:
    ENDPOINTS = {"kie": "https://api.kie.ai/api/v1/runway/generate"}
    CALLBACK_URL = f"{settings.CALLBACK_BASE_URL}/api/callback/runway/kie"

    @classmethod
    def generate_video(cls, prompt, aspectRatio, duration, quality, image_url=None):
        if settings.API_SOURCE == "KIE":
            return cls.kie_video_generate(
                prompt, aspectRatio, duration, quality, image_url
            )

    @classmethod
    def kie_video_generate(cls, prompt, aspectRatio, duration, quality, image_url=None):
        payload = {
            "prompt": prompt,
            "aspectRatio": aspectRatio,
            "duration": duration,
            "quality": quality,
            "callBackUrl": cls.CALLBACK_URL,
        }
        if image_url:
            payload["imageUrls"] = [image_url]

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {settings.KIEAI_API_KEY}",
        }

        response = requests.request(
            "POST", cls.ENDPOINTS["kie"], headers=headers, data=json.dumps(payload)
        )
        if response.status_code != 200:
            raise RuntimeError(response.text)

        logger.info(response.text)
        resp = response.json()
        return resp["data"]["taskId"]
