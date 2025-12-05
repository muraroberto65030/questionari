from rest_framework import viewsets, views, status, permissions, decorators
from rest_framework.response import Response as APIResponse
from django.shortcuts import get_object_or_404
from .models import Questionnaire, Invitation, Response, Question
from .serializers import QuestionnaireSerializer, InvitationSerializer, ResponseSerializer

class VerifyTokenView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return APIResponse({'error': 'Token mancante'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            invitation = Invitation.objects.get(token=token)
            # Check if user is observer or simple user
            # Return token and role
            return APIResponse({
                'valid': True, 
                'role': invitation.role, 
                'email': invitation.email,
                'used': invitation.used
            })
        except Invitation.DoesNotExist:
            return APIResponse({'error': 'Token non valido'}, status=status.HTTP_404_NOT_FOUND)

class SurveyViewSet(viewsets.ModelViewSet):
    """
    CRUD for surveys. 
    """
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        #Ideally filter by invitation permission
        return super().get_queryset()

    @decorators.action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        survey = self.get_object()
        responses = Response.objects.filter(question__questionnaire=survey).select_related('invitation', 'question')
        
        data = []
        for r in responses:
            data.append({
                'id': r.id,
                'email': r.invitation.email,
                'question': r.question.text,
                'answer': r.answer_text if r.question.question_type == 'text' else r.answer_choice,
                'submitted_at': r.submitted_at
            })
        return APIResponse(data)

class SubmitResponseView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        questionnaire = get_object_or_404(Questionnaire, pk=pk)
        token = request.data.get('token')
        answers = request.data.get('answers') # List of {question_id: 1, text: '...'}
        print(f"DEBUG: Submit attempt. Token: {token}, Answers: {len(answers) if answers else 'None'}")
        
        invitation = get_object_or_404(Invitation, token=token)
        
        # Determine if already used or allow multiple submissions? 
        # Requirement: "visualizzare le risposte date" implies storing them.
        
        saved_responses = []
        for ans in answers:
            question_id = ans.get('question_id')
            q = get_object_or_404(Question, pk=question_id, questionnaire=questionnaire)
            
            # Create response
            resp = Response.objects.create(
                invitation=invitation,
                question=q,
                answer_text=ans.get('answer_text', ''),
                answer_choice=ans.get('answer_choice', [])
            )
            saved_responses.append(resp.id)
            
        invitation.used = True
        invitation.save()
        
        return APIResponse({'status': 'submitted', 'count': len(saved_responses)})

class UserHistoryView(views.APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        token = request.query_params.get('token')
        invitation = get_object_or_404(Invitation, token=token)
        
        # Get all responses for this user
        responses = Response.objects.filter(invitation=invitation).select_related('question__questionnaire')
        
        data = []
        # Group by questionnaire?
        # For MVP, just return flat list or grouped
        return APIResponse({'history': 'todo'}) # Placeholder
