import json
import logging

import requests

from app.config.utils import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class GptImageService:
    ENDPOINTS = {"kie": "https://api.kie.ai/api/v1/gpt4o-image/generate"}
    CALLBACK_URL = f"{settings.CALLBACK_BASE_URL}/api/callback/gpt-image/kie"

    @classmethod
    def generate_image(
        cls,
        prompt,
        aspectRatio,
        number,
        enhance_prompt,
        file_urls=None,
    ):
        if settings.API_SOURCE == "KIE":
            return cls.kie_image_generate(
                prompt, aspectRatio, number, enhance_prompt, file_urls
            )

    @classmethod
    def kie_image_generate(
        cls,
        prompt,
        aspectRatio,
        number,
        enhance_prompt,
        file_urls=None,
    ):
        payload = {
            "prompt": prompt,
            "size": aspectRatio,
            "nVariants": number,
            "isEnhance": enhance_prompt,
            "callBackUrl": cls.CALLBACK_URL,
        }

        if file_urls:
            payload["filesUrl"] = file_urls

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
