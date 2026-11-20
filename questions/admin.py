from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fields = ('avatar',)
    verbose_name_plural = 'Профиль'


class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ('author', 'text', 'rating', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = False


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'rating', 'created_at')
    list_filter = ('created_at', 'rating', 'tags')
    search_fields = ('title', 'text', 'author__username')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'text', 'author')
        }),
        ('Метаданные', {
            'fields': ('rating', 'created_at')
        }),
        ('Теги', {
            'fields': ('tags',)
        }),
    )
    filter_horizontal = ('tags',)
    inlines = (AnswerInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'author__profile').prefetch_related('tags')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('get_question', 'author', 'rating', 'is_correct', 'created_at')
    list_filter = ('created_at', 'rating', 'is_correct', 'question')
    search_fields = ('text', 'author__username', 'question__title')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('question', 'author', 'text')
        }),
        ('Метаданные', {
            'fields': ('rating', 'is_correct', 'created_at')
        }),
    )

    def get_question(self, obj):
        return obj.question.title[:50]
    get_question.short_description = 'Вопрос'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('question', 'author', 'author__profile')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('get_question', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('question__title', 'user__username')
    readonly_fields = ('created_at',)

    def get_question(self, obj):
        return obj.question.title[:50]
    get_question.short_description = 'Вопрос'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('question', 'user')


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('get_answer', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('answer__text', 'user__username', 'answer__question__title')
    readonly_fields = ('created_at',)

    def get_answer(self, obj):
        return f"{obj.answer.question.title[:30]}..."
    get_answer.short_description = 'Ответ'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('answer', 'answer__question', 'user')
