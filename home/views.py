from datetime import datetime, timedelta, timezone

from django.core.management import call_command
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from home.models import EngRusDict
from users.forms import LearningWords

from django.contrib import messages

from users.management.commands import update_stat
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
    if request.user.profile.learning_word == "":
        words_ids = LearnedWords.objects.filter(user_id=request.user.id).values_list('word_id')
        word_to_learn = EngRusDict.objects.exclude(id__in=words_ids)[0]
        request.user.profile.learning_word = str(word_to_learn.id) + "," + word_to_learn.rus + "," + word_to_learn.eng
        request.user.profile.save()
    word_id, ru, eng = request.user.profile.learning_word.split(",")
    if request.method == 'POST':
        form = LearningWords(request.POST)
        if form.is_valid() and form.cleaned_data.get('word') == eng:
            messages.success(request, 'Отлично, теперь Вы знаете на 1 слово больше!')
            request.user.profile.learning_word = ""
            request.user.profile.save()
            AddWord(request.user.id, int(word_id))
            return redirect('learn')
        else:
            messages.error(request, 'Неверно, попробуйте еще раз!')
            return redirect('learn')
    else:
        form = LearningWords()
    return render(request, 'home/learnPage.html', {'ru': ru, 'eng': eng, 'form': form})


@login_required
def repeat(request):
    learned_words = LearnedWords.objects.filter(user_id=request.user.id).order_by('forgetting_coef')
    if len(learned_words) == 0:
        return render(request, 'home/nothingToRepeatPage.html')
    if request.user.profile.repeating_word == "":
        learned_word = learned_words.first()
        request.user.profile.repeating_word = str(learned_word.pk)
        request.user.profile.save()
    learned_word = LearnedWords.objects.filter(pk=int(request.user.profile.repeating_word)).first()
    curr_word = learned_word.word
    message = curr_word.rus
    if request.method == 'POST':
        form = LearningWords(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('word') == curr_word.eng:
                request.user.profile.learning_level *= 0.9
                learned_word.repeating += 1
                messages.success(request, "Верный ответ!")
            else:
                request.user.profile.learning_level /= 0.9
                learned_word.repeating = 1
                messages.error(request, f'Вы ошиблись! Правильный ответ: {curr_word}.')
            request.user.profile.repeating_word = ""
            learned_word.last_repeating = datetime.now(timezone.utc)
            learned_word.save()
            call_command('update_stat')
            request.user.profile.save()
            return redirect('repeat')
    else:
        form = LearningWords()
    return render(request, 'home/repeatPage.html', {'message': message, 'form': form})


def compete(request):
    profiles = Profile.objects.all().order_by('-rating')[:10]
    messages_list = []
    i = 1
    for profile in profiles:
        messages_list.append({'username': profile.user.username, 'rating': round(profile.rating, 2), 'i': i})
        i += 1
    return render(request, 'home/competePage.html', {'messages_list': messages_list})
