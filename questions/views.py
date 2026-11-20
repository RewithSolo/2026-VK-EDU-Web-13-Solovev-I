from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import F
from core.utils import paginate
from .models import Question, Tag, Answer, QuestionLike, AnswerLike
from .forms import QuestionForm, AnswerForm


def index(request):
    questions = Question.objects.new()
    page_obj = paginate(questions, request, per_page=10)
    return render(request, 'questions/index.html', {'page_obj': page_obj})


def hot(request):
    questions = Question.objects.best()
    page_obj = paginate(questions, request, per_page=10)
    return render(request, 'questions/index.html', {'page_obj': page_obj})


def tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.with_related().filter(tags=tag).order_by("-created_at")
    page_obj = paginate(questions, request, per_page=10)
    return render(request, 'questions/index.html', {'page_obj': page_obj, 'tag': tag})


def question_detail(request, question_id):
    question = get_object_or_404(Question.objects.with_related(), pk=question_id)
    answers = question.answers.select_related('author', 'author__profile')
    page_obj = paginate(answers, request, per_page=10)
    return render(request, 'questions/question.html', {'question': question, 'page_obj': page_obj})


@require_http_methods(['GET', 'POST'])
def ask(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(author=request.user)
            return redirect('question', question_id=question.id)
    else:
        form = QuestionForm()

    return render(request, 'questions/ask.html', {'form': form})


@require_POST
def answer(request, question_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)

    question = get_object_or_404(Question, pk=question_id)

    form = AnswerForm(request.POST)
    if form.is_valid():
        answer_obj = form.save(author=request.user, question=question)
        return redirect(f'/questions/{question_id}/#answer-{answer_obj.id}')

    return redirect('question', question_id=question_id)


@require_POST
def vote_question(request, question_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)

    if request.content_type != 'application/json':
        return JsonResponse({'error': 'Content-Type должен быть application/json'}, status=400)

    import json
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Невалидный JSON'}, status=400)

    question = get_object_or_404(Question, pk=question_id)
    vote_type = data.get('type')

    if vote_type not in ['up', 'down']:
        return JsonResponse({'error': 'Невалидный тип голоса'}, status=400)

    like_exists = QuestionLike.objects.filter(question=question, user=request.user).exists()

    if like_exists:
        return JsonResponse({'error': 'Вы уже голосовали за этот вопрос'}, status=400)

    QuestionLike.objects.create(question=question, user=request.user)

    if vote_type == 'up':
        question.rating = F('rating') + 1
    else:
        question.rating = F('rating') - 1

    question.save(update_fields=['rating'])
    question.refresh_from_db()

    return JsonResponse({'rating': question.rating})


@require_POST
def vote_answer(request, answer_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)

    if request.content_type != 'application/json':
        return JsonResponse({'error': 'Content-Type должен быть application/json'}, status=400)

    import json
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Невалидный JSON'}, status=400)

    answer_obj = get_object_or_404(Answer, pk=answer_id)
    vote_type = data.get('type')

    if vote_type not in ['up', 'down']:
        return JsonResponse({'error': 'Невалидный тип голоса'}, status=400)

    like_exists = AnswerLike.objects.filter(answer=answer_obj, user=request.user).exists()

    if like_exists:
        return JsonResponse({'error': 'Вы уже голосовали за этот ответ'}, status=400)

    AnswerLike.objects.create(answer=answer_obj, user=request.user)

    if vote_type == 'up':
        answer_obj.rating = F('rating') + 1
    else:
        answer_obj.rating = F('rating') - 1

    answer_obj.save(update_fields=['rating'])
    answer_obj.refresh_from_db()

    return JsonResponse({'rating': answer_obj.rating})


@require_POST
def mark_correct(request, answer_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)

    if request.content_type != 'application/json':
        return JsonResponse({'error': 'Content-Type должен быть application/json'}, status=400)

    answer_obj = get_object_or_404(Answer, pk=answer_id)

    if answer_obj.question.author != request.user:
        return JsonResponse({'error': 'Только автор вопроса может выбирать правильный ответ'}, status=403)

    answer_obj.is_correct = not answer_obj.is_correct
    answer_obj.save(update_fields=['is_correct'])

    return JsonResponse({'is_correct': answer_obj.is_correct})