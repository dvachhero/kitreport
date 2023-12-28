from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

import logging
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

from .scripts.read_file import read_file
from .scripts.write_table import write_table
from handbooks.models import HandbooksOsnspr, EncassationMainhandbook

from .models import EncassationReportError, EncassationControl
from .forms import UploadFileForm

import pandas as pd
from datetime import datetime, date
import os

MAPPING = { 
    'mon': 'пн', 'monday': 'пн',  
    'tue': 'вт', 'tuesday': 'вт', 
    'wed': 'ср', 'wednesday': 'ср', 
    'thu': 'чт', 'thursday': 'чт',
    'fri': 'пт', 'friday': 'пт',
    'sat': 'сб', 'saturday': 'сб',
    'sun': 'вс', 'sunday': 'вс',
    'everyday': 'ежедневно',
}

COLUMN_TITLES = {
    'день недели': 'Дата инкассации',
    'код завода': 'Код завода',
    'название основного счета': 'Филиал',
    'ответственное лицо': 'Ответственное лицо',
    'ID сотрудника': 'ID сотрудника',
    'способ инкассации': 'Способ инкассации',
    'основной счет': 'Основной счет',
    'партнерство': 'Партнерство',
    'вход. сальдо': 'Вход. сальдо',
    'исход. сальдо': 'Исход. сальдо',
    'кредит': 'Кредит',
    'дебет': 'Дебет',
    'установленные дни': 'Установленные дни',
}

COLUMN_TITLES_TAB = {    
    'id': 'id',
    'ere_date': 'Дата инкассации',
    'ere_comment': 'comment',
    'ere_main_acc': 'Основной счет',
    'ere_code_fn': 'Код завода',
    'ere_name_rp': 'Филиал',
    'ere_affiliation': 'Партнерство',
    'ere_saldo_in': 'Вход. сальдо',
    'ere_debet': 'Дебет',
    'ere_credit': 'Кредит',
    'ere_saldo_out': 'Исход. сальдо',
    'ere_encas_type': 'Способ инкассации',
    'ere_fio_rp': 'Ответственное лицо',
    'ere_id_rp': 'ID сотрудника',
}

COLUMNS_ORDER = [
    'Дата инкассации', 'Основной счет', 'Код завода', 
    'Филиал', 'Партнерство', 'Вход. сальдо',
    'Дебет', 'Кредит', 'Исход. сальдо', 
    'Установленные дни', 'Способ инкассации',
    'Ответственное лицо', 'ID сотрудника'
]

logger = logging.getLogger('encassationreport')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/homefd')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('/login/')

@login_required(login_url='/login/')
def homefd(request):
    return render(request, 'homefd.html')

# Функция для очистки папки media
def clear_media_folder():
    media_root = settings.MEDIA_ROOT_ISR
    if not os.path.exists(media_root):
        os.makedirs(media_root)
    else:
        for file_name in os.listdir(media_root):
            file_path = os.path.join(media_root, file_name)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info("INFO clear_media_folder: Функция завершила работу успешно")
            except Exception as err:
                logger.error(f'ERROR clear_media_folder: Не удалось удалить файл: {err}')

# Функция для записи ошибок в csv
def save_errors_to_csv(df_errors):
    procedure_dir = os.path.join(settings.MEDIA_ROOT_ISR, 'procedure')
    if not os.path.exists(procedure_dir):
        os.makedirs(procedure_dir)
    filename = "[{}][{}]_encassationreport.csv".format(
        datetime.now().strftime("%Y%m%d"),
        datetime.now().strftime("%H%M%S")
    )
    filepath = os.path.join(procedure_dir, filename)
    try:
        df_errors.to_csv(filepath, sep=',', index=False, encoding='utf-16')
        logger.info(f"INFO save_errors_to_csv: Новые ошибки сохранены, путь:\n{filepath}")
    except Exception as err:
        logger.error(f"ERROR save_errors_to_csv: Ошибка сохранения: {err}")
    return filepath

# Функция для загрузки файлов на сервер
def handle_uploaded_file(f, file_name, clear_folder=False):
    media_root = settings.MEDIA_ROOT_ISR
    if not os.path.exists(media_root):
        os.makedirs(media_root)

    if clear_folder:
        clear_media_folder()

    file_path = os.path.join(media_root, file_name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path

# Функция для архивации уже существующих ошибок
def archive():
    existing_errors = EncassationReportError.objects.prefetch_related('ere_encas_days').all()
    
    if existing_errors.exists():
        column_names = COLUMN_TITLES_TAB.keys()
        df_existing_errors = pd.DataFrame.from_records(
            existing_errors.values_list(*column_names), columns=COLUMN_TITLES_TAB.values()
        )
        
        if 'id' in df_existing_errors.columns:
            df_existing_errors.drop('id', axis=1)
        
        if 'comment' in df_existing_errors.columns:
            df_existing_errors.drop('comment', axis=1)
        
        df_existing_errors['Установленные дни'] = [
            ', '.join(day.get_day_display() for day in error.ere_encas_days.all())
            for error in existing_errors
        ]
        
        df_existing_errors = df_existing_errors[COLUMNS_ORDER]
            
        old_procedure_dir = os.path.join(settings.MEDIA_ROOT_ISR, 'procedure.old')
        if not os.path.exists(old_procedure_dir):
            os.makedirs(old_procedure_dir)

        old_filename = f"[{datetime.now().strftime('%Y%m%d')}][{datetime.now().strftime('%H%M%S')}]_encassationreport.old.csv"
        old_filepath = os.path.join(old_procedure_dir, old_filename)
        df_existing_errors.to_csv(old_filepath, sep=',', index=False, encoding='utf-16')

        existing_errors.delete()
        logger.info(f"INFO archive: Старые ошибки сохранены, путь:\n{old_filepath}")
        logger.info('INFO archive: Ошибки сохранены и очищены из таблицы')

# Функция для конвертации дней недели с eng на rus
def convert_weekday(weekday_eng):
    mapping = MAPPING
    return mapping.get(weekday_eng, '')

# Функция для обработки файла z0660
def filter_z0660(file_z0660_path):
    try:
        df_error_acc = read_file(file_z0660_path)
        logger.info('INFO filter_z0660: Функция завершила работу успешно')
        return df_error_acc
    except Exception as err:
        logger.error(f"ERROR filter_z0660: Ошибка обработки: {err}")
        return pd.DataFrame()

# Функция для добавления кода завода в z0660
def filter_code_fn(df_error_fn):
    df_error_fn['код завода'] = pd.Series(dtype=str)

    for index, row in df_error_fn.iterrows():
        hb_main_acc = row['основной счет']

        try:
            handbook_entries = EncassationMainhandbook.objects.filter(hb_main_acc=hb_main_acc)
            if handbook_entries:
                df_error_fn.at[index, 'код завода'] = handbook_entries.first().hb_code_fn
            else:
                df_error_fn.at[index, 'код завода'] = None
        except Exception as err:
            df_error_fn.at[index, 'код завода'] = None
            logger.error(f'ERROR filter_code_fn: Ошибка обработки: {err}')

    logger.info('INFO filter_code_fn: Функция завершила работу успешно')
    
    return df_error_fn

# Функция для добавления графика и способа инкассации в z0660
def filter_encas_days(df_encas_days):
    # Извлечение данных с учетом ManyToManyField
    controls = EncassationControl.objects.prefetch_related('encas_days').all()
    controls_dict = {}
    for control in controls:
        days = control.encas_days.all().values_list('day', flat=True)
        controls_dict[control.ec_code_fn] = {
            'encas_days': days,
            'ec_encas_type': control.ec_encas_type
        }

    for index, row in df_encas_days.iterrows():
        control_entry = controls_dict.get(row['код завода'])
        try:
            if control_entry:
                encas_days_rus = [convert_weekday(day) for day in control_entry['encas_days']]
                df_encas_days.at[index, 'установленные дни'] = ', '.join(encas_days_rus)
                df_encas_days.at[index, 'способ инкассации'] = control_entry['ec_encas_type']
            else:
                df_encas_days.at[index, 'установленные дни'] = None
                df_encas_days.at[index, 'способ инкассации'] = None
        except Exception as err:
            df_encas_days.at[index, 'установленные дни'] = None
            df_encas_days.at[index, 'способ инкассации'] = None
            logger.error(f'ERROR filter_encas_days: Ошибка обработки для кода завода {row["код завода"]}: {err}')
        
    logger.info('INFO filter_encas_days: Функция завершила работу успешно')
    return df_encas_days


def filter_errors(df_encas_days, selected_date):
    errors_list = []
    weekday_eng = selected_date.strftime('%a').lower()
    weekday = convert_weekday(weekday_eng)

    try:
        for index, row in df_encas_days.iterrows():
            error = False
            established_days = row['установленные дни']

            if established_days is None:
                error = True
            else:
                # Проверка 1
                if row['исход. сальдо'] > 100000:
                    error = True

                # Проверка 2
                elif (weekday in row['установленные дни'] or 'ежедневно' in row['установленные дни']) and row['кредит'] == 0:
                    if row['способ инкассации'] == 'инкассаторы' and row['вход. сальдо'] < 25000:
                        error = False
                    elif row['исход. сальдо'] < 10000:
                        error = False
                    else:
                        error = True

                if error:
                    errors_list.append(row.to_dict())
        
        logger.info('INFO filter_errors: Функция завершила работу успешно')
        df_errors = pd.DataFrame(errors_list)
        
    except Exception as err:
        logger.error(f'ERROR filter_errors: ошибка обработки: {err}')
        
    return df_errors

# Функция для доавления записей в финальный отчет
def filter_forreport(df_forreport):
    df_forreport['ответственное лицо'] = pd.Series(dtype=str)
    df_forreport['ID сотрудника'] = pd.Series(dtype=str)
    df_forreport['партнерство'] = pd.Series(dtype=str)
    
    all_entries = HandbooksOsnspr.objects.all().values('pfm', 'fio_rp', 'id_rp', 'affiliation')
    entries_dict = {entry['pfm']: entry for entry in all_entries}
    
    for index, row in df_forreport.iterrows():
        pfm = row['код завода']
        entry = entries_dict.get(pfm)
        
        try:
            if entry:
                df_forreport.at[index, 'ответственное лицо'] = entry['fio_rp']
                df_forreport.at[index, 'ID сотрудника'] = entry['id_rp']
                df_forreport.at[index, 'партнерство'] = entry['affiliation']
            else:
                df_forreport.at[index, 'ответственное лицо'] = None
                df_forreport.at[index, 'ID сотрудника'] = None
                df_forreport.at[index, 'партнерство'] = None
    
        except Exception as err:
            df_forreport.at[index, 'ответственное лицо'] = None
            df_forreport.at[index, 'ID сотрудника'] = None
            df_forreport.at[index, 'партнерство'] = None
            logger.error(f'ERROR filter_forreport: Ошибка обработки: {err}')
    
    logger.info('INFO filter_forreport: Функция завершила работу успешно')
    
    return df_forreport


# Функция для перенаправления на страницу загрузки
@login_required(login_url='/login/')
def encassation_upload_success(request):
    download_path_exists = 'download_path' in request.session and request.session['download_path']
    return render(request, 'encassation_upload_success.html', {'download_url': download_path_exists})

# Функция для загрузки файлов
@login_required(login_url='/login/')
def encassation_report_upload(request):
    
    logger.info("==========================================================================================")
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            clear_media_folder()
            file_z0660 = request.FILES.get('file_z0660')
            file_z0660_path = handle_uploaded_file(file_z0660, file_z0660.name)
            selected_date = request.POST.get('date_input')
            if selected_date:
                try:
                    selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
                    success = main_process(file_z0660_path, selected_date, request)
                    
                    if success:
                        logger.info('INFO encassation_report_upload: Перенаправление на окно загрузки')
                        return redirect('encassation_upload_success')
                    else:
                        logger.info('INFO encassation_report_upload: Не удалось перенаправить на окно загрузки')
                        messages.error(request, 'Не удалось перенаправить на upload_success.html')
                except ValueError:
                    logger.error(f'ERROR encassation_report_upload: Неверный формат даты')
                    messages.error(request, 'Неверный формат даты.')
            else:
                logger.error(f'ERROR encassation_report_upload: Дата не выбрана')
                messages.error(request, 'Дата не выбрана.')
        else:
            logger.error(f'ERROR encassation_report_upload: Ошибка в форме загрузки')
            messages.error(request, 'Ошибка в форме загрузки.')

    else:
        form = UploadFileForm()
    
    return render(request, 'encassationreportupload.html', {'form': form})

# Функция для загрузки отчета на пк
@login_required(login_url='/login/')
def encassation_download_file(request):
    file_path = request.session.get('download_path')
    if file_path and os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

# Главная функция (логика обработки)
def main_process(file_z0660_path, selected_date, request):
    try:
        df_error_acc = filter_z0660(file_z0660_path)
        df_error_fn = filter_code_fn(df_error_acc)
        df_encas_days = filter_encas_days(df_error_fn)
        df_errors = filter_errors(df_encas_days, selected_date)
        df_forreport = filter_forreport(df_errors)
        df_forreport.insert(0, 'день недели', selected_date)
                
        if not df_forreport.empty:
            df_forreport = df_forreport.rename(columns=COLUMN_TITLES)
            df_forreport = df_forreport[COLUMNS_ORDER]
            
            archive()
            write_table(df_forreport)
            
            csv_filepath = save_errors_to_csv(df_forreport)
            request.session['download_path'] = csv_filepath
            return True
        return False
    
    except Exception as err:
        logger.error(f'ERROR main_process: Ошибка обработки: {err}')
        return False
