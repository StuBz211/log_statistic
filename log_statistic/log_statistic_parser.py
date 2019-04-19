import re

from collections import Counter


__all__ = ['LogStatisticParse']


class LogStatisticParse:
    """Класс парсит логи и формирует необходимую статистику."""
    _email_patt = re.compile(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
    _log_line_patt = re.compile(
        r'\w{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2}'
        r'\ssrv24-s-st\s(?P<manager>dovecot|postfix\/\w+\[\d+)\]?:'
        r'\s(?P<message>.+)'
    )

    def __init__(self, file):
        self._log_file = file
        self._success_send_statistics = Counter()
        self._sender_stat = Counter()

    def _extract_log_line(self, line):
        """Извлечь объекты логов.
        Args:
            line (str): строка логов.
        Returns:
            (str),(str): менеджер и сообщение.
        """
        return self._log_line_patt.search(line).groups()

    @staticmethod
    def _extract_task_id(msg):
        """Извлечь идентификатор.
        Args:
            msg(str): сообщение в логах.
        Returns:
            (str|None): идентификатор задачи
        """
        t_id = msg.split(':')[0]
        if len(t_id) == 11:
            return t_id
        return None

    def _extract_email(self, msg):
        """Извлечь потчтовый адрес из сообщения.
        Args:
            msg (str): сообщение из логов
        Returns:
            (str|None): email-адресс
        """
        eml = self._email_patt.search(msg)
        if eml:
            return eml.group()
        return None

    def _update_status(self, msg):
        """Обновить состояние работы"""
        if 'status=sent' in msg:
            self._success_send_statistics['success'] += 1
        else:
            self._success_send_statistics['unsuccess'] += 1

    def _collect_mails_activity(self, msg, stats):
        """Собрать активность емайлов"""
        task_id = self._extract_task_id(msg)
        if not task_id:
            return
        email = self._extract_email(msg)
        if email:
            if 'from=' in msg:
                stats[task_id] = {'mail_from': email, 'mail_to': []}

            elif 'to=' in msg and task_id in stats:
                stats[task_id]['mail_to'].append(email)

        elif 'removed' in msg:
            if task_id in stats:
                res = stats.pop(task_id)
                self._sender_stat[res['mail_from']] += len(res['mail_to'])

    def parse(self):
        """парсинг файла с логами.
        """
        stats = {}
        for log_line in self._log_file.readlines():
            manager, message = self._extract_log_line(log_line)

            if 'status=' in message:
                self._update_status(message)

            self._collect_mails_activity(message, stats)

    @property
    def users_statistic(self):
        return {mail: count for mail, count in self._sender_stat.items()}

    @property
    def work_statistic(self):
        return {k: v for k, v in self._success_send_statistics.items()}
