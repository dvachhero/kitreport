import csv
from encassationreport.models import HandbookFBL3H

def import_FBL3H_handbook(csv_file_path):
    HandbookFBL3H.objects.all().delete()
    print("Таблица handbook_FBL3H очищена")
    count = 0
    with open(csv_file_path, mode='r', encoding='utf-16') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        print(reader.fieldnames)
        
        for row in reader:
            fb_fbl3h = row.get('fb_fbl3h').strip() if row.get('fb_fbl3h') else None
            fb_code_fn = row.get('fb_code_fn').strip() if row.get('fb_code_fn') else None
            fb_name_rp = row.get('fb_name_rp').strip() if row.get('fb_name_rp') else None
            fb_main_doc = row.get('fb_main_doc').strip() if row.get('fb_main_doc') else None

            if fb_fbl3h and fb_code_fn and fb_main_doc:
                HandbookFBL3H.objects.create(
                    fb_fbl3h=fb_fbl3h,
                    fb_code_fn=fb_code_fn,
                    fb_name_rp=fb_name_rp,
                    fb_main_doc=fb_main_doc,
                )
            
            count += 1
            print(f"{count} /// {fb_fbl3h} : {fb_code_fn} : {fb_name_rp} : {fb_main_doc}")

csv_file_path = 'C:/pyt/kitreport-for-tests/handbooks/FBL3H.csv'
import_FBL3H_handbook(csv_file_path)

