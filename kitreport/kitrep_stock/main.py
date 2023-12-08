import os
from datetime import datetime
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import mysql.connector
from mysql.connector import Error
from config import db_config

# Задан явный путь для папок procedure и procedure.old
current_dir = os.path.dirname(os.path.abspath(__file__))
procedure_dir = os.path.join(current_dir, 'procedure')
procedure_old_dir = os.path.join(current_dir, 'procedure.old')

# Функция для очистки CSV файла
def clean_dataframe(df):
    df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
    df.columns = df.iloc[0]
    df = df[1:]
    return df

# Запуск Tkinter и выбор файла
def select_file(title):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title=title)
    return file_path

# Функция для подключения к базе данных
def create_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            host=db_config['HOST'],
            port=db_config['PORT'],
            database=db_config['DATABASE']
        )
        print("///Database connection established.")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

# Функция для чтения данных из базы данных
def read_from_db(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

# Функция для записи данных в базу данных
def write_to_db(connection, query, data):
    cursor = connection.cursor()
    try:
        if isinstance(data, list):
            cursor.executemany(query, data)
        else:
            cursor.execute(query, data)
        connection.commit()
        print("///Query successful.")
    except Error as err:
        print(f"Error: '{err}'")

# Функция для проверки существующих записей в таблице ошибок
def check_existing_errors(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM inventoryreport_inventoryreporterrors")
    count = cursor.fetchone()[0]
    if count > 0:
        # Создание папки, если она не существует
        if not os.path.exists(procedure_old_dir):
            os.makedirs(procedure_old_dir)
        filename = "[" + datetime.now().strftime("%Y%m%d") + "]" + "[" + datetime.now().strftime("%H%M%S") + "]" + "inventoryreport.old.csv"
        filepath = os.path.join(procedure_old_dir, filename)
        # Выгрузка существующих записей в CSV файл
        cursor.execute("SELECT * FROM inventoryreport_inventoryreporterrors")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False, encoding='utf-16')
        print(f"///Existing error records were saved to {filepath}")
        cursor.execute("DELETE FROM inventoryreport_inventoryreporterrors")
    cursor.close()
    return count == 0

# Функция для записи данных в CSV
def save_errors_to_csv(df_errors):
    # Создание папки, если она не существует
    if not os.path.exists(procedure_dir):
        os.makedirs(procedure_dir)
    filename = "[" + datetime.now().strftime("%Y%m%d") + "]" + "[" + datetime.now().strftime("%H%M%S") + "]" + "inventoryreport.csv"
    filepath = os.path.join(procedure_dir, filename)
    df_errors.to_csv(filepath, index=False, encoding='utf-16')
    print(f"///Errors were saved to {filepath}")

# Функция для приведения к одному виду
def normalize_city_name(city):
    return city.strip().lower()

# Функция для проверки 500.csv
def compare_with_500_csv(connection, file_500_path):
    df_500 = pd.read_csv(file_500_path, encoding='utf-16')
    df_500_cleaned = clean_dataframe(df_500)
    df_500_cleaned.columns = df_500_cleaned.columns.where(df_500_cleaned.columns.notna(), '')
    df_500_cleaned['Основной с'] = df_500_cleaned['Основной с'].apply(normalize_city_name)
    
    # Получение данных из базы данных
    query = "SELECT main_city FROM inventoryreport_inventoryreporthandbook_complete WHERE main_doc = 500"
    cities_in_db = read_from_db(connection, query)
    cities_in_db_normalized = set(normalize_city_name(city[0]) for city in cities_in_db)

    # Сравнение городов из файла 500.csv с данными из таблицы
    cities_in_500_csv = set(df_500_cleaned['Основной с'])
    missing_cities_500 = cities_in_db_normalized - cities_in_500_csv

    return missing_cities_500

# Функция для проверки 555.csv
def compare_with_555_csv(connection, file_555_path):
    df_555 = pd.read_csv(file_555_path, encoding='utf-16')
    df_555_cleaned = clean_dataframe(df_555)
    df_555_cleaned.columns = df_555_cleaned.columns.where(df_555_cleaned.columns.notna(), '')
    df_555_cleaned['Основной с'] = df_555_cleaned['Основной с'].apply(normalize_city_name)
    
    # Получение данных из базы данных
    query = "SELECT main_city, main_acc FROM inventoryreport_inventoryreporthandbook_complete WHERE main_doc = 555"
    data_in_db = read_from_db(connection, query)
    cities_acc_in_db = {(normalize_city_name(row[0]), row[1]) for row in data_in_db}

    # Сравнение городов из файла 555.csv с данными из таблицы
    cities_in_555_csv = set(df_555_cleaned['Основной с'])
    missing_cities_acc_555 = {city_acc for city_acc in cities_acc_in_db if city_acc[0] not in cities_in_555_csv}

    return missing_cities_acc_555

# Фильтр 555.csv по z0660.csv
def filter_cities_with_z0660(missing_cities_acc_555, file_z0660_path):
    df_z0660 = pd.read_csv(file_z0660_path, encoding='utf-16', skiprows=12)
    df_z0660_cleaned = clean_dataframe(df_z0660)
    df_z0660_cleaned.columns = df_z0660_cleaned.columns.str.strip()
    df_z0660_cleaned = df_z0660_cleaned.dropna(how='all', axis=1).dropna(how='all', axis=0)
    df_z0660_cleaned.columns = df_z0660_cleaned.columns.where(df_z0660_cleaned.columns.notna(), '')
    
    df_z0660_cleaned['Основной счет'] = df_z0660_cleaned['Основной счет'].map(normalize_city_name)
    df_z0660_cleaned['Название основного счета'] = df_z0660_cleaned['Название основного счета'].map(normalize_city_name)
    df_z0660_cleaned['Кредит'] = df_z0660_cleaned['Кредит'].map(normalize_city_name)
    df_z0660_cleaned['Исход. сальдо'] = df_z0660_cleaned['Исход. сальдо'].map(normalize_city_name)
   
    # Оставляем только те записи из missing_cities_acc_555, для которых в z0660 суммы по кредиту и исходному сальдо не равны 0
    remaining_cities = set()
    for city, acc in missing_cities_acc_555:
        z0660_row = df_z0660_cleaned[(df_z0660_cleaned['Основной счет'] == acc) & (df_z0660_cleaned['Кредит'] == '0') & (df_z0660_cleaned['Исход. сальдо'] == '0')]
        if z0660_row.empty:
            remaining_cities.add(city)

    return remaining_cities

# Функция для проверки 555.csv по таблице for_report
def compare_with_for_report(connection, combined_missing_cities):
    query_for_report = "SELECT name_rp, fio_rp, id_rp FROM for_report"
    data_for_report = read_from_db(connection, query_for_report)

    for_report_set = {(normalize_city_name(row[0]), row[1], row[2]) for row in data_for_report}
    matching_records = []
    for city in combined_missing_cities:
        normalized_city = normalize_city_name(city)
        for name_rp, fio_rp, id_rp in for_report_set:
            if name_rp == normalized_city:
                matching_records.append((city, "Вы нарушили приказ о инвентаризации", fio_rp, id_rp))

    if matching_records:
        df_errors = pd.DataFrame(matching_records, columns=['name_rp', 'comment', 'fio_rp', 'id_rp'])
        if df_errors.isnull().values.any():
            print("///Empty values detected.")
            df_errors = df_errors.fillna({'fio_rp': 'N/A', 'id_rp': -1})
        return df_errors
    else:
        print("No matches.")
        return pd.DataFrame(columns=['name_rp', 'comment', 'fio_rp', 'id_rp'])

# Функция для выполнения основного процесса
def main_process(file_500_path, file_555_path, file_z0660_path, connection):
    missing_cities_500 = compare_with_500_csv(connection, file_500_path)
    missing_cities_acc_555 = compare_with_555_csv(connection, file_555_path)
    missing_cities_555 = filter_cities_with_z0660(missing_cities_acc_555, file_z0660_path)

    # Объединение множеств missing_cities_500 и missing_cities_555
    combined_missing_cities = missing_cities_500.union(missing_cities_555)

    df_errors = compare_with_for_report(connection, combined_missing_cities)
    
    if not df_errors.empty:
        # Запись в файл CSV
        save_errors_to_csv(df_errors)
        # Запись претендентов получить по жопе в базу данных
        insert_query = "INSERT INTO inventoryreport_inventoryreporterrors (name_rp, comment, fio_rp, id_rp) VALUES (%s, %s, %s, %s)"
        insert_data = [tuple(row) for row in df_errors.to_numpy()]
        
        write_to_db(connection, insert_query, insert_data)
        print(f"///Added {len(df_errors)} records to inventoryreport.csv file and database.")

file_500_path = select_file("Select 500.csv")

if file_500_path:
    file_555_path = select_file("Select 555.csv")
    
if file_500_path and file_555_path:
    file_z0660_path = select_file("Select Z0660.csv")

if file_500_path and file_555_path and file_z0660_path:
    try:
        with create_db_connection() as connection:
            check_existing_errors(connection)
            main_process(file_500_path, file_555_path, file_z0660_path, connection)

    except Exception as err:
        print(f"Connection error: {err}")
        
    finally:   
        try:
            if connection and connection.is_connected():
                connection.close()
            print("///Database connection closed.")
        except Exception as err:
            print(f"///Failed to close database connection: {err}")