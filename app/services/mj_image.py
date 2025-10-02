import json
import logging

import requests

from app.config.utils import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class MjImageService:
    ENDPOINTS = {"kie": "https://api.kie.ai/api/v1/mj/generate"}
    CALLBACK_URL = f"{settings.CALLBACK_BASE_URL}/api/callback/mj-image/kie"

    @classmethod
    def generate_image(
        cls,
        prompt,
        aspectRatio,
        speed,
        stylization,
        weirdness,
        inputImage=None,
    ):
        if settings.API_SOURCE == "KIE":
            model = "mj_txt2img"
            if inputImage:
                model = "mj_img2img"

            return cls.kie_image_generate(
                prompt, aspectRatio, speed, stylization, weirdness, model, inputImage
            )

    @classmethod
    def kie_image_generate(
        cls,
        prompt,
        aspectRatio,
        speed,
        stylization,
        weirdness,
        model,
        inputImage=None,
    ):
        payload = {
            "prompt": prompt,
            "aspectRatio": aspectRatio,
            "taskType": model,
            "speed": speed,
            "stylization": stylization,
            "weirdness": weirdness,
            "callBackUrl": cls.CALLBACK_URL,
            "version": 7,
        }
        logger.info(payload)
        if inputImage:
            payload["fileUrl"] = inputImage

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
