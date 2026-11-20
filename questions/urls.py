from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('questions/<int:question_id>/', views.question_detail, name='question'),
    path('ask/', views.ask, name='ask'),
    path('questions/<int:question_id>/answer/', views.answer, name='answer'),
    path('api/questions/<int:question_id>/vote/', views.vote_question, name='vote_question'),
    path('api/answers/<int:answer_id>/vote/', views.vote_answer, name='vote_answer'),
    path('api/answers/<int:answer_id>/correct/', views.mark_correct, name='mark_correct'),
]