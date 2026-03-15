from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from django.db.models import Count, Q
from django.views.generic import TemplateView
from .models import Employee, Attendance
from .serializers import EmployeeSerializer, AttendanceSerializer

import json


def _get_department_counts():
    """
    Return a dict of department -> employee count with normalized department names.
    Use this for both API and template report so counts match.
    """
    data = {}
    for dept in Employee.objects.values_list('department', flat=True):
        dept = (dept or "").strip()
        if not dept:
            continue
        data[dept] = data.get(dept, 0) + 1
    return data


class HomeView(TemplateView):
    """
    View for the home page.
    """
    template_name = 'employees/home.html'

    def get_context_data(self, **kwargs):
        """
        Return context for the home page.
        """
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()

        context['message'] = 'Welcome to HRMS System'
        context['stats'] = {
            'employees_total': Employee.objects.count(),
            'departments_total': len(
                {
                    (dept or "").strip()
                    for dept in Employee.objects.values_list('department', flat=True)
                    if (dept or "").strip()
                }
            ),
            'attendance_today': Attendance.objects.filter(date=today).count(),
        }
        return context


def home(request):
    """
    Simple view that returns welcome message.
    """
    return HttpResponse("Welcome to HRMS System")


class EmployeeListCreateView(ListCreateAPIView):
    """
    API view for listing and creating employees.

    Supports filtering via the following query parameters:
    - department: filter by department name (case-insensitive)
    - designation: filter by designation (case-insensitive)
    - search: partial match on name or email
    - date_from: join date greater than or equal to this date (YYYY-MM-DD)
    - date_to: join date less than or equal to this date (YYYY-MM-DD)
    """
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        """
        Return employees filtered according to query parameters.
        """
        queryset = Employee.objects.all()
        params = self.request.query_params

        department = params.get('department')
        designation = params.get('designation')
        search = params.get('search')
        date_from = params.get('date_from')
        date_to = params.get('date_to')

        if department:
            queryset = queryset.filter(department__iexact=department)
        if designation:
            queryset = queryset.filter(designation__iexact=designation)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(email__icontains=search)
            )
        if date_from:
            queryset = queryset.filter(date_of_joining__gte=date_from)
        if date_to:
            queryset = queryset.filter(date_of_joining__lte=date_to)

        return queryset


@api_view(['POST'])
def mark_attendance(request):
    """
    API view to mark attendance for an employee.
    """
    serializer = AttendanceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_attendance(request, employee_id):
    """
    API view to get attendance records for a specific employee.

    Optional query parameters:
    - date_from: start date (inclusive)
    - date_to: end date (inclusive)
    """
    employee = get_object_or_404(Employee, id=employee_id)
    attendances = Attendance.objects.filter(employee=employee)

    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')

    if date_from:
        attendances = attendances.filter(date__gte=date_from)
    if date_to:
        attendances = attendances.filter(date__lte=date_to)
    serializer = AttendanceSerializer(attendances, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def department_report(request):
    """
    API view to get the count of employees in each department.
    """
    data = _get_department_counts()

    output_format = request.query_params.get('format')
    if output_format == 'csv':
        lines = ["department,count"]
        for department, count in data.items():
            safe_department = (department or "").replace('"', '""')
            lines.append(f'"{safe_department}",{count}')
        csv_content = "\n".join(lines) + "\n"
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="department_report.csv"'
        return response

    return Response(data)


def employee_list(request):
    """
    View to display list of employees in a template with filters.
    """
    department = request.GET.get('department') or ''
    designation = request.GET.get('designation') or ''
    search = request.GET.get('search') or ''

    employees = Employee.objects.all()

    if department:
        employees = employees.filter(department__iexact=department)
    if designation:
        employees = employees.filter(designation__iexact=designation)
    if search:
        employees = employees.filter(
            Q(name__icontains=search) | Q(email__icontains=search)
        )

    context = {
        'employees': employees,
        'department': department,
        'designation': designation,
        'search': search,
    }
    return render(request, 'employees/employee_list.html', context)


def employee_detail(request, pk):
    """
    View to display details of a specific employee including attendance.
    Handles POST to mark attendance for this employee (date, in_time, out_time).
    """
    employee = get_object_or_404(Employee, pk=pk)
    attendances = Attendance.objects.filter(employee=employee).order_by('-date')

    if request.method == 'POST' and request.POST.get('mark_attendance') == '1':
        date_str = request.POST.get('date')
        in_time_str = request.POST.get('in_time')
        out_time_str = request.POST.get('out_time') or None

        errors = []
        if not date_str:
            errors.append('Date is required.')
        if not in_time_str:
            errors.append('In time is required.')

        if not errors:
            from datetime import datetime
            try:
                date_val = datetime.strptime(date_str, '%Y-%m-%d').date()
                in_time_val = datetime.strptime(in_time_str, '%H:%M').time()
                out_time_val = None
                if out_time_str:
                    out_time_val = datetime.strptime(out_time_str, '%H:%M').time()
                    if out_time_val <= in_time_val:
                        errors.append('Out time must be later than in time.')
            except ValueError:
                errors.append('Invalid date or time format.')

        if errors:
            messages.error(request, ' '.join(errors))
        else:
            existing = Attendance.objects.filter(employee=employee, date=date_val).first()
            if existing:
                if out_time_val and not existing.out_time:
                    existing.out_time = out_time_val
                    existing.save()
                    messages.success(request, f'Out time updated for {date_val}.')
                else:
                    messages.warning(request, f'Attendance already marked for {date_val}.')
            else:
                Attendance.objects.create(
                    employee=employee,
                    date=date_val,
                    in_time=in_time_val,
                    out_time=out_time_val,
                )
                messages.success(request, f'Attendance marked for {date_val}.')

        return redirect('employees:employee-detail', pk=pk)

    today = timezone.localdate().isoformat()
    context = {
        'employee': employee,
        'attendances': attendances,
        'today': today,
    }
    return render(request, 'employees/employee_detail.html', context)


def employee_add(request):
    """
    Render and handle the Add Employee form.

    On GET: show the form.
    On POST: validate input and create an employee record.
    """
    if request.method == 'POST':
        serializer = EmployeeSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return redirect('employees:employee-list')
        return render(
            request,
            'employees/employee_add.html',
            {'errors': serializer.errors, 'data': request.POST},
        )

    return render(request, 'employees/employee_add.html', {'data': {}})


def employee_delete(request, pk):
    """
    Delete an employee. GET shows confirmation page; POST performs delete.
    """
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employees:employee-list')
    return render(
        request,
        'employees/employee_confirm_delete.html',
        {'employee': employee},
    )


def report_export_csv(request):
    """
    Serve department report as CSV download. Dedicated URL so Export CSV never 404s.
    """
    data = _get_department_counts()
    lines = ["department,count"]
    for department, count in data.items():
        safe_department = (department or "").replace('"', '""')
        lines.append(f'"{safe_department}",{count}')
    csv_content = "\n".join(lines) + "\n"
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="department_report.csv"'
    return response


def department_chart(request):
    """
    View to display department report with Chart.js.
    Uses same normalized department counts as the API.
    """
    data = _get_department_counts()
    return render(request, 'employees/department_chart.html', {'data': json.dumps(data)})
