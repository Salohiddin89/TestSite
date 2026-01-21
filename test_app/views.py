from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db.models import Q
import random
import json

from .models import (
    Subject,
    Test,
    Question,
    Answer,
    UserProfile,
    UserTestAttempt,
    UserAnswer,
)


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        if password != password2:
            messages.error(request, _("Parollar bir xil emas!"))
            return render(request, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, _("Bu username band!"))
            return render(request, "register.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        UserProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
        )

        login(request, user)
        messages.success(request, _("Ro‘yxatdan muvaffaqiyatli o‘tdingiz!"))
        return redirect("home")

    return render(request, "register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, _("Tizimga muvaffaqiyatli kirdingiz!"))
            return redirect("home")
        else:
            messages.error(request, _("Username yoki parol noto‘g‘ri!"))

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    messages.info(request, _("Siz tizimdan chiqdingiz."))
    return redirect("login")


@login_required
def home_view(request):
    subjects = Subject.objects.all()
    return render(request, "home.html", {"subjects": subjects})


@login_required
def subject_tests_view(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    tests = subject.tests.all().order_by("order")

    test_data = []
    for test in tests:
        last_attempt = (
            UserTestAttempt.objects.filter(
                user=request.user,
                test=test,
                completed=True,
            )
            .order_by("-completed_at")
            .first()
        )

        is_unlocked = test.is_unlocked_for_user(request.user)

        test_data.append(
            {
                "test": test,
                "is_unlocked": is_unlocked,
                "attempted": last_attempt is not None,
                "score": last_attempt.score if last_attempt else 0,
                "total": last_attempt.total_questions if last_attempt else 0,
                "percentage": last_attempt.score_percentage if last_attempt else 0,
                "passed": last_attempt.is_passed if last_attempt else False,
                "can_retake": last_attempt.can_retake if last_attempt else False,
            }
        )

    unlocked_tests = [td["test"] for td in test_data if td["is_unlocked"]]
    can_take_random = len(unlocked_tests) > 0

    return render(
        request,
        "subject_tests.html",
        {
            "subject": subject,
            "test_data": test_data,
            "can_take_random": can_take_random,
        },
    )


@login_required
def take_test_view(request, test_id):
    test = get_object_or_404(Test, id=test_id)

    if not test.is_unlocked_for_user(request.user):
        messages.error(
            request,
            _("Bu test hali ochilmagan! Avval oldingi testdan o‘tishingiz kerak."),
        )
        return redirect("subject_tests", subject_id=test.subject.id)

    questions = test.questions.all().order_by("order").prefetch_related("answers")

    last_attempt = (
        UserTestAttempt.objects.filter(
            user=request.user,
            test=test,
            completed=True,
        )
        .order_by("-completed_at")
        .first()
    )

    previous_answers = {}
    if last_attempt:
        for user_answer in last_attempt.user_answers.all():
            previous_answers[user_answer.question.id] = {
                "selected": user_answer.selected_answer.id
                if user_answer.selected_answer
                else None,
                "is_correct": user_answer.is_correct,
            }

    return render(
        request,
        "take_test.html",
        {
            "test": test,
            "questions": questions,
            "previous_answers": json.dumps(previous_answers),
            "has_previous": last_attempt is not None,
            "min_score_to_unlock": test.min_score_to_unlock,
        },
    )


@login_required
def submit_test_view(request, test_id):
    if request.method != "POST":
        return redirect("home")

    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all()

    attempt = UserTestAttempt.objects.create(
        user=request.user,
        test=test,
        total_questions=questions.count(),
    )

    correct_count = 0

    for question in questions:
        answer_id = request.POST.get(f"question_{question.id}")
        if answer_id:
            try:
                selected_answer = Answer.objects.get(id=answer_id)
                is_correct = selected_answer.is_correct

                UserAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_answer=selected_answer,
                    is_correct=is_correct,
                )

                if is_correct:
                    correct_count += 1
            except Answer.DoesNotExist:
                pass

    attempt.score = correct_count
    attempt.completed = True
    attempt.completed_at = timezone.now()
    attempt.save()

    next_test = test.next_test()
    if attempt.is_passed and next_test:
        messages.success(
            request,
            _(
                "Tabriklaymiz! Siz %(test)s testidan muvaffaqiyatli o‘tdingiz. Keyingi test ochildi."
            )
            % {"test": test.name},
        )
    elif not attempt.is_passed:
        messages.warning(
            request,
            _("Siz %(test)s testidan o‘ta olmadingiz. Minimal ball: %(min)s%%.")
            % {"test": test.name, "min": test.min_score_to_unlock},
        )
    else:
        messages.success(
            request,
            _("Tabriklaymiz! Siz %(test)s testidan muvaffaqiyatli o‘tdingiz.")
            % {"test": test.name},
        )

    return redirect("test_result", attempt_id=attempt.id)


@login_required
def test_result_view(request, attempt_id):
    attempt = get_object_or_404(
        UserTestAttempt,
        id=attempt_id,
        user=request.user,
    )

    user_answers = attempt.user_answers.all().select_related(
        "question",
        "selected_answer",
    )

    results = []
    for user_answer in user_answers:
        correct_answer = user_answer.question.answers.filter(is_correct=True).first()
        results.append(
            {
                "question": user_answer.question,
                "selected_answer": user_answer.selected_answer,
                "correct_answer": correct_answer,
                "is_correct": user_answer.is_correct,
                "all_answers": user_answer.question.answers.all(),
            }
        )

    return render(
        request,
        "test_result.html",
        {
            "attempt": attempt,
            "results": results,
            "min_score": attempt.test.min_score_to_unlock if attempt.test else 80,
        },
    )


@login_required
def profile_view(request):
    profile = request.user.profile
    attempts = UserTestAttempt.objects.filter(
        user=request.user,
        completed=True,
    ).order_by("-completed_at")

    total_attempts = attempts.count()
    passed_attempts = sum(1 for a in attempts if a.is_passed)
    average_score = (
        sum(a.score_percentage for a in attempts) / total_attempts
        if total_attempts > 0
        else 0
    )

    return render(
        request,
        "profile.html",
        {
            "profile": profile,
            "attempts": attempts,
            "total_attempts": total_attempts,
            "passed_attempts": passed_attempts,
            "average_score": average_score,
        },
    )


@login_required
def retake_test_view(request, test_id):
    test = get_object_or_404(Test, id=test_id)

    if request.method == "POST":
        last_attempt = (
            UserTestAttempt.objects.filter(
                user=request.user,
                test=test,
                completed=True,
            )
            .order_by("-completed_at")
            .first()
        )

        if last_attempt and last_attempt.can_retake:
            UserTestAttempt.objects.filter(
                user=request.user,
                test=test,
            ).delete()

            messages.info(
                request,
                _("Test qayta topshirish uchun tayyor!"),
            )
            return redirect("take_test", test_id=test_id)
        else:
            messages.error(
                request,
                _("Siz bu testdan allaqachon o‘tgansiz! Qayta topshirish mumkin emas."),
            )

    return redirect("subject_tests", subject_id=test.subject.id)


# ================= RANDOM TEST =================


@login_required
def take_random_test_view(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    tests = subject.tests.all()
    unlocked_tests = [t for t in tests if t.is_unlocked_for_user(request.user)]

    if not unlocked_tests:
        messages.error(request, _("Sizda hali ochilgan testlar mavjud emas!"))
        return redirect("subject_tests", subject_id=subject_id)

    all_questions = []
    for test in unlocked_tests:
        all_questions.extend(list(test.questions.all()))

    question_count = min(subject.random_test_question_count, len(all_questions))
    if question_count < 5:
        messages.error(
            request,
            _("Random test uchun yetarli savol mavjud emas!"),
        )
        return redirect("subject_tests", subject_id=subject_id)

    random_questions = random.sample(all_questions, question_count)

    random_test = {
        "id": 0,
        "name": f"{subject.name} - Random Test",
        "subject": subject,
        "is_random": True,
    }

    return render(
        request,
        "take_random_test.html",
        {
            "test": random_test,
            "questions": random_questions,
            "subject": subject,
            "question_count": question_count,
        },
    )


@login_required
def submit_random_test_view(request, subject_id):
    if request.method != "POST":
        return redirect("home")

    subject = get_object_or_404(Subject, id=subject_id)
    question_ids = [int(i) for i in request.POST.getlist("question_ids[]") if i]

    if not question_ids:
        messages.error(request, _("Savollar topilmadi!"))
        return redirect("subject_tests", subject_id=subject_id)

    attempt = UserTestAttempt.objects.create(
        user=request.user,
        test=None,
        total_questions=len(question_ids),
        is_random=True,
    )

    correct_count = 0

    for q_id in question_ids:
        question = get_object_or_404(Question, id=q_id)
        answer_id = request.POST.get(f"question_{q_id}")

        if answer_id:
            try:
                selected_answer = Answer.objects.get(id=answer_id)
                is_correct = selected_answer.is_correct

                UserAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_answer=selected_answer,
                    is_correct=is_correct,
                )

                if is_correct:
                    correct_count += 1
            except (Answer.DoesNotExist, ValueError):
                pass

    attempt.score = correct_count
    attempt.completed = True
    attempt.completed_at = timezone.now()
    attempt.save()

    percentage = (correct_count / len(question_ids)) * 100 if question_ids else 0

    if percentage >= subject.random_test_min_score:
        messages.success(
            request,
            _("Tabriklaymiz! Random testdan %(percent).1f%% ball to‘pladingiz.")
            % {"percent": percentage},
        )
    else:
        messages.warning(
            request,
            _(
                "Random testdan %(percent).1f%% ball to‘pladingiz. Minimal %(min)s%% kerak."
            )
            % {
                "percent": percentage,
                "min": subject.random_test_min_score,
            },
        )

    return redirect("random_test_result", attempt_id=attempt.id)


@login_required
def random_test_result_view(request, attempt_id):
    attempt = get_object_or_404(
        UserTestAttempt,
        id=attempt_id,
        user=request.user,
        is_random=True,
    )

    user_answers = attempt.user_answers.all().select_related(
        "question",
        "selected_answer",
        "question__test",
    )

    results = []
    for user_answer in user_answers:
        correct_answer = user_answer.question.answers.filter(is_correct=True).first()
        results.append(
            {
                "question": user_answer.question,
                "selected_answer": user_answer.selected_answer,
                "correct_answer": correct_answer,
                "is_correct": user_answer.is_correct,
                "all_answers": user_answer.question.answers.all(),
                "test_name": user_answer.question.test.name,
            }
        )

    return render(
        request,
        "random_test_result.html",
        {
            "attempt": attempt,
            "results": results,
            "min_score": 60,
        },
    )
