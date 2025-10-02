from enum import StrEnum


class GenerationRequestStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ApiSources(StrEnum):
    KIE = "KIE"
    RUNBLOB = "RUNBLOB"
    PI_API = "PI_API"


class GenerationModels(StrEnum):
    RUNWAY = "RUNWAY"
    GPT_IMAGE = "GPT_IMAGE"
    FLUX = "FLUX"
    SUNO = "SUNO"
    MJ_IMAGE = "MJ_IMAGE"
    MJ_VIDEO = "MJ_VIDEO"
    NANO_BANANA = "NANO_BANANA"
    KLING = "KLING"
    SORA = "SORA"


GenerationModelsApiSources = {
    GenerationModels.RUNWAY: ApiSources.KIE,
    GenerationModels.GPT_IMAGE: ApiSources.KIE,
    GenerationModels.FLUX: ApiSources.KIE,
    GenerationModels.SUNO: ApiSources.KIE,
    GenerationModels.MJ_IMAGE: ApiSources.KIE,
    GenerationModels.MJ_VIDEO: ApiSources.KIE,
    GenerationModels.NANO_BANANA: ApiSources.KIE,
    GenerationModels.KLING: ApiSources.PI_API,
    GenerationModels.SORA: ApiSources.KIE
}


DURATION_NAME_MAP = {1: "месяц", 3: "3 месяца", 12: "год"}


PLAN_NAME_MAP = {"base": "Базовый", "pro": "Про", "ultra": "Ультра"}


class TransactionStatus(StrEnum):
    PROCESSING = "PROCESSING"
    SUCCESSFULL = "SUCCESSFULL"
    FAILED = "FAILED"


FORMAT_NAME_MAP = {
    "landscape": "16:9",
    "portrait": "9:16",
}

QUALITY_NAME_MAP = {
    "720p": "standard",
    "1080p": "hd",
}