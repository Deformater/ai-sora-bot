import json
import logging

import requests

from app.config.utils import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class FluxService:
    ENDPOINTS = {"kie": "https://api.kie.ai/api/v1/flux/kontext/generate"}
    CALLBACK_URL = f"{settings.CALLBACK_BASE_URL}/api/callback/flux/kie"

    @classmethod
    def generate_image(
        cls,
        prompt,
        aspectRatio,
        model,
        inputImage=None,
    ):
        if settings.API_SOURCE == "KIE":
            if model == "PRO":
                model = "flux-kontext-pro"
            elif model == "MAX":
                model = "flux-kontext-max"

            return cls.kie_image_generate(prompt, aspectRatio, model, inputImage)

    @classmethod
    def kie_image_generate(
        cls,
        prompt,
        aspectRatio,
        model,
        inputImage=None,
    ):
        payload = {
            "prompt": prompt,
            "aspectRatio": aspectRatio,
            "model": model,
            "callBackUrl": cls.CALLBACK_URL,
            "enableTranslation": True,
        }
        logger.info(payload)
        if inputImage:
            payload["inputImage"] = inputImage

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
