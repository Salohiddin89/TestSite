from django.urls import path
from . import views

# app_name = 'test_app'  # Namespace yo'q

urlpatterns = [
    path("", views.home_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("subject/<int:subject_id>/", views.subject_tests_view, name="subject_tests"),
    path("test/<int:test_id>/", views.take_test_view, name="take_test"),
    path("test/<int:test_id>/submit/", views.submit_test_view, name="submit_test"),
    path("test/<int:test_id>/retake/", views.retake_test_view, name="retake_test"),
    path("result/<int:attempt_id>/", views.test_result_view, name="test_result"),
    path("profile/", views.profile_view, name="profile"),
    path(
        "subject/<int:subject_id>/random/",
        views.take_random_test_view,
        name="take_random_test",
    ),
    path(
        "subject/<int:subject_id>/random/submit/",
        views.submit_random_test_view,
        name="submit_random_test",
    ),
    path(
        "random/result/<int:attempt_id>/",
        views.random_test_result_view,
        name="random_test_result",
    ),
]
