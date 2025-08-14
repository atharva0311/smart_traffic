from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('live/', views.traffic_dashboard, name='live'),  # Main dashboard page
    path('receive_frame/', views.receive_frame, name='receive_frame'),  # POST endpoint for frame processing
    path('about/',views.about,name='about'),
    path('',views.home,name='dashboard')
]
