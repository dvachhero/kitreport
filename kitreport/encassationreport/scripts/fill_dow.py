from encassationreport.models import DayOfWeek

def run():
    days_to_create = [
        ('monday', 'пн'),
        ('tuesday', 'вт'),
        ('wednesday', 'ср'),
        ('thursday', 'чт'),
        ('friday', 'пт'),
        ('saturday', 'сб'),
        ('sunday', 'вс'),
        ('everyday', 'ежедневно'),
    ]

    for code, name in days_to_create:
        DayOfWeek.objects.update_or_create(day=code, defaults={'day': code})
