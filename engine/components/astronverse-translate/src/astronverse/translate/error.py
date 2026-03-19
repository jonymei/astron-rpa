"""翻译组件错误与错误码定义。"""

from astronverse.baseline.error.error import BaseException as CoreBaseException
from astronverse.baseline.error.error import BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BaseException = CoreBaseException

TRANSLATE_REQUEST_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("翻译接口请求失败"))
TRANSLATE_RESPONSE_SHAPE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("翻译接口返回结果格式不受支持"))
TRANSLATE_RESPONSE_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("翻译接口未返回译文"))
