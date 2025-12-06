import uuid
from django.db import models
from django.contrib.auth.models import User

class Questionnaire(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questionnaires')

    THEME_CHOICES = [
        ('professional', 'Professional (Blue)'),
        ('light', 'Light (Clean)'),
        ('dark', 'Dark (Night Mode)'),
    ]
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='professional')
    is_anonymous = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = [
        ('text', 'Text'),
        ('single', 'Single Choice'),
        ('multi', 'Multiple Choice'),
    ]
    
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='text')
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    choices = models.JSONField(default=list, blank=True, help_text="List of choices for single/multi types")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.questionnaire.title} - {self.text}"

class Invitation(models.Model):
    ROLES = [
        ('user', 'User'),
        ('observer', 'Observer'),
    ]

    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    role = models.CharField(max_length=10, choices=ROLES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    # For simplicity, we can link invitations to specific questionnaires via ManyToMany if needed,
    # or just assume observers see all results and users take assigned ones.
    # Requirement says "osservatore ... visualizzare ed esportare i risultati dei questionari a cui si è stati abilitati".
    # So we need a ManyToMany to Questionnaire.
    can_view = models.ManyToManyField(Questionnaire, related_name='observing_invitations', blank=True)
    can_answer = models.ManyToManyField(Questionnaire, related_name='answering_invitations', blank=True)

    def __str__(self):
        return f"{self.email} ({self.role})"

class Response(models.Model):
    invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    answer_text = models.TextField(blank=True, null=True) # For text answers
    answer_choice = models.JSONField(default=list, blank=True) # For single/multi choices (list of selected strings)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.question.id} by {self.invitation.email}"
