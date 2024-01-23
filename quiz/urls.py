from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    # Main paths
    path('', views.redirect_to_index, name='index'),
    path('logged_in_index/', views.logged_in_index, name='logged_in_index'),
    path('logged_out_index/', views.logged_out_index, name='logged_out_index'),
    path("setup/", views.setup, name="setup"),
    path("profile/", views.profile, name="profile"),
    path("account/", views.account, name="account"),
    path("logout/", views.logout_view, name="logout"),
    path("join_quiz/<int:quiz_id>/", views.join_quiz, name="join_quiz"),
    path("quiz_redirection/<int:quiz_id>/", views.quiz_redirection, name="quiz_redirection"),
    path("waiting/", views.waiting, name="waiting"),
    path("waiting/<int:quiz_id>/", views.waiting, name="waiting"),
    path("question/", views.question, name="question"),
    path("question/<int:quiz_id>/", views.question, name="question"),
    path("results/<int:quiz_id>/", views.results, name="results"),
    path("results/<int:quiz_id>/<int:team_id>", views.results, name="results"),
    path("results_detailed/<int:quiz_id>/", views.results_detailed, name="results_detailed"),
    path("quiz_host/", views.quiz_host, name="quiz_host"),
    path("quiz_host/<int:quiz_id>/", views.quiz_host, name="quiz_host"),
    path("create/", views.create, name="create"),
    path("create/<str:name>/", views.create, name="create"),
    path("create/<str:name>/<int:number>/", views.create, name="create"),
    path("browse/", views.browse, name="browse"),
    path("browse/<str:filter>/", views.browse, name="browse"),
    path("browse/<str:filter>/<str:category>", views.browse, name="browse"),
    path("my_quizzes/", views.my_quizzes, name="my_quizzes"),
    path("quiz_management/", views.quiz_management, name="quiz_management"),
    path("quiz_management/<int:quiz_id>/", views.quiz_management, name="quiz_management"),
    path("quiz_registration/", views.quiz_registration, name="quiz_registration"),
    path("quiz_registration/<int:quiz_id>/", views.quiz_registration, name="quiz_registration"),

    # APIs
    path("voting", views.voting, name="voting"),
    path("forward_waiting", views.forward_waiting, name="forward_waiting"),
    path("next_step_one", views.next_step_one, name="next_step_one"),
    path("submit_open_answer", views.submit_open_answer, name="submit_open_answer"),
    path("see_multichoice_answers", views.see_multichoice_answers, name="see_multichoice_answers"),
    path("submit_multi_answer", views.submit_multi_answer, name="submit_multi_answer"),
    path("forward_question", views.forward_question, name="forward_question"),
    path("question_started", views.question_started, name="question_started"),
    path("update_host_view", views.update_host_view, name="update_host_view"),
    path("change_quiz_parameter", views.change_quiz_parameter, name="change_quiz_parameter"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)