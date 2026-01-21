from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    name = models.CharField(max_length=200, verbose_name="Fan nomi")
    image = models.ImageField(upload_to="subjects/", verbose_name="Rasm")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    created_at = models.DateTimeField(auto_now_add=True)

    # Random test uchun sozlamalar
    random_test_question_count = models.IntegerField(
        default=20, verbose_name="Random test savollar soni"
    )
    random_test_min_score = models.IntegerField(
        default=60, verbose_name="Random test minimal ball %"
    )

    class Meta:
        verbose_name = "Fan"
        verbose_name_plural = "Fanlar"

    def __str__(self):
        return self.name

    def unlocked_tests_for_user(self, user):
        """Foydalanuvchi uchun ochilgan testlar"""
        tests = self.tests.all().order_by("order")
        unlocked_tests = []

        for test in tests:
            last_attempt = (
                UserTestAttempt.objects.filter(user=user, test=test, completed=True)
                .order_by("-completed_at")
                .first()
            )

            if test.order == 1:  # Birinchi test har doim ochiq
                unlocked_tests.append(test)
            elif (
                last_attempt
                and last_attempt.score_percentage >= test.min_score_to_unlock
            ):
                unlocked_tests.append(test)

        return unlocked_tests


class Test(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="tests", verbose_name="Fan"
    )
    name = models.CharField(max_length=200, verbose_name="Test nomi")
    order = models.IntegerField(default=1, verbose_name="Tartib raqami")
    min_score_to_unlock = models.IntegerField(
        default=80, verbose_name="Keyingi test uchun minimal ball %"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Test"
        verbose_name_plural = "Testlar"
        ordering = ["order"]
        unique_together = ["subject", "order"]

    def __str__(self):
        return f"{self.subject.name} - {self.name}"

    def next_test(self):
        """Keyingi testni qaytaradi"""
        return Test.objects.filter(subject=self.subject, order=self.order + 1).first()

    def is_unlocked_for_user(self, user):
        """Foydalanuvchi uchun test ochiqmi"""
        if self.order == 1:
            return True

        previous_test = Test.objects.filter(
            subject=self.subject, order=self.order - 1
        ).first()

        if not previous_test:
            return True

        last_attempt = (
            UserTestAttempt.objects.filter(
                user=user, test=previous_test, completed=True
            )
            .order_by("-completed_at")
            .first()
        )

        if (
            last_attempt
            and last_attempt.score_percentage >= previous_test.min_score_to_unlock
        ):
            return True

        return False


class Question(models.Model):
    test = models.ForeignKey(
        Test, on_delete=models.CASCADE, related_name="questions", verbose_name="Test"
    )
    question_text = models.TextField(verbose_name="Savol matni")
    order = models.IntegerField(default=1, verbose_name="Tartib raqami")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"
        ordering = ["order"]

    def __str__(self):
        return f"{self.test.name} - Savol {self.order}"

    def correct_answer(self):
        """To'g'ri javobni qaytaradi"""
        return self.answers.filter(is_correct=True).first()


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers", verbose_name="Savol"
    )
    answer_text = models.CharField(max_length=500, verbose_name="Javob matni")
    is_correct = models.BooleanField(default=False, verbose_name="To'g'ri javob")
    order = models.CharField(
        max_length=1,
        choices=[("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")],
        verbose_name="Harf",
    )

    class Meta:
        verbose_name = "Javob"
        verbose_name_plural = "Javoblar"
        ordering = ["order"]

    def __str__(self):
        return f"{self.order}) {self.answer_text[:50]}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=100, verbose_name="Ism")
    last_name = models.CharField(max_length=100, verbose_name="Familiya")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foydalanuvchi profili"
        verbose_name_plural = "Foydalanuvchilar profili"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class UserTestAttempt(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="test_attempts"
    )
    test = models.ForeignKey(
        Test, on_delete=models.CASCADE, related_name="attempts", null=True, blank=True
    )
    completed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_random = models.BooleanField(default=False, verbose_name="Random test")

    class Meta:
        verbose_name = "Test topshiruvi"
        verbose_name_plural = "Test topshiruvlari"
        ordering = ["-started_at"]

    def __str__(self):
        if self.is_random:
            return f"{self.user.username} - Random Test"
        return f"{self.user.username} - {self.test.name}"

    @property
    def score_percentage(self):
        """Foizdagi ball"""
        if self.total_questions > 0:
            return (self.score / self.total_questions) * 100
        return 0

    @property
    def is_passed(self):
        """Testdan o'tganmi?"""
        if self.is_random:
            return self.score_percentage >= 60  # Random test uchun default 60%
        if self.test:
            return self.score_percentage >= self.test.min_score_to_unlock
        return False

    @property
    def can_retake(self):
        """Qayta topshirish mumkinmi?"""
        if self.is_random:
            return False  # Random testni qayta topshirish mumkin emas
        return not self.is_passed


class UserAnswer(models.Model):
    attempt = models.ForeignKey(
        UserTestAttempt, on_delete=models.CASCADE, related_name="user_answers"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, null=True, blank=True
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Foydalanuvchi javobi"
        verbose_name_plural = "Foydalanuvchi javoblari"

    def __str__(self):
        return f"{self.attempt.user.username} - Savol {self.question.order}"
