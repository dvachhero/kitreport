from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

@login_required(login_url='/login/')
def inventory_report_upload(request):
    # Ваша логика обработки запроса, если необходимо
    return render(request, 'inventoryreportupload.html')