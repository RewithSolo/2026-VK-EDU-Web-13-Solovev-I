from django.shortcuts import render, get_object_or_404
from django.http import Http404
from core.utils import paginate
from .models import Question, Tag, Answer

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
    questions = Question.objects.filter(tags=tag).new()
    page_obj = paginate(questions, request, per_page=10)
    return render(request, 'questions/index.html', {'page_obj': page_obj, 'tag': tag})

def question_detail(request, question_id):
    question = get_object_or_404(Question.objects.with_related(), pk=question_id)
    answers = question.answers.select_related('author', 'author__profile')
    page_obj = paginate(answers, request, per_page=10)
    return render(request, 'questions/question.html', {'question': question, 'page_obj': page_obj})

def ask(request):
    return render(request, 'questions/ask.html')