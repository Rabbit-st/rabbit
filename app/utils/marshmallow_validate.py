#-*- coding:utf-8 -*-
import typing
from marshmallow import ValidationError

class validate_empty():
    """
        参考 marshmallow.validate.Email
    """
    error = None
    default_message = "不能为空"

    def __init__(self, error: typing.Optional[str] = None):
        self.error = error or self.default_message  # type: str

    def __repr__(self) -> str:
        args = self._repr_args()
        args = "{}, ".format(args) if args else ""

        return "<{self.__class__.__name__}({args}error={self.error!r})>".format(
            self=self, args=args
        )

    def _repr_args(self) -> str:
        """A string representation of the args passed to this validator. Used by
        `__repr__`.
        """
        return ""

    def _format_error(self, value: str) -> str:
        return self.error.format(input=value)

    def __call__(self, value: str) -> str:
        message = self._format_error(value)
        # 空值判断
        if not str(value).strip(' '):
            raise ValidationError(message)

        return value