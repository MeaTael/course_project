import json
from datetime import datetime, timedelta

from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect

from home.models import EngRusDict
from users.forms import LearningWords

from django.contrib import messages

from users.models import Profile


def home(request):
    return render(request, 'home/mainPage.html')


def learn(request):
    words = json.loads(request.user.profile.learned_words)
    word_to_check = EngRusDict.objects.exclude(eng__in=words.keys())[0]
    ru = word_to_check.rus
    eng = word_to_check.eng
    if request.method == 'POST':
        form = LearningWords(request.POST)
        if form.is_valid() and form.cleaned_data.get('word') == eng:
            messages.success(request, 'Отлично, теперь Вы знаете на 1 слово больше!')
            words[eng] = {"translate": ru, "forgeting_coef": 1.0, "last_repeating": datetime.now().strftime('%d.%m.%Y %H:%M'), "repeating": 1}
            request.user.profile.learned_words = json.dumps(words)
            request.user.profile.save()
            return redirect('learn')
        else:
            messages.error(request, 'Неверно, попробуйте еще раз!')
            return redirect('learn')
    else:
        form = LearningWords()
        form.set_word_to_check(word_to_check)
    return render(request, 'home/learnPage.html', {'ru': ru, 'eng': eng, 'form': form})


def repeat(request):
    words = json.loads(request.user.profile.learned_words)
    if len(words) == 0:
        return render(request, 'home/nothingToRepeatPage.html')
    word_to_check = sorted(words.keys(), key=lambda x: words[x]['forgeting_coef'])[0]
    message = words[word_to_check]["translate"]
    if request.method == 'POST':
        form = LearningWords(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('word') == word_to_check:
                request.user.profile.learning_level *= 0.9
                words[word_to_check]['repeating'] += 1
                messages.success(request, "Верный ответ!")
            else:
                request.user.profile.learning_level /= 0.9
                words[word_to_check]['repeating'] = 1
                messages.error(request, f'Вы ошиблись! Правильный ответ: {word_to_check}.')
            timepassed = datetime.now() - datetime.strptime(words[word_to_check]['last_repeating'], '%d.%m.%Y %H:%M')
            words[word_to_check]['forgeting_coef'] = (1 + 2 ** words[word_to_check]['repeating'] *
                                                      request.user.profile.learning_level * timepassed.total_seconds() /
                                                      timedelta(hours=1).total_seconds()) ** (-1 / (2 ** words[word_to_check]['repeating']))
            words[word_to_check]['last_repeating'] = datetime.now().strftime('%d.%m.%Y %H:%M')
            request.user.profile.learned_words = json.dumps(words)
            request.user.profile.save()
            return redirect('repeat')
    else:
        form = LearningWords()
        form.set_word_to_check(word_to_check)
    return render(request, 'home/repeatPage.html', {'message': message, 'form': form})


def compete(request):
    profiles = Profile.objects.all().order_by('-rating')[:10]
    messages_list = []
    i = 1
    for profile in profiles:
        messages_list.append({'username': profile.user.username, 'rating': profile.rating, 'i': i})
        i += 1
    return render(request, 'home/competePage.html', {'messages_list': messages_list})
