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
        token = self.request.query_params.get('token') or self.request.POST.get('token')
        if not token:
             return Questionnaire.objects.none()

        try:
             invitation = Invitation.objects.get(token=token)
             
             # Standard Rule: Users see assigned + active surveys
             assigned_active = invitation.can_answer.filter(is_active=True)
             
             # Creator Rule: Creators see EVERYTHING (Super Admin style)
             if invitation.role == 'creator':
                  return Questionnaire.objects.all()
             
             return assigned_active
        except Invitation.DoesNotExist:
             return Questionnaire.objects.none()

    def create(self, request, *args, **kwargs):
        from django.contrib.auth.models import User
        token = request.data.get('token')
        if not token:
            return APIResponse({'error': 'Token mancante'}, status=status.HTTP_400_BAD_REQUEST)
        
        invitation = get_object_or_404(Invitation, token=token)
        if invitation.role != 'creator':
             return APIResponse({'error': 'Permessi insufficienti'}, status=status.HTTP_403_FORBIDDEN)

        # Use a system user or the first user as "owner"
        system_user = User.objects.first()
        if not system_user:
            system_user = User.objects.create(username='system', email='system@example.com')

        # Prepare data
        data = request.data.copy()
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        # Save with owner and token
        survey = serializer.save(created_by=system_user, created_by_token=token)
        
        # Auto-assign permissions to the creator
        invitation.can_view.add(survey)
        invitation.can_answer.add(survey)
        invitation.save()
        
        headers = self.get_success_headers(serializer.data)
        return APIResponse(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
    def update(self, request, *args, **kwargs):
         # Check ownership via token
         token = request.data.get('token') or request.query_params.get('token')
         if not token:
              return APIResponse({'error': 'Token necessario per modifica'}, status=status.HTTP_403_FORBIDDEN)
         
         survey = self.get_object()
         survey = self.get_object()
         # Allow if creator OR if owner (fallback)
         # We already checked role via token in get_queryset or similar, but for update we need to be sure.
         # Actually get_queryset filters what they can see. If they can see it and have creator role, let them edit.
         invitation = Invitation.objects.get(token=token)
         if invitation.role != 'creator' and survey.created_by_token != token:
              return APIResponse({'error': 'Non sei autorizzato a modificare questo questionario'}, status=status.HTTP_403_FORBIDDEN)
              
         return super().update(request, *args, **kwargs)

    @decorators.action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        import csv
        import io
        from django.core.mail import send_mail
        from django.conf import settings

        survey = self.get_object()
        file = request.FILES.get('file')
        token = request.data.get('token')
        
        if not file:
            return APIResponse({'error': 'Nessun file CSV caricato'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify permissions
        # Allow if creator OR if owner
        invitation = Invitation.objects.get(token=token)
        if invitation.role != 'creator' and survey.created_by_token != token:
             return APIResponse({'error': 'Non autorizzato'}, status=status.HTTP_403_FORBIDDEN)

        decoded_file = file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string)
        
        emails_sent = 0
        for row in reader:
             if not row: continue
             email = row[0].strip()
             if '@' not in email: continue
             
             invitation, _ = Invitation.objects.get_or_create(email=email, defaults={'role': 'user'})
             invitation.can_answer.add(survey)
             
             # Use NEXT_PUBLIC_API_URL logic or hardcoded for now as per verified env
             link = f"http://localhost:3000/survey/{survey.id}?token={invitation.token}"
             subject = f"Invito al questionario: {survey.title}"
             message = f"Ciao! Sei stato invitato a compilare il questionario '{survey.title}'.\n\nClicca qui per iniziare subito:\n{link}\n\nGrazie!"
             
             try:
                 send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
                 emails_sent += 1
             except Exception as e:
                 print(f"Error sending to {email}: {e}")

        return APIResponse({'status': 'success', 'invited': emails_sent})

    @decorators.action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        survey = self.get_object()
        responses = Response.objects.filter(question__questionnaire=survey)
        serializer = ResponseSerializer(responses, many=True)
        return APIResponse(serializer.data)

class SubmitResponseView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        questionnaire = get_object_or_404(Questionnaire, pk=pk)
        token = request.data.get('token')
        answers = request.data.get('answers') # List of {question_id: 1, text: '...'}
        
        invitation = get_object_or_404(Invitation, token=token)
        
        saved_responses = []
        if answers:
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
        if not token:
             return APIResponse({'error': 'Token mancante'}, status=status.HTTP_400_BAD_REQUEST)
             
        invitation = get_object_or_404(Invitation, token=token)
        
        # Get all responses for this user
        responses = Response.objects.filter(invitation=invitation).select_related('question__questionnaire', 'question')
        
        # Group by questionnaire
        history_map = {}
        for r in responses:
            survey_id = r.question.questionnaire.id
            if survey_id not in history_map:
                history_map[survey_id] = {
                    'survey_title': r.question.questionnaire.title,
                    'survey_id': survey_id,
                    'last_submitted': r.submitted_at, # Rough approximation
                    'responses': []
                }
            
            # Update last submitted to be the latest
            if r.submitted_at > history_map[survey_id]['last_submitted']:
                history_map[survey_id]['last_submitted'] = r.submitted_at

            history_map[survey_id]['responses'].append({
                'question': r.question.text,
                'answer': r.answer_text if r.question.question_type == 'text' else r.answer_choice
            })
        
        data = list(history_map.values())
        return APIResponse(data)
