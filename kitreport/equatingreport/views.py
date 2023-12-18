from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import FileUploadForm, CheckFnForm
from .models import EkviringData, PaymentData, sprforekv, EkviringData_enriched, sprforfn, PaymentData_enriched
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
                df_sap.columns = ['CODE_FN', 'DATE', 'SUM', 'CREATED_BY', 'DRIVER', 'PAYMENT_TYPE']
                # Преобразование формата даты
                df_sap['DATE'] = pd.to_datetime(df_sap['DATE'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')
                # Вставьте код преобразования формата суммы здесь
                df_sap['SUM'] = pd.to_numeric(df_sap['SUM'], errors='coerce').fillna(0).astype(int)
                # Фильтрация данных
                df_sap_filtered = df_sap[df_sap['PAYMENT_TYPE'].isin(['Плат. картой (пин-пад)', 'Плат. картой (терминал)'])]
                # Сохранение в базу данных
                for _, row in df_sap_filtered.iterrows():
                    PaymentData.objects.create(
                        code_fn=row['CODE_FN'],
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

                # Load data from EkviringData and sprforekv models
                ekviring_data = pd.DataFrame(list(EkviringData.objects.all().values()))
                sprforekv_data = pd.DataFrame(list(sprforekv.objects.all().values()))

                # Merge and enrich the data
                enriched_data = pd.merge(ekviring_data, sprforekv_data, left_on='terminal', right_on='TID')

                # Save enriched data to EkviringData_enriched model
                for _, row in enriched_data.iterrows():
                    EkviringData_enriched.objects.create(**row.to_dict())

                # Load data from PaymentData and sprforfn models
                payment_data = pd.DataFrame(list(PaymentData.objects.all().values()))
                sprforfn_data = pd.DataFrame(list(sprforfn.objects.all().values()))

                # Merge and enrich payment data
                enriched_payment_data = pd.merge(payment_data, sprforfn_data, on='code_fn')

                # Save enriched payment data to PaymentData_enriched model
                for _, row in enriched_payment_data.iterrows():
                    PaymentData_enriched.objects.create(**row.to_dict())

                # Load data from EkviringData_enriched and PaymentData_enriched models
                ekviring_enriched = pd.DataFrame(list(EkviringData_enriched.objects.all().values()))
                payment_enriched = pd.DataFrame(list(PaymentData_enriched.objects.all().values()))

                # Merge the enriched data
                merged_df = pd.merge(ekviring_enriched, payment_enriched,
                                     left_on=['date_operation', 'sum_operation', 'pfm'],
                                     right_on=['date', 'sum', 'pfm'],
                                     how='outer', indicator=True)

                # Select mismatches
                mismatches = merged_df[merged_df['_merge'] == 'right_only'].drop(columns=['_merge'])

                # Сохранение в Excel только выбранных столбцов
                mismatches_filtered = mismatches[
                    ["date", "sum", "created_by", "payment_type", "code_fn", "pfm", "name_rp_y","fio_rp","id_rp"]]
                mismatches_filtered.to_excel('mismatched_data.xlsx', index=False)


                return HttpResponse("Файлы были успешно обработаны и данные сохранены.")
            except Exception as e:
                return HttpResponse(f"Произошла ошибка: {e}")
    else:
        form = FileUploadForm()
        return render(request, 'equatingreportupload.html', {'form': form})

def read_excel_with_skip1(file, column_index, skip_value=None):
    print(f"Чтение файла Excel и пропуск строк до значения {skip_value}, индекс столбца: {column_index}")
    try:
        # Сначала прочитаем весь файл, чтобы найти строку, содержащую нужное значение, если skip_value задан
        if skip_value is not None:
            df_temp = pd.read_excel(file, header=None)
            start_row = df_temp.index[df_temp[column_index] == skip_value].tolist()
            skiprows = start_row[0] + 1 if start_row else 0
        else:
            skiprows = 0

        # Чтение файла с пропуском строк
        file.seek(0)  # Сбросить указатель файла
        return pd.read_excel(file, skiprows=skiprows, usecols=[column_index])

    except Exception as e:
        print(f"Ошибка при чтении Excel файла: {e}")
def check_fn(request):
    print("Функция check_fn вызвана")
    context = {'form': CheckFnForm()}  # Инициализация контекста здес
    if request.method == 'POST':
        print("Обработка POST запроса")
        form = CheckFnForm(request.POST, request.FILES)

        if form.is_valid():
            print("Форма валидна")
            ekv_file = request.FILES['ekv_file']
            ekv_krym_file = request.FILES['ekv_krym_file']
            fn_file = request.FILES['fn_file']

            try:
                df_ekv = read_excel_without_skip(ekv_file, [10])
                df_ekv_krym = read_excel_with_skip1(ekv_krym_file, 4, skip_value='5')
                df_fn = pd.read_csv(BytesIO(fn_file.read()), sep='\t', encoding='utf-16', skiprows=2)

                # Приводим типы данных к строкам для сравнения
                df_ekv[df_ekv.columns[0]] = df_ekv[df_ekv.columns[0]].astype(str)
                df_ekv_krym[df_ekv_krym.columns[0]] = df_ekv_krym[df_ekv_krym.columns[0]].astype(str)
                df_fn[df_fn.columns[1]] = df_fn[df_fn.columns[1]].astype(str)

                # Получаем данные из моделей, также приводим к строкам
                sprforekv_data = pd.DataFrame(list(sprforekv.objects.all().values('TID')))
                sprforekv_data['TID'] = sprforekv_data['TID'].astype(str)
                sprforfn_data = pd.DataFrame(list(sprforfn.objects.all().values('code_fn')))
                sprforfn_data['code_fn'] = sprforfn_data['code_fn'].astype(str)

                # Объединяем и находим несоответствия
                combined_ekv = pd.concat([df_ekv, df_ekv_krym], ignore_index=True)
                print(combined_ekv)
                combined_ekv.to_excel('combined_ekv.xlsx', index=False)

                # Объединяем столбцы из df_ekv и df_ekv_krym в один столбец
                combined_ekv_column = pd.concat([df_ekv[df_ekv.columns[0]], df_ekv_krym[df_ekv_krym.columns[0]]],ignore_index=True)

                # Создаем DataFrame с объединенным столбцом
                combined_ekv = pd.DataFrame(combined_ekv_column)
                combined_ekv.columns = ['Combined_EKV']  # Назначаем имя столбца
                print(combined_ekv)
                combined_ekv.to_excel('combined_ekv.xlsx', index=False)

                mismatches_ekv = pd.merge(combined_ekv, sprforekv_data, left_on='Combined_EKV', right_on='TID', how='left', indicator=True)
                mismatches_ekv = mismatches_ekv[mismatches_ekv['_merge'] == 'left_only']
                mismatches_fn = pd.merge(df_fn, sprforfn_data, left_on=df_fn.columns[1], right_on='code_fn', how='left', indicator=True)
                mismatches_fn = mismatches_fn[mismatches_fn['_merge'] == 'left_only']

                # Обновляем контекст, добавляя HTML таблиц
                context['mismatches_ekv'] = mismatches_ekv.to_html(classes='table table-striped', index=False)
                context['mismatches_fn'] = mismatches_fn.to_html(classes='table table-striped', index=False)

            except Exception as e:
                print(f"Ошибка при обработке файлов: {e}")
                context['error'] = str(e)

        else:
            print("Форма не валидна")
            context['error'] = form.errors.as_json()

    # Возвращаем ответ для всех запросов, включая GET
    return render(request, 'check_fn.html', context)

