# HRMS Project

A **Human Resource Management System** built with **Django** and **Django REST Framework**. It supports employee management, attendance tracking, department-wise reporting, and a template-based UI with REST APIs for integration.

---

## Tech Stack

| Layer        | Technology                          |
|-------------|--------------------------------------|
| Language    | Python 3.x                           |
| Web Framework | Django                             |
| API         | Django REST Framework (DRF)          |
| Database    | SQLite (default; easily swappable)   |
| Frontend    | Bootstrap 5, Chart.js, Django Templates |
| Standards   | PEP 8, REST conventions, docstrings   |

---

## Architecture

### 1. Django MVT (Model–View–Template)

- **Models** (`employees/models.py`): Define data structure and business entities (Employee, Attendance). Use Django ORM; no raw SQL.
- **Views** (`employees/views.py`): Handle HTTP request/response. Mix of:
  - **Template views**: Render HTML (home, employee list/detail, reports, mark attendance form).
  - **DRF API views**: Return JSON (list/create employees, mark/get attendance, department report, CSV export).
- **Templates** (`employees/templates/employees/`): HTML with Django template language. Base layout in `base.html`; others extend it.

### 2. Project vs App Structure

- **Project** (`hrms/`): Configuration only — `settings.py`, root `urls.py`, WSGI. No business logic.
- **App** (`employees/`): All business logic — models, views, serializers, URLs, templates, admin. Keeps the project clean and the app reusable.

### 3. REST API Design

- **Resource-based URLs**: `/api/employees/`, `/api/attendance/<id>/`, `/api/report/department/`.
- **HTTP methods**: GET (list/retrieve), POST (create). Proper status codes (200, 201, 400, 404).
- **Query parameters** for filtering: `department`, `designation`, `search`, `date_from`, `date_to` on employees and attendance.
- **Content negotiation**: Same report endpoint returns JSON by default; CSV via `?format=csv` or dedicated `/report/export/csv/`.

### 4. Separation of Concerns

- **Serializers** (`serializers.py`): Validate and serialize request/response data; validation (e.g. date_of_joining not future, out_time > in_time) lives here.
- **Views**: Orchestrate flow (get queryset, call serializer, return response). Thin where possible.
- **Models**: Single source of truth; `unique_together` and `related_name` used for data integrity.

### 5. Security & Best Practices

- **CSRF**: Enabled for all forms (template and API if session-based).
- **Admin**: Employee and Attendance registered with list_display, search, filters.
- **Input validation**: In serializers and in form POST (e.g. mark attendance view).
- **Docstrings**: On models, views, serializers, and helper functions for maintainability.

---

## Directory Structure

```
hrms_project/
├── hrms/                    # Project package (config only)
│   ├── __init__.py
│   ├── settings.py          # Django settings, INSTALLED_APPS, DB, middleware
│   ├── urls.py              # Root URLconf; includes employees.urls
│   └── wsgi.py
├── employees/               # Main application
│   ├── migrations/
│   ├── templates/
│   │   └── employees/
│   │       ├── base.html           # Shared layout, nav, styles
│   │       ├── home.html
│   │       ├── employee_list.html
│   │       ├── employee_detail.html  # Includes "Mark Attendance" form
│   │       ├── employee_add.html
│   │       ├── employee_confirm_delete.html
│   │       └── department_chart.html # Reports + Chart.js
│   ├── __init__.py
│   ├── admin.py             # EmployeeAdmin, AttendanceAdmin
│   ├── apps.py
│   ├── models.py            # Employee, Attendance
│   ├── serializers.py       # EmployeeSerializer, AttendanceSerializer
│   ├── urls.py              # App URL patterns (api + template routes)
│   └── views.py             # API views + template views + helpers
├── manage.py
├── db.sqlite3               # SQLite database (created after migrate)
├── requirements.txt
└── README.md
```

---

## Design Decisions (Interview Points)

| Decision | Reason |
|----------|--------|
| Single `employees` app | Domain is small; one app keeps URLs and logic in one place. Easy to add more apps (e.g. `leave`, `payroll`) later. |
| Both templates and API | Templates for browser users; API for mobile/frontend or integrations. Same models and serializers. |
| SQLite | No extra setup; good for demo and small teams. Django ORM allows switching to PostgreSQL/MySQL by changing `settings.py`. |
| DRF for API | Standard way in Django ecosystem; serializers, status codes, and browsable API out of the box. |
| Normalized department counts | Report uses a helper that strips whitespace and aggregates in Python so "IT" and "IT " count together. |
| Mark attendance on detail page | User stays in context (same employee); form defaults to today so "Attendance Today" on home updates. |

---

## Installation

1. **Clone or navigate to the project:**
   ```bash
   cd hrms_project
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **(Optional) Create superuser for admin:**
   ```bash
   python manage.py createsuperuser
   ```

---

## How to Run

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in the browser.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home (landing) |
| GET | `/api/employees/` | List employees. Query params: `department`, `designation`, `search`, `date_from`, `date_to` |
| POST | `/api/employees/add` | Create employee (JSON body) |
| POST | `/api/attendance/mark/` | Mark attendance (JSON: `employee`, `date`, `in_time`, `out_time`) |
| GET | `/api/attendance/<employee_id>/` | Get attendance for employee. Params: `date_from`, `date_to` |
| GET | `/api/report/department/` | Department-wise employee count (JSON) |
| GET | `/report/export/csv/` | Department report as CSV download |
| GET | `/admin/` | Django Admin (superuser required) |

---

## Template Pages (UI)

| URL | Purpose |
|-----|---------|
| `/` | Home, quick overview stats, links to Employees & Reports |
| `/employees/` | Employee list with filters (department, designation, search) |
| `/employees/add/` | Add employee form |
| `/employees/<id>/` | Employee detail + **Mark Attendance** form + attendance table |
| `/employees/<id>/delete/` | Confirm delete employee |
| `/report/` | Reports: bar chart, doughnut chart, table, Export CSV / JSON |

---

## Models

**Employee**  
`id`, `name`, `email` (unique), `address`, `designation`, `department`, `date_of_joining`

**Attendance**  
`id`, `employee` (FK → Employee, CASCADE), `date`, `in_time`, `out_time` (nullable)  
`Meta`: `unique_together = ['employee', 'date']` (one record per employee per day)

---

## Features

- Employee CRUD (list, add, view, delete) via UI and API
- Attendance: mark from employee detail page (date, in/out time); view per employee; optional API
- Department report: counts, bar/doughnut charts (Chart.js), table, CSV export
- Filters: department, designation, search, date range on employees and attendance
- Admin: Employee and Attendance with list_display, search, filters
- Input validation and sensible HTTP status codes; docstrings throughout

---

