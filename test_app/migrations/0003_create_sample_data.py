from django.db import migrations
from django.core.files.base import ContentFile
import random

# ===== SAVOL–JAVOB BANKLARI =====

PHYSICS_QA = [
    (
        "Nyutonning birinchi qonuni nimani ifodalaydi?",
        "Jismga kuch ta’sir qilmasa, u tinch yoki tekis harakatda bo‘ladi",
        ["Kuch massaga teng", "Energiya saqlanadi", "Bosim kuchga bog‘liq"],
    ),
]

CHEMISTRY_QA = [
    ("Suvning kimyoviy formulasi qaysi?", "H₂O", ["CO₂", "NaCl", "O₂"]),
]

BIOLOGY_QA = [
    ("Inson yuragi nechta kameradan iborat?", "4 ta", ["2 ta", "3 ta", "5 ta"]),
]

INFORMATICS_QA = [
    (
        "Python’da o‘zgaruvchi qanday e’lon qilinadi?",
        "a = 5",
        ["int a = 5", "var a := 5", "define a = 5"],
    ),
]

TEST_NAMES = [
    "Boshlang‘ich test",
    "O‘rta daraja test",
    "Murakkab test",
    "Ilg‘or test",
    "Yakuniy test",
]


def create_sample_data(apps, schema_editor):
    Subject = apps.get_model("test_app", "Subject")
    Test = apps.get_model("test_app", "Test")
    Question = apps.get_model("test_app", "Question")
    Answer = apps.get_model("test_app", "Answer")

    subjects_map = {
        "Matematika": None,  # maxsus ishlanadi
        "Fizika": PHYSICS_QA,
        "Kimyo": CHEMISTRY_QA,
        "Biologiya": BIOLOGY_QA,
        "Informatika": INFORMATICS_QA,
    }

    for subject_name, qa_list in subjects_map.items():
        subject = Subject.objects.create(
            name=subject_name,
            description=f"{subject_name} fanidan testlar",
            random_test_question_count=20,
            random_test_min_score=60,
        )
        subject.image.save("default.png", ContentFile(b""), save=True)

        # ===== 5 TA TEST =====
        for test_order, test_name in enumerate(TEST_NAMES, start=1):
            test = Test.objects.create(
                subject=subject,
                name=test_name,
                order=test_order,
                min_score_to_unlock=70 + test_order * 5,
            )

            # ===== 30 TA SAVOL =====
            for q_order in range(1, 31):
                # === MATEMATIKA ===
                if subject_name == "Matematika":
                    a = random.randint(10, 99)
                    b = random.randint(10, 99)
                    question_text = f"{a} + {b} = ?"
                    correct = str(a + b)
                    wrongs = list(
                        {
                            str(a + b + x)
                            for x in [-10, -5, -3, 3, 5, 10]
                            if a + b + x > 0
                        }
                    )[:3]

                # === BOSHQA FANLAR ===
                else:
                    qa = qa_list[(q_order - 1) % len(qa_list)]
                    question_text, correct, wrongs = qa

                question = Question.objects.create(
                    test=test,
                    question_text=question_text,
                    order=q_order,
                )

                options = [correct] + wrongs
                random.shuffle(options)
                letters = ["a", "b", "c", "d"]

                for letter, text in zip(letters, options):
                    Answer.objects.create(
                        question=question,
                        answer_text=text,
                        is_correct=(text == correct),
                        order=letter,
                    )


def reverse_func(apps, schema_editor):
    Subject = apps.get_model("test_app", "Subject")
    Subject.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("test_app", "0002_subject_random_test_min_score_and_more"),
    ]

    operations = [
        migrations.RunPython(create_sample_data, reverse_func),
    ]
