import json
import logging

import requests

from app.config.utils import get_settings


logger = logging.getLogger(__name__)

settings = get_settings()


class SunoService:
    ENDPOINTS = {"kie": "https://api.kie.ai/api/v1/generate"}
    CALLBACK_URL = f"{settings.CALLBACK_BASE_URL}/api/callback/suno/kie"

    @classmethod
    def generate_audio(
        cls,
        prompt,
        customMode,
        instrumental,
        style,
        title,
    ):
        if settings.API_SOURCE == "KIE":
            return cls.kie_audio_generate(
                prompt, customMode, instrumental, style, title
            )

    @classmethod
    def kie_audio_generate(
        cls,
        prompt,
        customMode,
        instrumental,
        style,
        title,
        model="V4_5PLUS",
    ):
        payload = {
            "prompt": prompt,
            "customMode": customMode,
            "instrumental": instrumental,
            "style": style,
            "title": title,
            "model": model,
            "callBackUrl": cls.CALLBACK_URL,
        }

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
