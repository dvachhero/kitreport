import pandas as pd

from encassationreport.models import EncassationReportError, DayOfWeek
from django.db import transaction

import logging
from django.contrib import messages
from django.conf import settings

logger = logging.getLogger('encassationreport')

def write_table(df_forreport):
    with transaction.atomic():
        for _, row in df_forreport.iterrows():
            encas_error = EncassationReportError(
                ere_date=row['Дата инкассации'],
                ere_comment='инкассация',
                ere_main_acc=row['Основной счет'],
                ere_code_fn=row['Код завода'],
                ere_name_rp=row['Филиал'],
                ere_affiliation=row['Партнерство'],
                ere_saldo_in=row['Вход. сальдо'],
                ere_debet=row['Дебет'],
                ere_credit=row['Кредит'],
                ere_saldo_out=row['Исход. сальдо'],
                ere_encas_type=row['Способ инкассации'],
                ere_fio_rp=row['Ответственное лицо'],
                ere_id_rp=row['ID сотрудника']
            )
            encas_error.save()
            
            if row['Установленные дни']:
                days = row['Установленные дни'].split(', ')
                day_instances = DayOfWeek.objects.filter(day__in=days)
                encas_error.ere_encas_days.set(day_instances)

    logger.info('INFO save_errors_to_model: Функция завершила работу успешно')
