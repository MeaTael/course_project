from django.shortcuts import render


def home(request):
    return render(request, 'home/mainPage.html')


def learn(request):
    return render(request, 'home/learnPage.html')


def repeat(request):
    return render(request, 'home/repeatPage.html')


def compete(request):
    return render(request, 'home/competePage.html')


def login(request):
    return render(request, 'home/loginPage.html')


def signup(request):
    return render(request, 'home/signupPage.html')