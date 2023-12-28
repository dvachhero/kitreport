import csv
from handbooks.models import EncassationMainhandbook

def import_encassation_handbook(csv_file_path):
    EncassationMainhandbook.objects.all().delete()
    print("Таблица encassation_handbook очищена")
    count = 0
    with open(csv_file_path, mode='r', encoding='utf-16') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        print(reader.fieldnames)
        
        for row in reader:
            hb_main_acc = row.get('hb_main_acc').strip() if row.get('hb_main_acc') else None
            hb_fbl3h = row.get('hb_fbl3h').strip() if row.get('hb_fbl3h') else None
            hb_code_kk = row.get('hb_code_kk').strip() if row.get('hb_code_kk') else None
            hb_code_fn = row.get('hb_code_fn').strip() if row.get('hb_code_fn') else None
            hb_name_rp_0660 = row.get('hb_name_rp_0660').strip() if row.get('hb_name_rp_0660') else None
            hb_name_rp = row.get('hb_name_rp').strip() if row.get('hb_name_rp') else None
            hb_main_doc = row.get('hb_main_doc').strip() if row.get('hb_main_doc') else None

            if hb_main_acc and hb_code_fn:
                EncassationMainhandbook.objects.create(
                    hb_main_acc=hb_main_acc,
                    hb_fbl3h=hb_fbl3h,
                    hb_code_kk=hb_code_kk,
                    hb_code_fn=hb_code_fn,
                    hb_name_rp_0660=hb_name_rp_0660,
                    hb_name_rp=hb_name_rp,
                    hb_main_doc=hb_main_doc,
                )
            
            count += 1
            print(f"{count} /// {hb_main_acc} : {hb_fbl3h} : {hb_code_kk} : {hb_code_fn}: {hb_name_rp_0660} : {hb_name_rp} : {hb_main_doc}")

csv_file_path = 'C:/pyt/kitreport-for-tests/handbooks/MainHandbook.csv'
import_encassation_handbook(csv_file_path)

