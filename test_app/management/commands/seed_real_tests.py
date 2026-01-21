from django.core.management.base import BaseCommand
from test_app.models import Subject, Test, Question, Answer


class Command(BaseCommand):
    help = "Real mantiqiy savollar bilan 5 fanli testlar yaratadi (UZ/RU/EN)"

    def handle(self, *args, **options):
        subjects = [
            {
                "name": ("Matematika", "Математика", "Mathematics"),
                "questions": [
                    {
                        "q": (
                            "2, 4, 8, 16, ?",
                            "2, 4, 8, 16, ?",
                            "2, 4, 8, 16, ?",
                        ),
                        "answers": [
                            ("32", "32", "32"),
                            ("24", "24", "24"),
                            ("18", "18", "18"),
                            ("20", "20", "20"),
                        ],
                        "correct": 0,
                    },
                    {
                        "q": (
                            "Agar 5 × 6 = 30 bo‘lsa, 7 × 8 = ?",
                            "Если 5 × 6 = 30, то 7 × 8 = ?",
                            "If 5 × 6 = 30, then 7 × 8 = ?",
                        ),
                        "answers": [
                            ("56", "56", "56"),
                            ("54", "54", "54"),
                            ("48", "48", "48"),
                            ("64", "64", "64"),
                        ],
                        "correct": 0,
                    },
                ],
            },
            {
                "name": ("Mantiq", "Логика", "Logic"),
                "questions": [
                    {
                        "q": (
                            "Qaysi shakl boshqalardan farq qiladi?",
                            "Какая фигура отличается от других?",
                            "Which shape is different from the others?",
                        ),
                        "answers": [
                            ("Doira", "Круг", "Circle"),
                            ("Kvadrat", "Квадрат", "Square"),
                            ("Uchburchak", "Треугольник", "Triangle"),
                            ("To‘rtburchak", "Прямоугольник", "Rectangle"),
                        ],
                        "correct": 0,
                    },
                ],
            },
            {
                "name": ("Ingliz tili", "Английский язык", "English"),
                "questions": [
                    {
                        "q": (
                            "He ___ to school every day.",
                            "Он ___ в школу каждый день.",
                            "He ___ to school every day.",
                        ),
                        "answers": [
                            ("goes", "ходит", "goes"),
                            ("go", "идти", "go"),
                            ("going", "идущий", "going"),
                            ("gone", "ушёл", "gone"),
                        ],
                        "correct": 0,
                    },
                ],
            },
            {
                "name": ("Informatika", "Информатика", "Computer Science"),
                "questions": [
                    {
                        "q": (
                            "Algoritm nima?",
                            "Что такое алгоритм?",
                            "What is an algorithm?",
                        ),
                        "answers": [
                            (
                                "Muammoni yechish ketma-ketligi",
                                "Последовательность шагов решения",
                                "A sequence of steps to solve a problem",
                            ),
                            (
                                "Kompyuter",
                                "Компьютер",
                                "Computer",
                            ),
                            (
                                "Dasturlash tili",
                                "Язык программирования",
                                "Programming language",
                            ),
                            (
                                "Fayl",
                                "Файл",
                                "File",
                            ),
                        ],
                        "correct": 0,
                    },
                ],
            },
            {
                "name": ("Tarix", "История", "History"),
                "questions": [
                    {
                        "q": (
                            "Ikkinchi jahon urushi qachon tugagan?",
                            "Когда закончилась Вторая мировая война?",
                            "When did World War II end?",
                        ),
                        "answers": [
                            ("1945", "1945", "1945"),
                            ("1939", "1939", "1939"),
                            ("1950", "1950", "1950"),
                            ("1941", "1941", "1941"),
                        ],
                        "correct": 0,
                    },
                ],
            },
        ]

        for s in subjects:
            subject = Subject.objects.create(
                name_uz=s["name"][0],
                name_ru=s["name"][1],
                name_en=s["name"][2],
            )

            for t in range(1, 6):
                test = Test.objects.create(
                    subject=subject,
                    order=t,
                    name_uz=f"{s['name'][0]} Test {t}",
                    name_ru=f"{s['name'][1]} Тест {t}",
                    name_en=f"{s['name'][2]} Test {t}",
                )

                for i in range(25):
                    qdata = s["questions"][i % len(s["questions"])]

                    question = Question.objects.create(
                        test=test,
                        order=i + 1,
                        question_text_uz=qdata["q"][0],
                        question_text_ru=qdata["q"][1],
                        question_text_en=qdata["q"][2],
                    )

                    for idx, ans in enumerate(qdata["answers"]):
                        Answer.objects.create(
                            question=question,
                            order=chr(97 + idx),
                            is_correct=idx == qdata["correct"],
                            answer_text_uz=ans[0],
                            answer_text_ru=ans[1],
                            answer_text_en=ans[2],
                        )

        self.stdout.write(self.style.SUCCESS("✅ REAL mantiqiy testlar yaratildi!"))
