from modeltranslation.translator import register, TranslationOptions
from .models import Subject, Test, Question, Answer


@register(Subject)
class SubjectTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Test)
class TestTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = ("question_text",)


@register(Answer)
class AnswerTranslationOptions(TranslationOptions):
    fields = ("answer_text",)
