import pandas as pd
import os
import io

import logging
from django.contrib import messages
from django.conf import settings

logger = logging.getLogger('encassationreport')

def read_file(file_path):
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.xls':
        logger.info("INFO read_file: Формат файла .xls")
        with open(file_path, 'r', encoding='utf-16') as f:
            content = f.readlines()
        
        header_index = None
        for i, line in enumerate(content):
            if "основной счет" in line.lower():
                header_index = i
                break
        
        if header_index is None:
            messages.error("Ошибка обработки файла")
            logger.error("ERROR read_file: Формат файла не поддерживается")
        
        df = pd.read_csv(
            io.StringIO(''.join(content[header_index:])),
            delimiter='\t',
            header=0
        )
        
        if df.empty:
            messages.error("Файл пуст")
            logger.error("ERROR read_file: Файл пуст")
            return None
        
        df.dropna(how='all', axis=1, inplace=True)
        df.dropna(how='all', axis=0, inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        df.columns = df.columns.str.strip().str.lower()
            
    elif file_ext in ['.csv', '.xlsx']:
        
        if file_ext == '.csv':
            logger.info("INFO read_file: Формат файла .csv")
            df = pd.read_csv(file_path, encoding='utf-16', delimiter='\t')
        else:
            logger.info("INFO read_file: Формат файла .xlsx")
            df = pd.read_excel(file_path, engine='openpyxl')
            
        df = df[~df.apply(lambda x: x.astype(str).str.contains('\*')).any(axis=1)]
        main_account_index = df.apply(lambda x: x.astype(str).str.  wer().str.contains("основной счет")).any(axis=1)
        
        if df.empty:
            messages.error("Файл пуст")
            logger.error("ERROR read_file: Файл пуст")
            return None
        
        if not main_account_index.any():
            messages.error("Ошибка обработки файла")
            logger.error("INFO read_file: Фраза 'основной счет' не найдена в файле")

        row_index = main_account_index.idxmax()

        df_trimmed = df.iloc[row_index + 1:]
        df_trimmed.columns = df.iloc[row_index].str.strip().str.lower()
        df_trimmed = df_trimmed.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df_trimmed = df_trimmed.reset_index(drop=True)
        
        df = df_trimmed
        
    else:
        messages.error("Формат файла не поддерживается")
        logger.error("ERROR read_file: Формат файла не поддерживается")
        return None
    
    df.columns = df.columns.str.strip().str.lower()
    columns_to_lowercase = ['основной счет', 'название основного счета']
    
    for col in columns_to_lowercase:
        df[col] = df[col].astype(str).str.strip().str.lower()
    
    numeric_columns = ['вход. сальдо', 'дебет', 'кредит', 'исход. сальдо']
    for col in numeric_columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace(',', '.').str.replace(' ', '')
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].astype(float)
        elif df[col].dtype == 'int64':
            df[col] = df[col].astype(float)

    logger.info("INFO read_file: Функция завершила работу успешно")

    return df
