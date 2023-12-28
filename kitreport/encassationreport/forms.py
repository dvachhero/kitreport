from django import forms

class UploadFileForm(forms.Form):
    file_z0660 = forms.FileField(label='Выберите Z0660.csv:')