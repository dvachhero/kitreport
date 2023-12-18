from django import forms

class FileUploadForm(forms.Form):
    ekv_sap = forms.FileField(label='Отчет SAP:')
    ekv = forms.FileField(label='Отчет Экваринг:')
    ekv_krym = forms.FileField(label='Отчет Экваринг Крым:')

class CheckFnForm(forms.Form):
    fn_file = forms.FileField(label='Загрузите Отчет SAP для проверки ФН:')
    ekv_file = forms.FileField(label='Загрузите файл Эквайринг для проверки:')
    ekv_krym_file = forms.FileField(label='Загрузите файл Эквайринг Крым для проверки:')