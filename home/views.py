from datetime import datetime, timedelta, timezone

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from home.models import EngRusDict
from users.forms import LearningWords

from django.contrib import messages

from users.models import Profile, LearnedWords


def home(request):
    return render(request, 'home/mainPage.html')


def AddWord(user_id, word_id):
    learned_word = LearnedWords()
    learned_word.user_id = user_id
    learned_word.word_id = word_id
    learned_word.last_repeating = datetime.now(timezone.utc)
    learned_word.save()

@login_required
def learn(request):
    words_ids = LearnedWords.objects.filter(user_id=request.user.id).values_list('word_id')
    word_to_check = EngRusDict.objects.exclude(id__in=words_ids)[0]
    ru = word_to_check.rus
    eng = word_to_check.eng
    if request.method == 'POST':
        form = LearningWords(request.POST)
        if form.is_valid() and form.cleaned_data.get('word') == eng:
            messages.success(request, 'Отлично, теперь Вы знаете на 1 слово больше!')
            AddWord(request.user.id, word_to_check.id)
            return redirect('learn')
        else:
            messages.error(request, 'Неверно, попробуйте еще раз!')
            return redirect('learn')
    else:
        form = LearningWords()
        form.set_word_to_check(word_to_check)
    return render(request, 'home/learnPage.html', {'ru': ru, 'eng': eng, 'form': form})


@login_required
def repeat(request):
    learned_words = LearnedWords.objects.filter(user_id=request.user.id).order_by('forgetting_coef')
    if len(learned_words) == 0:
        return render(request, 'home/nothingToRepeatPage.html')
    learned_word = learned_words.first()
    word_to_check = learned_word.word
    message = word_to_check.rus
    if request.method == 'POST':
        form = LearningWords(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('word') == word_to_check.eng:
                request.user.profile.learning_level *= 0.9
                learned_word.repeating += 1
                messages.success(request, "Верный ответ!")
            else:
                request.user.profile.learning_level /= 0.9
                learned_word.repeating = 1
                messages.error(request, f'Вы ошиблись! Правильный ответ: {word_to_check}.')
            timepassed = datetime.now(timezone.utc) - learned_word.last_repeating
            learned_word.forgetting_coef = (1 + 2 ** learned_word.repeating *
                                                      request.user.profile.learning_level * timepassed.total_seconds() /
                                                      timedelta(hours=1).total_seconds()) ** (-1 / (2 ** learned_word.repeating))
            learned_word.last_repeating = datetime.now(timezone.utc)
            learned_word.save()
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
        messages_list.append({'username': profile.user.username, 'rating': round(profile.rating, 2), 'i': i})
        i += 1
    return render(request, 'home/competePage.html', {'messages_list': messages_list})
