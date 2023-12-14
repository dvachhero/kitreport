from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

import logging
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import InventoryReportHandbook, InventoryReportError, ForReport
from .forms import UploadFileForm
import pandas as pd
from datetime import datetime
import os

logger = logging.getLogger(__name__)

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
def inventory_report_upload(request):
    # Ваша логика обработки запроса, если необходимо
    return render(request, 'inventoryreportupload.html')

@login_required(login_url='/login/')
def homefd(request):
    # Логика для страницы home
    return render(request, 'homefd.html')

# Функция для очистки CSV файла
def clean_dataframe(df):
    df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
    df.columns = df.iloc[0]
    df = df[1:]
    return df

# Функция для приведения к одному виду
def normalize_city_name(city):
    return city.strip().lower()

# Функция для записи ошибок в csv
def save_errors_to_csv(df_errors):
    procedure_dir = os.path.join(settings.MEDIA_ROOT, 'procedure')
    if not os.path.exists(procedure_dir):
        os.makedirs(procedure_dir)
    filename = "[{}][{}]_inventoryreport.csv".format(
        datetime.now().strftime("%Y%m%d"),
        datetime.now().strftime("%H%M%S")
    )
    filepath = os.path.join(procedure_dir, filename)
    try:
        df_errors.to_csv(filepath, index=False, encoding='utf-16')
        logger.info(f"Ошибки были сохранены по пути: {filepath}")
    except Exception as err:
        logger.error(f"Ошибка при сохранении файла: {err}")
    return filepath

# Функция для проверки 500.csv
def compare_with_500_csv(file_500_path):
    df_500 = pd.read_csv(file_500_path, encoding='utf-16')
    df_500_cleaned = clean_dataframe(df_500)
    df_500_cleaned.columns = df_500_cleaned.columns.where(df_500_cleaned.columns.notna(), '')
    df_500_cleaned['Основной с'] = df_500_cleaned['Основной с'].apply(normalize_city_name)
    
    cities_in_db = InventoryReportHandbook.objects.filter(main_doc='500').values_list('main_city', flat=True)
    cities_in_db_normalized = set(normalize_city_name(city) for city in cities_in_db)

    cities_in_500_csv = set(df_500_cleaned['Основной с'])
    missing_cities_500 = cities_in_db_normalized - cities_in_500_csv

    return missing_cities_500

# Функция для проверки 555.csv
def compare_with_555_csv(file_555_path):
    df_555 = pd.read_csv(file_555_path, encoding='utf-16')
    df_555_cleaned = clean_dataframe(df_555)
    df_555_cleaned.columns = df_555_cleaned.columns.where(df_555_cleaned.columns.notna(), '')
    df_555_cleaned['Основной с'] = df_555_cleaned['Основной с'].apply(normalize_city_name)
    
    cities_acc_in_db = InventoryReportHandbook.objects.filter(main_doc='555').values_list('main_city', 'main_acc')
    cities_acc_in_db_normalized = {(normalize_city_name(row[0]), row[1]) for row in cities_acc_in_db}
    
    cities_in_555_csv = set(df_555_cleaned['Основной с'])
    missing_cities_acc_555 = {city_acc for city_acc in cities_acc_in_db_normalized if city_acc[0] not in cities_in_555_csv}

    return missing_cities_acc_555

# Фильтр 555.csv по z0660.csv
def filter_cities_with_z0660(missing_cities_acc_555, file_z0660_path):
    df_z0660 = pd.read_csv(file_z0660_path, encoding='utf-16', skiprows=12)
    df_z0660_cleaned = clean_dataframe(df_z0660)
    df_z0660_cleaned.columns = df_z0660_cleaned.columns.str.strip()
    df_z0660_cleaned = df_z0660_cleaned.dropna(how='all', axis=1).dropna(how='all', axis=0)
    df_z0660_cleaned.columns = df_z0660_cleaned.columns.where(df_z0660_cleaned.columns.notna(), '')

    df_z0660_cleaned['Основной счет'] = df_z0660_cleaned['Основной счет'].astype(str).map(normalize_city_name)
    df_z0660_cleaned['Название основного счета'] = df_z0660_cleaned['Название основного счета'].map(normalize_city_name)
    df_z0660_cleaned['Кредит'] = df_z0660_cleaned['Кредит'].map(normalize_city_name)
    df_z0660_cleaned['Исход. сальдо'] = df_z0660_cleaned['Исход. сальдо'].map(normalize_city_name)

    remaining_cities = set()
    for city, acc in missing_cities_acc_555:
        filtered_df = df_z0660_cleaned[
            (df_z0660_cleaned['Основной счет'] == acc) & 
            ((df_z0660_cleaned['Кредит'].astype(float) != 0) | 
             (df_z0660_cleaned['Исход. сальдо'].astype(float) != 0))
        ]
        if not filtered_df.empty:
            remaining_cities.add(city)
    
    return remaining_cities

# Функция для проверки 555.csv по таблице for_report
def compare_with_for_report(combined_missing_cities):
    for_report_records = ForReport.objects.values_list('name_rp', 'fio_rp', 'id_rp')
    for_report_set = {(normalize_city_name(row[0]), row[1], row[2]) for row in for_report_records}
    
    matching_records = [
        (city, "Вы нарушили приказ о инвентаризации", fio_rp, id_rp)
        for city in combined_missing_cities
        for name_rp, fio_rp, id_rp in for_report_set
        if name_rp == normalize_city_name(city)
    ]

    return pd.DataFrame(matching_records, columns=['name_rp', 'comment', 'fio_rp', 'id_rp']) if matching_records else pd.DataFrame()

# Функция для сохранения и очистки существующих ошибок из модели
def archive_and_clear_existing_errors():
    existing_errors = InventoryReportError.objects.all()
    if existing_errors.exists():
        # Преобразование QuerySet в DataFrame
        df_existing_errors = pd.DataFrame.from_records(existing_errors.values())

        # Проверка и создание папки, если не существует
        old_procedure_dir = os.path.join(settings.MEDIA_ROOT, 'procedure.old')
        if not os.path.exists(old_procedure_dir):
            os.makedirs(old_procedure_dir)

        # Формирование пути к файлу и сохранение ошибок
        old_filename = "[{}][{}]_inventoryreport.old.csv".format(
            datetime.now().strftime("%Y%m%d"),
            datetime.now().strftime("%H%M%S")
        )
        old_filepath = os.path.join(old_procedure_dir, old_filename)
        df_existing_errors.to_csv(old_filepath, index=False, encoding='utf-16')

        # Очистка существующих записей в модели
        existing_errors.delete()
        logger.info(f"Существующие ошибки сохранены в {old_filepath} и очищены из базы данных.")

# Функция для записи ошибок в таблицу
def save_errors_to_db(errors):
    for error in errors:
        try:
            new_error = InventoryReportError.objects.create(**error)
            logger.info(f"Добавлена ошибка: {new_error}")
        except Exception as e:
            logger.error(f"Ошибка при добавлении записи в базу данных: {e}")

# Функция для выполнения основного процесса
def main_process(file_500_path, file_555_path, file_z0660_path):
    try:
        archive_and_clear_existing_errors()
        
        missing_cities_500 = compare_with_500_csv(file_500_path)
        missing_cities_acc_555 = compare_with_555_csv(file_555_path)
        missing_cities_555 = filter_cities_with_z0660(missing_cities_acc_555, file_z0660_path)

        combined_missing_cities = missing_cities_500.union(missing_cities_555)
        df_errors = compare_with_for_report(combined_missing_cities)
        
        if not df_errors.empty:
            csv_filepath = save_errors_to_csv(df_errors)
            save_errors_to_db(df_errors.to_dict('records'))
            logger.info(f"Добавлено {len(df_errors)} новых ошибок в базу данных и сохранено в {csv_filepath}.")
            
    except Exception as err:
        logger.error(f'Ошибка при обработке файлов: {err}')
        raise

# Функция для очистки папки media
def clear_media_folder():
    media_root = settings.MEDIA_ROOT
    if not os.path.exists(media_root):
        os.makedirs(media_root)
    else:
        for file_name in os.listdir(media_root):
            file_path = os.path.join(media_root, file_name)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f'Не удалось удалить {file_path}. Причина: {e}')

# Функция для загрузки файлов на сервер
def handle_uploaded_file(f, file_name, clear_folder=False):
    media_root = settings.MEDIA_ROOT
    if not os.path.exists(media_root):
        os.makedirs(media_root)

    if clear_folder:
        clear_media_folder()

    file_path = os.path.join(media_root, file_name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path
    
# Функция для загрузки файлов
@login_required(login_url='/login/')
def inventory_report_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            clear_media_folder()  # Очистка перед загрузкой новых файлов
            file_500 = request.FILES.get('file_500')
            file_555 = request.FILES.get('file_555')
            file_z0660 = request.FILES.get('file_z0660')
            
            file_500_path = handle_uploaded_file(file_500, file_500.name)
            file_555_path = handle_uploaded_file(file_555, file_555.name)
            file_z0660_path = handle_uploaded_file(file_z0660, file_z0660.name)

            try:
                main_process(file_500_path, file_555_path, file_z0660_path)
                messages.success(request, 'Файлы успешно обработаны.')
            except Exception as e:
                messages.error(request, f'Ошибка при обработке файлов: {e}')
        else:
            messages.error(request, 'Ошибка в форме загрузки.')

    else:
        form = UploadFileForm()

    return render(request, 'inventoryreportupload.html', {'form': form})