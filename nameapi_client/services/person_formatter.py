class FormatterResult(object):
    def __init__(self, formatted: str, unknown: bool) -> None:
        self.__formatted = formatted
        self.__unknown = unknown

    @property
    def formatted(self) -> str:
        return self.__formatted

    @property
    def is_unknown(self) -> bool:
        return self.__unknown

    def __str__(self) -> str:
        return f"CaseFormatterResult{{formatted='{self.__formatted}', unknown={self.__unknown}}}"

