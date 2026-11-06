from django.shortcuts import render
from core.utils import paginate

# Create your views here.

def get_questions():
    questions = []
    for i in range(1, 31):
        questions.append({
            'id': i,
            'title': f'Question title {i}',
            'text': f'This is the text of question number {i}. Lorem ipsum dolor sit amet.',
            'rating': i % 15,
            'answers_count': i % 7,
            'tags': ['bluelock', 'football', f'tag{i % 5}']
        })
    return questions

def index(request):
    questions = get_questions()
    page_obj = paginate(questions, request, per_page=5)
    return render(request, 'questions/index.html', {'page_obj': page_obj})

def hot(request):
    questions = get_questions()
    questions = list(reversed(questions))
    page_obj = paginate(questions, request, per_page=5)
    return render(request, 'questions/index.html', {'page_obj': page_obj})

def tag(request, tag_name):
    questions = get_questions()
    questions = [q for q in questions if tag_name in q['tags']]
    page_obj = paginate(questions, request, per_page=5)
    return render(request, 'questions/index.html', {'page_obj': page_obj})

def question(request, question_id):
    return render(request, 'questions/question.html', {'question_id': question_id})

def ask(request):
    return render(request, 'questions/ask.html')