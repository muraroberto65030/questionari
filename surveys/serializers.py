from rest_framework import serializers
from .models import Questionnaire, Question, Invitation, Response

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'is_required', 'choices', 'order']

class QuestionnaireSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    
    class Meta:
        model = Questionnaire
        fields = ['id', 'title', 'description', 'questions', 'created_at', 'theme']
        
    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        questionnaire = Questionnaire.objects.create(**validated_data)
        for q_data in questions_data:
            Question.objects.create(questionnaire=questionnaire, **q_data)
        return questionnaire

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['id', 'email', 'role', 'token', 'used']

class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ['question', 'answer_text', 'answer_choice']
