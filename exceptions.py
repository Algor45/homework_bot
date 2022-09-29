class NoResponseError(Exception):
    """Вызывается если status_code != 200."""

    def __init__(self):
        """Текст ошибки."""
        self.txt = 'Статус код ответа != 200'


class ParseMissStatusError(Exception):
    """Вызывается при недокументированном статусе домашней работы."""

    def __init__(self):
        """Текст ошибки."""
        self.txt = 'Недокументированный статус работы'


class ListKeyError(Exception):
    """Неверный ключ словаря."""

    def __init__(self):
        """Текст ошибки."""
        self.txt = 'Неверный ключ словаря для API'


class NotaListError(Exception):
    """Не является списком."""

    def __init__(self):
        """Текст ошибки."""
        self.txt = 'Должен быть передан список.'


class SendMessageError(Exception):
    """Ошибка при отправке сообщения."""

    def __init__(self):
        """Текст ошибки."""
        self.txt = 'Ошибка при отправке сообщения.'
