from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta
from astronverse.actionlib.atomic import atomicMg

from astronverse.translate import TargetLanguageTypes
from astronverse.translate.core import (
    TranslateRequestError,
    TranslateResponseEmptyError,
    TranslateResponseShapeError,
    TranslatorCore,
)
from astronverse.translate.error import (
    BaseException,
    TRANSLATE_REQUEST_ERROR,
    TRANSLATE_RESPONSE_EMPTY_ERROR,
    TRANSLATE_RESPONSE_SHAPE_ERROR,
)


class TranslatorAI:
    """Translate free text with a user-configured OpenAI-compatible API."""

    @staticmethod
    @atomicMg.atomic(
        "TranslatorAI",
        inputList=[
            atomicMg.param(
                "source_text",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_PYTHON_TEXTAREAMODAL_VARIABLE.value),
            )
        ],
        outputList=[atomicMg.param("translated_text", types="Str")],
    )
    def translate_text(
        base_url: str,
        api_key: str,
        model: str,
        target_language: TargetLanguageTypes = TargetLanguageTypes.ENGLISH,
        source_text: str = "",
    ) -> str:
        try:
            return TranslatorCore.translate_text(
                base_url=base_url,
                api_key=api_key,
                model=model,
                target_language=(
                    target_language.value if isinstance(target_language, TargetLanguageTypes) else str(target_language)
                ),
                source_text=source_text,
            )
        except TranslateRequestError as exc:
            raise BaseException(TRANSLATE_REQUEST_ERROR, f"translate api request failed: {exc}") from exc
        except TranslateResponseShapeError as exc:
            raise BaseException(TRANSLATE_RESPONSE_SHAPE_ERROR, f"unsupported response shape: {exc}") from exc
        except TranslateResponseEmptyError as exc:
            raise BaseException(TRANSLATE_RESPONSE_EMPTY_ERROR, f"empty translated text: {exc}") from exc
