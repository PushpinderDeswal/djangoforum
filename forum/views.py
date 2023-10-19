from django.shortcuts import render, redirect, get_object_or_404
from django.http import (
    HttpResponseBadRequest,
    HttpResponseRedirect,
    Http404,
    HttpResponseForbidden,
)
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import AskQuestionForm, ResponseForm
from .models import Question, VoteQuestion, Response, VoteResponse
from django.urls import reverse


def home(request):
    user = request.user
    questions = Question().get_questions_list(user)
    return render(request, "forum/home.html", {"questions": questions})


def about(request):
    return render(request, "forum/about.html")


@login_required
def ask_question(request):
    if request.method == "POST":
        form = AskQuestionForm(request.POST)
        if form.is_valid():
            form.instance.questioner = request.user
            form.save()
            return redirect("forum:home")

    form = AskQuestionForm()

    return render(request, "forum/ask.html", {"form": form})


def question_detail(request, slug):
    question = Question().get_question_info(request.user, slug)

    if question is None:
        raise Http404()

    responses = Response().get_response_list_by_question(question.id, request.user)

    context = {
        "question": question,
        "responses": responses,
        "response_form": ResponseForm(),
    }
    return render(request, "forum/question_detail.html", context)


@login_required
def questions_asked_by_current_user(request):
    user = request.user
    questions = Question().get_questions_list(user).filter(questioner=user)

    return render(
        request, "forum/current_user_question_list.html", {"questions": questions}
    )


@login_required
@require_POST
def post_answer(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except:
        raise HttpResponseBadRequest("Bad request")

    form = ResponseForm(request.POST)

    if form.is_valid():
        form.instance.respondent = request.user
        form.instance.question = question

        form.save()

    return redirect("forum:question_detail", question.slug)


@login_required
@require_POST
def upvote_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    vote, created = VoteQuestion.objects.get_or_create(
        user=request.user, question=question, defaults={"vote": VoteQuestion.UPVOTE}
    )

    if not created and vote.vote == VoteQuestion.UPVOTE:
        vote.delete()
        question.upvotes -= 1
    elif not created and vote.vote == VoteQuestion.DOWNVOTE:
        vote.vote = VoteQuestion.UPVOTE
        vote.save()
        question.downvotes -= 1
        question.upvotes += 1
    else:
        question.upvotes += 1

    question.save()

    next = request.POST.get("next", "/")
    return HttpResponseRedirect(next)


@login_required
@require_POST
def downvote_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    vote, created = VoteQuestion.objects.get_or_create(
        user=request.user, question=question, defaults={"vote": VoteQuestion.DOWNVOTE}
    )

    if not created and vote.vote == VoteQuestion.DOWNVOTE:
        vote.delete()
        question.downvotes -= 1
    elif not created and vote.vote == VoteQuestion.UPVOTE:
        vote.vote = VoteQuestion.DOWNVOTE
        vote.save()
        question.downvotes += 1
        question.upvotes -= 1
    else:
        question.downvotes += 1

    question.save()

    next = request.POST.get("next", "/")
    return HttpResponseRedirect(next)


@login_required
@require_POST
def upvote_response(request, response_id):
    response = get_object_or_404(Response, id=response_id)

    vote, created = VoteResponse.objects.get_or_create(
        user=request.user, response=response, defaults={"vote": VoteResponse.UPVOTE}
    )

    if not created and vote.vote == VoteResponse.UPVOTE:
        vote.delete()
        response.upvotes -= 1
    elif not created and vote.vote == VoteResponse.DOWNVOTE:
        vote.vote = VoteResponse.UPVOTE
        vote.save()
        response.downvotes -= 1
        response.upvotes += 1
    else:
        response.upvotes += 1

    response.save()

    return redirect("forum:question_detail", response.question.slug)


@login_required
@require_POST
def downvote_response(request, response_id):
    response = get_object_or_404(Response, id=response_id)

    vote, created = VoteResponse.objects.get_or_create(
        user=request.user, response=response, defaults={"vote": VoteResponse.DOWNVOTE}
    )

    if not created and vote.vote == VoteResponse.DOWNVOTE:
        vote.delete()
        response.downvotes -= 1
    elif not created and vote.vote == VoteResponse.UPVOTE:
        vote.vote = VoteResponse.DOWNVOTE
        vote.save()
        response.upvotes -= 1
        response.downvotes += 1
    else:
        response.downvotes += 1

    response.save()

    return redirect("forum:question_detail", response.question.slug)


def list_question_by_tag(request, tag):
    questions = Question().get_questions_by_tag(tag, request.user)

    return render(
        request, "forum/questions_by_tag.html", {"questions": questions, "tag": tag}
    )


@login_required
def update_question(request, slug):
    next = request.GET.get("next", "/")
    question = get_object_or_404(Question, slug=slug)

    if question.questioner != request.user:
        return HttpResponseForbidden("You are not allowed to edit this question.")

    if request.method == "POST":
        form = AskQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect(next)
    else:
        form = AskQuestionForm(instance=question)

    return render(
        request,
        "forum/update_question.html",
        {"form": form, "question": question, "next": next},
    )


@login_required
def delete_question(request, slug):
    next = request.GET.get("next", "/")
    detail_url = reverse("forum:question_detail", kwargs={"slug": slug})
    question = get_object_or_404(Question, slug=slug)

    if question.questioner != request.user:
        return HttpResponseForbidden("You are not allowed to delete this question.")

    if request.method == "POST":
        question.delete()
        if next == detail_url:
            return HttpResponseRedirect("/")
        return HttpResponseRedirect(next)

    return render(
        request,
        "forum/delete_question_confirm.html",
        {"question": question, "next": next},
    )


@login_required
def update_response(request, response_id):
    response = get_object_or_404(Response, id=response_id)

    if request.user != response.respondent:
        return HttpResponseBadRequest("You are not authorized to edit this response.")

    if request.method == "POST":
        form = ResponseForm(request.POST, instance=response)
        if form.is_valid():
            form.save()
            return redirect("forum:question_detail", slug=response.question.slug)
    else:
        form = ResponseForm(instance=response)

    return render(
        request, "forum/update_response.html", {"form": form, "response": response}
    )


@login_required
def delete_response(request, response_id):
    response = get_object_or_404(Response, id=response_id)

    if request.user != response.respondent:
        return HttpResponseBadRequest("You are not authorized to delete this response.")

    if request.method == "POST":

        question_slug = response.question.slug
        response.delete()

        return redirect("forum:question_detail", slug=question_slug)

    return render(request, "forum/delete_response_confirm.html", {"response": response})
