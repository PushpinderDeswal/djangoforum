from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from random import randint
from django.db.models import Count, Case, When, IntegerField


class Tag(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class Question(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=600)
    questioner = models.ForeignKey(User, on_delete=models.CASCADE)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, max_length=400, blank=True)
    tags = models.ManyToManyField(Tag, related_name="questions")

    def save(self, *args, **kwars) -> None:
        if self.pk is None:
            self.slug = slugify(self.title) + "-" + str(randint(11111111, 99999999))
        super(Question, self).save(*args, **kwars)

    def __str__(self) -> str:
        return self.title

    def get_questions_list(self, user):
        questions = (
            Question.objects.select_related("questioner")
            .only(
                "id",
                "title",
                "description",
                "upvotes",
                "downvotes",
                "slug",
                "questioner__username",
                "created_at",
                "updated_at",
            )
            .prefetch_related("tags")
            .order_by("-created_at")
        )

        if not user.is_authenticated:
            return questions

        return questions.annotate(
            user_upvoted=Count(
                Case(
                    When(votes__user=user, votes__vote=VoteQuestion.UPVOTE, then=1),
                    output_field=IntegerField(),
                )
            ),
            user_downvoted=Count(
                Case(
                    When(votes__user=user, votes__vote=VoteQuestion.DOWNVOTE, then=1),
                    output_field=IntegerField(),
                )
            ),
        )

    def get_questions_by_tag(self, tag, user):
        questions = (
            Question.objects.select_related("questioner")
            .only(
                "id",
                "title",
                "description",
                "upvotes",
                "downvotes",
                "slug",
                "questioner__username",
                "created_at",
                "updated_at",
            )
            .prefetch_related("tags")
            .filter(tags__name=tag)
            .order_by("-created_at")
        )

        if not user.is_authenticated:
            return questions

        return questions.annotate(
            user_upvoted=Count(
                Case(
                    When(votes__user=user, votes__vote=VoteQuestion.UPVOTE, then=1),
                    output_field=IntegerField(),
                )
            ),
            user_downvoted=Count(
                Case(
                    When(votes__user=user, votes__vote=VoteQuestion.DOWNVOTE, then=1),
                    output_field=IntegerField(),
                )
            ),
        )

    def get_question_info(self, user, question_slug):
        try:
            question = (
                Question.objects.select_related("questioner")
                .prefetch_related("tags")
                .only(
                    "id",
                    "title",
                    "description",
                    "upvotes",
                    "downvotes",
                    "questioner__username",
                    "created_at",
                    "updated_at",
                )
            )

            if not user.is_authenticated:
                return question.get(slug=question_slug)

            return question.annotate(
                user_upvoted=Count(
                    Case(
                        When(
                            votes__user=user,
                            votes__vote=VoteQuestion.UPVOTE,
                            then=1,
                        ),
                        output_field=IntegerField(),
                    )
                ),
                user_downvoted=Count(
                    Case(
                        When(
                            votes__user=user,
                            votes__vote=VoteQuestion.DOWNVOTE,
                            then=1,
                        ),
                        output_field=IntegerField(),
                    )
                ),
            ).get(slug=question_slug)
        except self.DoesNotExist:
            return None


class Response(models.Model):
    content = models.TextField(max_length=600)
    respondent = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_response_list_by_question(self, question_id, user):
        responses = (
            Response.objects.select_related("respondent")
            .only(
                "id",
                "content",
                "upvotes",
                "downvotes",
                "respondent__username",
                "created_at",
                "updated_at",
            )
            .filter(question__id=question_id)
        )
        if not user.is_authenticated:
            return responses

        return responses.annotate(
            user_upvoted=Count(
                Case(
                    When(votes__user=user, votes__vote=VoteResponse.UPVOTE, then=1),
                    output_field=IntegerField(),
                )
            ),
            user_downvoted=Count(
                Case(
                    When(votes__user=user, votes__vote=VoteResponse.DOWNVOTE, then=1),
                    output_field=IntegerField(),
                )
            ),
        )

    def __str__(self) -> str:
        return self.content


class VoteQuestion(models.Model):
    UPVOTE = 1
    DOWNVOTE = -1
    VOTE_CHOICES = ((UPVOTE, "Upvote"), (DOWNVOTE, "Downvote"))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="votes"
    )
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)

    class Meta:
        unique_together = ("user", "question")


class VoteResponse(models.Model):
    UPVOTE = 1
    DOWNVOTE = -1
    VOTE_CHOICES = ((UPVOTE, "Upvote"), (DOWNVOTE, "Downvote"))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.ForeignKey(
        Response, on_delete=models.CASCADE, related_name="votes"
    )
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)

    class Meta:
        unique_together = ("user", "response")
