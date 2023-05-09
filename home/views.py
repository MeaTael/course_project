import json
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect

from home.models import EngRusDict
from users.forms import LearningWords

from django.contrib import messages


def home(request):
    return render(request, 'home/mainPage.html')


def learn(request):
    words = json.loads(request.user.profile.learned_words)
    word_to_check = EngRusDict.objects.exclude(eng__in=words.keys())[0]
    message = f'Текущее слово: {word_to_check.rus}, оно переводится как {word_to_check.eng}, введите это слово на английском в форме ниже'
    if request.method == 'POST':
        form = LearningWords(request.POST)
        if form.is_valid() and form.cleaned_data.get('word') == word_to_check.eng:
            messages.success(request, 'Отлично, все верно, теперь Вы знаете на 1 слово больше')
            words[word_to_check.eng] = {"forgeting_coef": 1.0, "last_repeating": datetime.now().strftime('%d.%m.%Y %H:%M'), 'repeating': 1}
            request.user.profile.learned_words = json.dumps(words)
            request.user.profile.save()
            response = HttpResponse(status=302)
            response['Location'] = '/learn'
            return response
        else:
            messages.success(request, 'Внимательно посмотрите, как именно пишется данное слово на английском')
            return redirect('learn')
    else:
        form = LearningWords()
        form.set_word_to_check(word_to_check)
    return render(request, 'home/learnPage.html', {'message': message, 'form': form})


def repeat(request):
    return render(request, 'home/repeatPage.html')


def compete(request):
    return render(request, 'home/competePage.html')
