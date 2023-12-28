import csv
from encassationreport.models import EncassationControl, DayOfWeek

days_mapping = {
    'пн': 'monday',
    'вт': 'tuesday',
    'ср': 'wednesday',
    'чт': 'thursday',
    'пт': 'friday',
    'пт*': 'friday',
    'пт**': 'friday',
    'сб': 'saturday',
    'вс': 'sunday',
    'ежедневно': 'everyday',
    'ежедневно*': 'everyday',
    'ежедневно**': 'everyday',
}

def import_encassation_control(csv_file_path):
    EncassationControl.objects.all().delete()
    print("Таблица encassation_control очищена")
    count = 0
    with open(csv_file_path, mode='r', encoding='utf-16') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            row = {key.strip().lower(): value.strip() for key, value in row.items()}
            ec_city_name = row.get('филиал')
            encas_days = row.get('установленные дни')
            ec_encas_type = row.get('способ инкассации')
            ec_code_fn = row.get('код завода')

            if ec_city_name and encas_days and ec_encas_type and ec_code_fn:
                encas_control = EncassationControl.objects.create(
                    ec_main_city=ec_city_name,
                    ec_encas_type=ec_encas_type,
                    ec_code_fn=ec_code_fn
                )

                # Обработка дней инкассации
                days = encas_days.split(',')
                for day_abbr in days:
                    day_abbr = day_abbr.lower().strip()
                    if day_abbr in days_mapping:
                        day_instance, created = DayOfWeek.objects.get_or_create(day=days_mapping[day_abbr])
                        encas_control.encas_days.add(day_instance)
            
            count += 1
            print(f"{count} /// {ec_city_name} : {encas_days} : {ec_encas_type} : {ec_code_fn}")

csv_file_path = 'c:/pyt/kitreport-for-tests/encassation/HB_graph.csv'
import_encassation_control(csv_file_path)
