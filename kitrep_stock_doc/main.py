import os
from datetime import datetime
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import mysql.connector
from mysql.connector import Error
from config import db_config

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
        print("MySQL Database connection successful")
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
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

# Функция для проверки существующих записей в таблице ошибок
def check_existing_errors(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM inventoryreport_inventoryreporterrors")
    count = cursor.fetchone()[0]
    if count > 0:
        # Создание папки, если она не существует
        if not os.path.exists('procedure.old'):
            os.makedirs('procedure.old')
        filename = "[" + datetime.now().strftime("%Y%m%d") + "]" + "[" + datetime.now().strftime("%H%M%S") + "]" + "inventoryreport.old.csv"
        filepath = os.path.join('procedure.old', filename)
        # Выгрузка существующих записей в CSV файл
        cursor.execute("SELECT * FROM inventoryreport_inventoryreporterrors")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False, encoding='utf-16')
        print(f"Existing error records were saved to {filepath}")
        cursor.execute("DELETE FROM inventoryreport_inventoryreporterrors")
    cursor.close()
    return count == 0

# Функция для записи данных в CSV
def save_errors_to_csv(df_errors):
    # Создание папки, если она не существует
    if not os.path.exists('procedure'):
        os.makedirs('procedure')
    filename = "[" + datetime.now().strftime("%Y%m%d") + "]" + "[" + datetime.now().strftime("%H%M%S") + "]" + "inventoryreport.csv"
    filepath = os.path.join('procedure', filename)
    df_errors.to_csv(filepath, index=False, encoding='utf-16')
    print(f"Errors were saved to {filepath}")

# Функция для приведения к одному виду
def normalize_city_name(city):
    return city.strip().lower()

# Функция для выполнения основного процесса
def main_process(file_500_path, file_555_path, connection):
    df_500 = pd.read_csv(file_500_path, encoding='utf-16')
    df_555 = pd.read_csv(file_555_path, encoding='utf-16')
    
    df_500_cleaned = clean_dataframe(df_500)
    df_555_cleaned = clean_dataframe(df_555)
    
    df_500_cleaned.loc[:, 'Основной с'] = df_500_cleaned['Основной с'].apply(normalize_city_name)
    df_555_cleaned.loc[:, 'Основной с'] = df_555_cleaned['Основной с'].apply(normalize_city_name)
    
    df_500_main = df_500_cleaned[['Основной с']] if 'Основной с' in df_500_cleaned.columns else pd.DataFrame()
    df_555_main = df_555_cleaned[['Основной с']] if 'Основной с' in df_555_cleaned.columns else pd.DataFrame()
    
    unique_cities = pd.concat([df_500_main, df_555_main]).drop_duplicates().reset_index(drop=True)
    # Получение уникальных городов из базы данных
    cursor = connection.cursor()
    cursor.execute("SELECT name_rp FROM inventoryreport_inventoryreporthandbook")
    handbook_cities = cursor.fetchall()
    
    handbook_cities_normalized = set(normalize_city_name(city[0]) for city in handbook_cities)
    unique_cities_normalized = set(unique_cities['Основной с'])

    missing_cities_set = handbook_cities_normalized - unique_cities_normalized
    # Получение данных об отсутствующих городах из справочника
    missing_cities_data = []
    for city in missing_cities_set:
        cursor.execute("SELECT * FROM inventoryreport_inventoryreporthandbook WHERE name_rp = %s", (city,))
        city_data = cursor.fetchone()
        if city_data:
            missing_cities_data.append(city_data)

    if missing_cities_data:
        df_errors = pd.DataFrame(missing_cities_data, columns=['id', 'name_rp', 'comment', 'fio_rp', 'id_rp'])  # Пример столбцов
        # Запись в файл CSV
        save_errors_to_csv(df_errors)

        insert_query = "INSERT INTO inventoryreport_inventoryreporterrors (id, name_rp, comment, fio_rp, id_rp) VALUES (%s, %s, %s, %s, %s)"
        insert_data = [tuple(row) for row in df_errors.to_numpy()]

        write_to_db(connection, insert_query, insert_data)
        print(f"Добавлено {len(missing_cities_data)} записей в файл errors.csv и базу данных.")

file_500_path = select_file("Выберите файл 500.csv")
file_555_path = select_file("Выберите файл 555.csv")

if file_500_path and file_555_path:
    with create_db_connection() as connection:
        check_existing_errors(connection)
        main_process(file_500_path, file_555_path, connection)
#конец