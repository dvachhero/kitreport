from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import EkviringData, PaymentData
from io import BytesIO
import pandas as pd




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
def equating_report_upload(request):
    # Ваша логика обработки запроса, если необходимо
    return render(request, 'equatingreportupload.html')

@login_required(login_url='/login/')
def homefd(request):
    # Логика для страницы home
    return render(request, 'homefd.html')


# Не забудьте определить индексы столбцов:
indices_eqvar = [10, 11, 13]  # Индексы для "Экваринг"
indices_eqvarkrym = [3, 4, 7]  # Индексы для "Экваринг Крым"
indices_sap = [1, 2, 8, 11, 12, 5]  # Индексы для "Отчет SAP"
# Функция для чтения Excel файла с пропуском начальных строк для "Экваринг Крым"


# views.py

from django.shortcuts import render
from django.http import HttpResponse
from .forms import FileUploadForm
from .models import EkviringData, PaymentData
import pandas as pd
from io import BytesIO

# Предположим, что у вас есть следующие функции, которые вы предоставили для чтения Excel файлов.
# Они используются для обработки загруженных файлов перед сохранением в базу данных.

def read_excel_with_skip(file, columns_indices):
    for skiprows in range(1, 10):
        df = pd.read_excel(file, skiprows=skiprows, nrows=0)
        if all(idx < len(df.columns) for idx in columns_indices):
            file.seek(0)  # Сбросить указатель файла
            return pd.read_excel(file, skiprows=skiprows, usecols=columns_indices)
    raise ValueError("Не удалось найти нужные столбцы в файле")

def read_excel_without_skip(file, columns_indices):
    try:
        return pd.read_excel(file, usecols=columns_indices)
    except Exception as e:
        raise ValueError(f"Ошибка при чтении файла: {e}")

def read_sap_file(file, column_indices):
    try:
        file.seek(0)  # Сбросить указатель файла
        df = pd.read_csv(file, sep='\t', encoding='utf-16', skiprows=2)
        df = df.iloc[:, column_indices]
        df.columns = [col.upper().replace(' ', '') for col in df.columns]
        df.iloc[:, 2] = df.iloc[:, 2].astype(str).str.replace(' ', '').str.replace(',', '.')
        df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2], errors='coerce').fillna(0).round().astype(int)
        return df
    except Exception as e:
        raise ValueError(f"Ошибка при чтении файла: {e}")

def upload_files(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                ekv_sap_file = request.FILES['ekv_sap']
                ekv_file = request.FILES['ekv']
                ekv_krym_file = request.FILES['ekv_krym']

                # Индексы столбцов для каждого типа файла
                indices_eqvar = [10, 11, 13]  # Индексы для "Экваринг"
                indices_eqvarkrym = [3, 4, 7]  # Индексы для "Экваринг Крым"
                indices_sap = [1, 2, 8, 11, 12, 5]  # Индексы для "Отчет SAP"

                # Обработка файла 'Отчет SAP'
                df_sap = read_sap_file(BytesIO(ekv_sap_file.read()), indices_sap)
                # Переименование столбцов для соответствия модели
                df_sap.columns = ['SERIAL_NUMBER', 'DATE', 'SUM', 'CREATED_BY', 'DRIVER', 'PAYMENT_TYPE']
                # Преобразование формата даты
                df_sap['DATE'] = pd.to_datetime(df_sap['DATE'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')
                # Вставьте код преобразования формата суммы здесь
                df_sap['SUM'] = pd.to_numeric(df_sap['SUM'], errors='coerce').fillna(0).astype(int)
                # Фильтрация данных
                df_sap_filtered = df_sap[df_sap['PAYMENT_TYPE'].isin(['Плат. картой (пин-пад)', 'Плат. картой (терминал)'])]
                # Сохранение в базу данных
                for _, row in df_sap_filtered.iterrows():
                    PaymentData.objects.create(
                        serial_number=row['SERIAL_NUMBER'],
                        date=row['DATE'],
                        sum=row['SUM'],
                        created_by=row['CREATED_BY'],
                        driver=row['DRIVER'],
                        payment_type=row['PAYMENT_TYPE']
                    )

                # Обработка файла 'Экваринг'
                df_ekv = read_excel_without_skip(BytesIO(ekv_file.read()), indices_eqvar)
                # Переименование столбцов для соответствия модели
                df_ekv.columns = ['TERMINAL', 'DATE_OPERATION', 'SUM_OPERATION']
                # Вставьте код преобразования формата даты здесь
                df_ekv['DATE_OPERATION'] = pd.to_datetime(df_ekv['DATE_OPERATION'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')
                # Сохранение в базу данных
                for _, row in df_ekv.iterrows():
                    EkviringData.objects.create(
                        date_operation=row['DATE_OPERATION'],
                        terminal=row['TERMINAL'],
                        sum_operation=row['SUM_OPERATION']
                    )

                # Обработка файла 'Экваринг Крым'
                df_ekv_krym = read_excel_with_skip(BytesIO(ekv_krym_file.read()), indices_eqvarkrym)
                # Переименование столбцов для соответствия модели
                df_ekv_krym.columns = ['DATE_OPERATION', 'TERMINAL', 'SUM_OPERATION']
                # Сохранение в базу данных
                for _, row in df_ekv_krym.iterrows():
                    try:
                        EkviringData.objects.create(
                            date_operation=row['DATE_OPERATION'],
                            terminal=row['TERMINAL'],
                            sum_operation=row['SUM_OPERATION']
                        )
                    except Exception as e:
                        print(f"Ошибка при сохранении записи: {e}")
                        # Здесь вы можете добавить дополнительную логику для обработки ошибки, если нужно
                        continue  # Продолжить обработку следующей записи

                return HttpResponse("Файлы были успешно обработаны и данные сохранены.")
            except Exception as e:
                return HttpResponse(f"Произошла ошибка: {e}")
    else:
        form = FileUploadForm()
    return render(request, 'upload.html', {'form': form})

