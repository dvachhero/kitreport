from django import forms

class FileUploadForm(forms.Form):
    ekv_sap = forms.FileField(label='Отчет SAP:')
    ekv = forms.FileField(label='Отчет Экваринг:')
    ekv_krym = forms.FileField(label='Отчет Экваринг Крым:')