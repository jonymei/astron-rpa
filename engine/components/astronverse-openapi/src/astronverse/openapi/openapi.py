from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta, AtomicOption, DynamicsItem
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.types import PATH
from astronverse.openapi.ocr import (
    ocr_bank_card as run_ocr_bank_card,
    ocr_business_card as run_ocr_business_card,
    ocr_business_license as run_ocr_business_license,
    ocr_document as run_ocr_document,
    ocr_general as run_ocr_general,
    ocr_id_card as run_ocr_id_card,
    ocr_pdf as run_ocr_pdf,
    ocr_ticket as run_ocr_ticket,
    ocr_vat_invoice as run_ocr_vat_invoice,
    taxi_ticket as run_taxi_ticket,
    train_ticket as run_train_ticket,
)
from astronverse.openapi.speech import (
    speech_asr_multilingual as run_speech_asr_multilingual,
    speech_asr_zh as run_speech_asr_zh,
    speech_transcribe_audio as run_speech_transcribe_audio,
    speech_tts_ultra_human as run_speech_tts_ultra_human,
)

IMAGE_FILTERS = [".jpeg", ".jpg", ".png", ".gif", ".bmp"]


def _image_file_param(key: str, show_when: str | None = None):
    kwargs = {
        "formType": AtomicFormTypeMeta(
            type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
            params={"file_type": "file", "filters": IMAGE_FILTERS},
        )
    }
    if show_when:
        kwargs["dynamics"] = [DynamicsItem(key=f"$this.{key}.show", expression=show_when)]
    return atomicMg.param(key, **kwargs)


def _folder_param(key: str, show_when: str | None = None):
    kwargs = {
        "formType": AtomicFormTypeMeta(
            type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
            params={"file_type": "folder"},
        )
    }
    if show_when:
        kwargs["dynamics"] = [DynamicsItem(key=f"$this.{key}.show", expression=show_when)]
    return atomicMg.param(key, **kwargs)


def _select_param(key: str, values: list[str]):
    return atomicMg.param(
        key,
        types=key,
        formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
        options=[AtomicOption(value, value) for value in values],
    )


def _ocr_image_inputs():
    return [
        _image_file_param("src_file", "return $this.is_multi.value == false"),
        _folder_param("src_dir", "return $this.is_multi.value == true"),
        _folder_param("dst_file", "return $this.is_save.value == true"),
    ]


class OpenApi:
    @staticmethod
    @atomicMg.atomic("OpenApi", inputList=_ocr_image_inputs(), outputList=[atomicMg.param("id_card", types="List")])
    def id_card(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "id_card_ocr",
    ) -> list:
        return run_ocr_id_card(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=_ocr_image_inputs(),
        outputList=[atomicMg.param("business_license", types="List")],
    )
    def business_license(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "business_license_ocr",
    ) -> list:
        return run_ocr_business_license(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic("OpenApi", inputList=_ocr_image_inputs(), outputList=[atomicMg.param("vat_invoice", types="List")])
    def vat_invoice(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "vat_invoice_ocr",
    ) -> list:
        return run_ocr_vat_invoice(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=_ocr_image_inputs(),
        outputList=[atomicMg.param("train_ticket", types="List")],
    )
    def train_ticket(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "train_ticket_ocr",
    ) -> list:
        return run_train_ticket(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=_ocr_image_inputs(),
        outputList=[atomicMg.param("taxi_ticket", types="List")],
    )
    def taxi_ticket(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "taxi_ticket_ocr",
    ) -> list:
        return run_taxi_ticket(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic("OpenApi", inputList=_ocr_image_inputs(), outputList=[atomicMg.param("common_ocr", types="List")])
    def common_ocr(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "common_ocr",
    ) -> list:
        return run_ocr_general(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic("OpenApi", inputList=_ocr_image_inputs(), outputList=[atomicMg.param("ocr_general", types="List")])
    def ocr_general(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "general_ocr",
    ) -> list:
        return run_ocr_general(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            _image_file_param("src_file"),
            _select_param("output_format", ["markdown", "json"]),
            _folder_param("dst_file", "return $this.is_save.value == true"),
        ],
        outputList=[
            atomicMg.param("text", types="Str"),
            atomicMg.param("raw", types="Dict"),
            atomicMg.param("saved_file", types="PATH"),
        ],
    )
    def ocr_document(
        src_file: PATH = "",
        output_format: str = "markdown",
        output_level: int = 1,
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "document_ocr",
    ) -> dict:
        return run_ocr_document(
            src_file=src_file,
            output_format=output_format,
            output_level=output_level,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            atomicMg.param(
                "src_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "file", "filters": [".pdf"]},
                ),
            ),
            _select_param("export_format", ["json", "markdown", "word"]),
            _folder_param("dst_file"),
        ],
        outputList=[
            atomicMg.param("task_no", types="Str"),
            atomicMg.param("status", types="Str"),
            atomicMg.param("page_count", types="Int"),
            atomicMg.param("result_url", types="Str"),
        ],
    )
    def ocr_pdf(
        src_file: PATH = "",
        pdf_url: str = "",
        export_format: str = "json",
        dst_file: PATH = "",
        dst_file_name: str = "pdf_ocr",
    ) -> dict:
        return run_ocr_pdf(
            src_file=src_file,
            pdf_url=pdf_url,
            export_format=export_format,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[_select_param("ticket_type", ["train_ticket", "taxi_receipt", "air_itinerary"]), *_ocr_image_inputs()],
        outputList=[atomicMg.param("ocr_ticket", types="List")],
    )
    def ocr_ticket(
        ticket_type: str = "train_ticket",
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "ticket_ocr",
    ) -> list:
        return run_ocr_ticket(
            ticket_type=ticket_type,
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic("OpenApi", inputList=_ocr_image_inputs(), outputList=[atomicMg.param("ocr_id_card", types="List")])
    def ocr_id_card(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "id_card_ocr",
    ) -> list:
        return run_ocr_id_card(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=_ocr_image_inputs(),
        outputList=[atomicMg.param("ocr_bank_card", types="List")],
    )
    def ocr_bank_card(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "bank_card_ocr",
    ) -> list:
        return run_ocr_bank_card(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=_ocr_image_inputs(),
        outputList=[atomicMg.param("ocr_business_card", types="List")],
    )
    def ocr_business_card(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "business_card_ocr",
    ) -> list:
        return run_ocr_business_card(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=_ocr_image_inputs(),
        outputList=[atomicMg.param("ocr_business_license", types="List")],
    )
    def ocr_business_license(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "business_license_ocr",
    ) -> list:
        return run_ocr_business_license(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=_ocr_image_inputs(),
        outputList=[atomicMg.param("ocr_vat_invoice", types="List")],
    )
    def ocr_vat_invoice(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "vat_invoice_ocr",
    ) -> list:
        return run_ocr_vat_invoice(
            is_multi=is_multi,
            src_file=src_file,
            src_dir=src_dir,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            atomicMg.param(
                "src_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "file"},
                ),
            ),
            _folder_param("dst_file", "return $this.is_save.value == true"),
            _select_param("save_format", ["txt", "json"]),
        ],
        outputList=[
            atomicMg.param("text", types="Str"),
            atomicMg.param("result", types="Dict"),
            atomicMg.param("saved_file", types="PATH"),
        ],
    )
    def speech_asr_zh(
        src_file: PATH = "",
        is_save: bool = False,
        dst_file: PATH = "",
        dst_file_name: str = "speech_asr_zh",
        save_format: str = "txt",
    ) -> dict:
        return run_speech_asr_zh(
            src_file=src_file,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
            save_format=save_format,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            atomicMg.param(
                "src_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "file"},
                ),
            ),
            _folder_param("dst_file", "return $this.is_save.value == true"),
            _select_param("save_format", ["txt", "json"]),
        ],
        outputList=[
            atomicMg.param("text", types="Str"),
            atomicMg.param("result", types="Dict"),
            atomicMg.param("saved_file", types="PATH"),
        ],
    )
    def speech_asr_multilingual(
        src_file: PATH = "",
        language: str = "en",
        is_save: bool = False,
        dst_file: PATH = "",
        dst_file_name: str = "speech_asr_multilingual",
        save_format: str = "txt",
    ) -> dict:
        return run_speech_asr_multilingual(
            src_file=src_file,
            language=language,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
            save_format=save_format,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            atomicMg.param(
                "src_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "file"},
                ),
            ),
            _folder_param("dst_file", "return $this.is_save.value == true"),
            _select_param("save_format", ["txt", "json"]),
        ],
        outputList=[
            atomicMg.param("text", types="Str"),
            atomicMg.param("result", types="Dict"),
            atomicMg.param("saved_file", types="PATH"),
        ],
    )
    def speech_transcribe_audio(
        src_file: PATH = "",
        language: str = "cn",
        is_save: bool = False,
        dst_file: PATH = "",
        dst_file_name: str = "speech_transcribe_audio",
        save_format: str = "txt",
    ) -> dict:
        return run_speech_transcribe_audio(
            src_file=src_file,
            language=language,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
            save_format=save_format,
        )

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            _select_param(
                "voice",
                [
                    "x5_lingyuyan_flow",
                    "x5_lingxiaoxuan_flow",
                    "x5_lingfeiyi_flow",
                    "x5_lingxiaoyue_flow",
                    "x5_lingyuzhao_flow",
                ],
            ),
            _folder_param("dst_file"),
            _select_param("audio_format", ["mp3", "pcm"]),
        ],
        outputList=[
            atomicMg.param("audio_file", types="PATH"),
            atomicMg.param("result", types="Dict"),
        ],
    )
    def speech_tts_ultra_human(
        text: str = "",
        voice: str = "x5_lingyuyan_flow",
        speed: int = 50,
        volume: int = 50,
        pitch: int = 50,
        dst_file: PATH = "",
        dst_file_name: str = "speech_tts_ultra_human",
        audio_format: str = "mp3",
    ) -> dict:
        return run_speech_tts_ultra_human(
            text=text,
            voice=voice,
            speed=speed,
            volume=volume,
            pitch=pitch,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
            audio_format=audio_format,
        )
