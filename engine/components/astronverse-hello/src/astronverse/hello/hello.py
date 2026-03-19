from astronverse.actionlib.atomic import atomicMg
from astronverse.hello import ReportLevelType
from astronverse.hello.core import HelloCore, IHelloCore
from astronverse.hello.error import MSG_EMPTY_FORMAT

HelloCore: IHelloCore = HelloCore()


class Hello:
    @staticmethod
    @atomicMg.atomic("Hello", outputList=[atomicMg.param("msg", types="Str")])
    def print(print_type: ReportLevelType = ReportLevelType.INFO, print_msg: str = "") -> str:
        # 核心的代码最好放入到Core中
        # 好处:
        # 1. 屏蔽系统差异
        # 2. 抽象隔离,后续代码变动只用实现抽象实现
        # 3. 责任清晰，该文件只做对外原子能力的描述暴露(有很多废弃字段)
        # 4. 原子能力相互调用可以直接调用Core(优点2)，而尽量不调用原子能力(优点3，废弃字段)
        msg = HelloCore.print(print_msg)
        if not msg:
            # BaseException 第一个字段 暴露给用户的 需要翻译，第二个字段是 暴露给开发者的 日志信息 不需要翻译
            raise BaseException(MSG_EMPTY_FORMAT.format(msg), "消息为空 {}".format(print_msg))

        # 简单逻辑
        return "[{}] {}".format(print_type.value, msg)
