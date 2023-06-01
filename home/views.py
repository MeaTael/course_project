from datetime import datetime, timedelta, timezone

from django.core.management import call_command
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from home.models import EngRusDict
from users.forms import LearningWords

from django.contrib import messages

from users.management.commands import update_stat
from users.models import Profile, LearnedWords

from Levenshtein import distance
from hunspell import Hunspell
h_ru = Hunspell('/usr/share/hunspell/ru_RU')
h_en = Hunspell('/usr/share/hunspell/en_US')


def get_min_coef(wrong_word, words):
    possible_word = max(words, key=lambda x: len(x))
    min_dist = len(possible_word)
    for word in words:
        dist = distance(wrong_word, word)
        if dist < min_dist:
            min_dist = dist
            possible_word = word
    return min_dist/len(possible_word), possible_word

def get_words(word):
    if h_ru.spell(word):
        return h_ru.suggest(word)
    if h_en.spell(word):
        return h_en.suggest(word)
    return word



def home(request):
    return render(request, 'home/mainPage.html')


def AddWord(user_id, word_id):
    learned_word = LearnedWords()
    learned_word.user_id = user_id
    learned_word.word_id = word_id
    learned_word.last_repeating = datetime.now(timezone.utc)
    learned_word.learning_date = datetime.now(timezone.utc).date()
    learned_word.save()


@login_required
def switch(request):
    request.user.profile.mode = (request.user.profile.mode + 1) % 2
    request.user.profile.save()
    referer = request.META.get("HTTP_REFERER").split('/')[-2]
    return redirect(referer)


@login_required
def learn(request):
    if len(LearnedWords.objects.filter(user_id=request.user.id, learning_date=datetime.now(timezone.utc).date())) >= 5:
        return render(request, 'home/nothingToLearnPage.html')
    if request.user.profile.learning_word == "":
        words_ids = LearnedWords.objects.filter(user_id=request.user.id).values_list('word_id')
        word_to_learn = EngRusDict.objects.exclude(id__in=words_ids)[0]
        request.user.profile.learning_word = str(word_to_learn.id) + "," + word_to_learn.rus + "," + word_to_learn.eng
        request.user.profile.save()
    if not request.user.profile.mode:
        word_id, from_, to_ = request.user.profile.learning_word.split(",")
    else:
        word_id, to_, from_ = request.user.profile.learning_word.split(",")
    if request.method == 'POST':
        form = LearningWords(request.POST)
        if form.is_valid() and form.cleaned_data.get('word').strip() == to_:
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
    return render(request, 'home/learnPage.html', {'from_': from_, 'to_': to_, 'mode': request.user.profile.mode, 'form': form})


@login_required
def repeat(request):
    learned_words = LearnedWords.objects.filter(user_id=request.user.id, forgetting_coef__lte=0.7).order_by('forgetting_coef')
    if len(learned_words) == 0:
        return render(request, 'home/nothingToRepeatPage.html')
    if request.user.profile.repeating_word == "":
        learned_word = learned_words.first()
        request.user.profile.repeating_word = str(learned_word.pk)
        request.user.profile.save()
    learned_word = LearnedWords.objects.filter(pk=int(request.user.profile.repeating_word)).first()
    curr_word = learned_word.word
    if not request.user.profile.mode:
        learned_words = LearnedWords.objects.filter(user_id=request.user.id, word__rus=curr_word.rus, forgetting_coef__lte=0.7).order_by('forgetting_coef')
        from_, to_ = curr_word.rus, dict()
        for word in learned_words:
            to_[word.word.eng] = word.pk
    else:
        learned_words = LearnedWords.objects.filter(user_id=request.user.id, word__eng=curr_word.eng, forgetting_coef__lte=0.7).order_by(
            'forgetting_coef')
        from_, to_ = curr_word.eng, dict()
        for word in learned_words:
            to_[word.word.rus] = word.pk
    message = from_
    if request.method == 'POST':
        form = LearningWords(request.POST)
        if form.is_valid():
            for word in form.cleaned_data.get('word').split(","):
                word.strip()
                base_word = word
                for w in get_words(word):
                    if w is not None:
                        for key in to_.keys():
                            if w.lower() == key.lower():
                                base_word = key
                                break
                if base_word.lower() in map(str.lower, to_.keys()):
                    learned_word = LearnedWords.objects.get(pk=to_[base_word])
                    request.user.profile.learning_level *= 0.9
                    learned_word.repeating += 1
                    to_.pop(base_word)
                    learned_word.last_repeating = datetime.now(timezone.utc)
                    messages.success(request, "Верный ответ!")
                else:
                    coef, possible_word = get_min_coef(word, to_.keys())
                    request.user.profile.learning_level /= 1 - (0.1 * coef)
                    learned_word = LearnedWords.objects.get(pk=to_[possible_word])
                    if coef <= 0.5:
                        learned_word.repeating = max(learned_word.repeating // 2, 1)
                    else:
                        learned_word.repeating = 1
                    to_.pop(possible_word)
                    messages.error(request, f'Вы ошиблись! Правильный ответ: {possible_word}.')
                    learned_word.last_repeating = datetime.now(timezone.utc)
            request.user.profile.repeating_word = ""
            learned_word.save()
            call_command('update_stat')
            request.user.profile.save()
            return redirect('repeat')
    else:
        form = LearningWords()
    return render(request, 'home/repeatPage.html', {'message': message, 'mode': request.user.profile.mode, 'form': form})


def compete(request):
    profiles = Profile.objects.all().order_by('-rating')[:10]
    messages_list = []
    i = 1
    for profile in profiles:
        messages_list.append({'username': profile.user.username, 'rating': round(profile.rating, 2), 'i': i})
        i += 1
    return render(request, 'home/competePage.html', {'messages_list': messages_list})
