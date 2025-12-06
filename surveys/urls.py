from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SurveyViewSet, VerifyTokenView, SubmitResponseView, UserHistoryView

router = DefaultRouter()
router.register(r'surveys', SurveyViewSet)

urlpatterns = [
    path('surveys/history/', UserHistoryView.as_view(), name='user_history'),
    path('auth/verify/', VerifyTokenView.as_view(), name='verify_token'),
    path('surveys/<int:pk>/submit/', SubmitResponseView.as_view(), name='submit_survey'),
    path('', include(router.urls)),
]
