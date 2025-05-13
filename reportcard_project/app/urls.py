from django.urls import path
from . import views

urlpatterns = [
    path("api/students", views.add_student_api, name="api_add_student"),
    path("api/students/<int:student_id>/reportcard", views.get_report_card_api, name="api_get_report_card"),
    path('api/reportcard/generate', views.generate_reportcard_link, name='generate_reportcard_link'),
    
    # UI pages
    path('', views.student_list_view, name='students_list'),
    path('add_student/', views.add_student_view, name='add_student'),
    path('view/<int:student_id>/', views.view_report, name='view_report'),
    path('edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete/<int:student_id>/', views.delete_student, name='delete_student'),
    path('students/<int:student_id>/preview/', views.student_report_preview, name='student-preview'),
    path('student/<int:student_id>/download/', views.download_report_card_pdf, name='download_pdf'),

]
