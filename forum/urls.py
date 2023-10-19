from django.urls import path
from . import views

app_name = "forum"
urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("question/ask/", views.ask_question, name="ask_question"),
    path("question/<str:slug>/", views.question_detail, name="question_detail"),
    path("answer/question/<int:question_id>/", views.post_answer, name="post_answer"),
    path(
        "question/<int:question_id>/upvote/",
        views.upvote_question,
        name="upvote_question",
    ),
    path(
        "question/<int:question_id>/downvote/",
        views.downvote_question,
        name="downvote_question",
    ),
    path(
        "response/<int:response_id>/upvote/",
        views.upvote_response,
        name="upvote_response",
    ),
    path(
        "response/<int:response_id>/downvote/",
        views.downvote_response,
        name="downvote_response",
    ),
    path(
        "tags/<str:tag>/questions/",
        views.list_question_by_tag,
        name="questions_by_tag",
    ),
    path(
        "question/<str:slug>/update/",
        views.update_question,
        name="update_question",
    ),
    path(
        "question/<str:slug>/delete/",
        views.delete_question,
        name="delete_question",
    ),
    path(
        "response/update/<int:response_id>/",
        views.update_response,
        name="update_response",
    ),
    path(
        "response/delete/<int:response_id>/",
        views.delete_response,
        name="delete_response",
    ),
    path(
        "questions/asked_by/me/",
        views.questions_asked_by_current_user,
        name="current_user_questions",
    ),
]
