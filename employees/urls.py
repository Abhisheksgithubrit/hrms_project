from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('api/employees/', views.EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('api/employees/add', views.EmployeeListCreateView.as_view(), name='employee-add'),
    path('api/attendance/mark/', views.mark_attendance, name='mark-attendance'),
    path('api/attendance/<int:employee_id>/', views.get_attendance, name='get-attendance'),
    path('api/report/department/', views.department_report, name='department-report'),
    path('employees/', views.employee_list, name='employee-list'),
    path('employees/add/', views.employee_add, name='employee-add-page'),
    path('employees/<int:pk>/', views.employee_detail, name='employee-detail'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee-delete'),
    path('report/', views.department_chart, name='department-chart'),
    path('report/export/csv/', views.report_export_csv, name='report-export-csv'),
]