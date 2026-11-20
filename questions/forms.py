from django import forms
from django.core.exceptions import ValidationError
from .models import Question, Answer, Tag


class QuestionForm(forms.ModelForm):
    tags_input = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Теги через запятую'}),
        label='Теги',
        required=False
    )

    class Meta:
        model = Question
        fields = ['title', 'text']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст вопроса',
        }

    def save(self, commit=True, author=None):
        question = super().save(commit=False)
        if author:
            question.author = author

        if commit:
            question.save()

            tags_input = self.cleaned_data.get('tags_input', '')
            if tags_input:
                tag_names = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                tags = []
                for tag_name in tag_names:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    tags.append(tag)
                question.tags.set(tags)

        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
        labels = {
            'text': 'Ответ',
        }

    def save(self, commit=True, author=None, question=None):
        answer = super().save(commit=False)
        if author:
            answer.author = author
        if question:
            answer.question = question

        if commit:
            answer.save()

        return answer
