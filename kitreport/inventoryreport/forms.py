from django import forms

class UploadFileForm(forms.Form):
    file_500 = forms.FileField(label='Выберите 500.csv:')
    file_555 = forms.FileField(label='Выберите 555.csv:')
    file_z0660 = forms.FileField(label='Выберите Z0660.csv:')