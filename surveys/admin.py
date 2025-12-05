from django.contrib import admin
from .models import Questionnaire, Question, Invitation, Response

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('title', 'created_by', 'created_at')

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'token', 'used')
    readonly_fields = ('token',)

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('invitation', 'question', 'submitted_at')
    list_filter = ('invitation__email', 'question__questionnaire')
