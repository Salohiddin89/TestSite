from django.contrib import admin
from .models import (
    Subject,
    Test,
    Question,
    Answer,
    UserProfile,
    UserTestAttempt,
    UserAnswer,
)
import csv
from django.http import HttpResponse
from django.utils.html import format_html
from django import forms


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    max_num = 4
    fields = ("order", "answer_text", "is_correct")
    ordering = ("order",)


class QuestionForm(forms.ModelForm):
    """Question form - testni tanlash uchun"""

    class Meta:
        model = Question
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "test" in self.fields:
            self.fields["test"].queryset = Test.objects.all().order_by(
                "subject", "order"
            )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "test_count",
        "random_test_question_count",
        "random_test_min_score",
        "created_at",
    ]
    search_fields = ["name"]
    list_filter = ["created_at"]
    list_editable = ["random_test_question_count", "random_test_min_score"]

    def test_count(self, obj):
        return obj.tests.count()

    test_count.short_description = "Testlar soni"


class QuestionInline(admin.StackedInline):
    model = Question
    form = QuestionForm
    extra = 1
    show_change_link = True
    fields = ("order", "question_text")
    ordering = ("order",)


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "subject",
        "order",
        "min_score_to_unlock",
        "question_count",
        "created_at",
    ]
    list_filter = ["subject", "created_at"]
    search_fields = ["name"]
    inlines = [QuestionInline]
    list_editable = ["order", "min_score_to_unlock"]

    def question_count(self, obj):
        return obj.questions.count()

    question_count.short_description = "Savollar soni"


class AnswerForm(forms.ModelForm):
    """Answer form - question ni tanlash uchun"""

    class Meta:
        model = Answer
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "question" in self.fields:
            self.fields["question"].queryset = (
                Question.objects.all()
                .select_related("test__subject")
                .order_by("test__subject__name", "test__order", "order")
            )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = QuestionForm
    list_display = [
        "short_question_text",
        "test",
        "subject_name",
        "order",
        "answer_count",
    ]
    list_filter = ["test__subject", "test"]
    search_fields = ["question_text"]
    inlines = [AnswerInline]
    list_editable = ["order"]
    actions = ["export_questions"]

    def short_question_text(self, obj):
        return (
            obj.question_text[:50] + "..."
            if len(obj.question_text) > 50
            else obj.question_text
        )

    short_question_text.short_description = "Savol"

    def subject_name(self, obj):
        return obj.test.subject.name

    subject_name.short_description = "Fan"

    def answer_count(self, obj):
        return obj.answers.count()

    answer_count.short_description = "Javoblar"

    def export_questions(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="questions.csv"'

        writer = csv.writer(response)
        writer.writerow(["Test", "Savol", "A", "B", "C", "D", "To'g'ri javob"])

        for question in queryset:
            answers = list(question.answers.all().order_by("order"))
            correct_answer = question.answers.filter(is_correct=True).first()

            # Har doim 4 ta javob bo'lishi uchun
            answer_texts = ["", "", "", ""]
            for i, answer in enumerate(answers[:4]):
                answer_texts[i] = answer.answer_text

            writer.writerow(
                [
                    question.test.name,
                    question.question_text,
                    answer_texts[0],
                    answer_texts[1],
                    answer_texts[2],
                    answer_texts[3],
                    correct_answer.order if correct_answer else "",
                ]
            )

        return response

    export_questions.short_description = "Tanlangan savollarni eksport qilish"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    form = AnswerForm
    list_display = [
        "short_answer_text",
        "question_text",
        "order",
        "is_correct",
        "is_correct_badge",
    ]
    list_filter = ["is_correct", "order", "question__test__subject"]
    search_fields = ["answer_text", "question__question_text"]
    list_editable = ["order", "is_correct"]

    def short_answer_text(self, obj):
        return (
            obj.answer_text[:50] + "..."
            if len(obj.answer_text) > 50
            else obj.answer_text
        )

    short_answer_text.short_description = "Javob"

    def question_text(self, obj):
        question_text = obj.question.question_text
        return question_text[:50] + "..." if len(question_text) > 50 else question_text

    question_text.short_description = "Savol"

    def is_correct_badge(self, obj):
        if obj.is_correct:
            return format_html(
                "<span style=\"color: green; font-weight: bold;\">✓ To'g'ri</span>"
            )
        return format_html("<span style=\"color: red;\">✗ Noto'g'ri</span>")

    is_correct_badge.short_description = "Holati (badge)"


class BulkQuestionForm(forms.Form):
    """Ko'p savollarni bir vaqtda kiritish uchun form"""

    test = forms.ModelChoiceField(queryset=Test.objects.all(), label="Test")
    questions_file = forms.FileField(
        label="CSV fayl", help_text="CSV formatda: savol,A,B,C,D,to'gri_javob (a,b,c,d)"
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "first_name", "last_name", "created_at"]
    search_fields = ["first_name", "last_name", "user__username"]
    list_filter = ["created_at"]


class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0
    readonly_fields = ["question", "selected_answer", "is_correct"]
    can_delete = False


@admin.register(UserTestAttempt)
class UserTestAttemptAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "get_test_name",
        "score",
        "total_questions",
        "score_percentage",
        "is_passed_badge",
        "completed_at",
    ]
    list_filter = ["completed", "is_random", "test__subject"]
    search_fields = ["user__username", "test__name"]
    inlines = [UserAnswerInline]
    readonly_fields = [
        "user",
        "test",
        "score",
        "total_questions",
        "started_at",
        "completed_at",
        "is_random",
    ]

    def get_test_name(self, obj):
        if obj.is_random:
            return "Random Test"
        return obj.test.name if obj.test else "Noma'lum"

    get_test_name.short_description = "Test"

    def score_percentage(self, obj):
        return f"{obj.score_percentage:.1f}%"

    score_percentage.short_description = "Foiz"

    def is_passed_badge(self, obj):
        if obj.is_passed:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ O\'tdi</span>'
            )
        return format_html('<span style="color: red;">✗ O\'ta olmadi</span>')

    is_passed_badge.short_description = "Holati"


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ["attempt", "question", "selected_answer", "is_correct"]
    list_filter = ["is_correct", "attempt__is_random"]
    readonly_fields = ["attempt", "question", "selected_answer", "is_correct"]
