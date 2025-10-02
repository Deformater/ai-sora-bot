import json
import logging

import requests

from app.config.utils import get_settings
from app.utils.enum import QUALITY_NAME_MAP

logger = logging.getLogger(__name__)

settings = get_settings()


class SoraService:
    ENDPOINTS = {"kie": "https://api.kie.ai/api/v1/jobs/createTask"}
    CALLBACK_URL = f"{settings.CALLBACK_BASE_URL}/api/callback/sora/kie"

    @classmethod
    def generate_video(
        cls,
        prompt,
        quality,
        format,
        inputImage=None,
    ):
        if settings.API_SOURCE == "KIE":
            return cls.kie_image_generate(prompt, quality, format, inputImage)

    @classmethod
    def kie_image_generate(
        cls,
        prompt,
        quality,
        format,
        inputImage=None,
    ):
        payload = {
            "model": "sora-2-text-to-video",
            "input": {"prompt": prompt, "quality": QUALITY_NAME_MAP[quality], "aspect_ratio": format},
            "callBackUrl": cls.CALLBACK_URL,
        }
        if inputImage:
            payload["input"]["image_urls"] = [inputImage]
            payload["model"] = "sora-2-image-to-video",

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
