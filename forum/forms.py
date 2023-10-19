from django import forms
from .models import Question, Response


class AskQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["title", "description", "tags"]


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ["content"]
