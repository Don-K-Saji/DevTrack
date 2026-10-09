# DevTrack - Backend Engineering Issue Tracker API

DevTrack is a lightweight, high-performance Django REST backend API built for tracking software engineering issues, bugs, and priorities. 

This project was developed as part of the **AI-First Backend Engineering** program at **AirTribe**.

---

## 📌 Features & Core Architecture

1. **Pure Object-Oriented Domain Modeling (`issues/models.py`)**:
   - **`BaseEntity`**: Abstract Base Class enforcing `validate()` and `to_dict()` contracts.
   - **`Reporter`**: Models engineers filing bugs with name and email format validation.
   - **`Issue`**: Base model for bug reports with status (`open`, `in_progress`, `resolved`, `closed`) and priority (`low`, `medium`, `high`, `critical`) validation.
   - **Polymorphism via Priority Subclasses**: `CriticalIssue` and `LowPriorityIssue` override the `describe()` method to dynamically format priority messages (`[URGENT] ...` for critical issues, `... — low priority, handle when free` for low priority issues).

2. **JSON File-Based Persistence (`reporters.json` & `issues.json`)**:
   - Stores data persistently without external DB drivers, maintaining full referential integrity (`reporter_id` validation).

3. **RESTful Django API Views (`issues/views.py`)**:
   - Exposes clean JSON endpoints for creation, listing, single lookup, and query filtering.

---

## 🛠️ How to Set Up & Run the Project

### 1. Clone & Navigate to Project
```bash
git clone <your-github-repo-url>
cd DevTrack
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Development Server
```bash
python manage.py runserver
```
The server will start at `http://127.0.0.1:8000/`.

### 4. Run Automated Test Suite
```bash
python manage.py test
```

---

## 🔌 API Endpoints Documentation

### 1. Reporter Endpoints

#### 🟢 `POST /api/reporters/` — Create a Reporter
- **Request Body**:
  ```json
  {
    "id": 1,
    "name": "Rahul Sharma",
    "email": "rahul@company.com",
    "team": "backend"
  }
  ```
- **Response (`201 Created`)**:
  ```json
  {
    "id": 1,
    "name": "Rahul Sharma",
    "email": "rahul@company.com",
    "team": "backend"
  }
  ```

#### 🔵 `GET /api/reporters/` — Get All Reporters
- **Response (`200 OK`)**: List of all reporter objects.

#### 🔵 `GET /api/reporters/?id=1` — Get Reporter by ID
- **Response (`200 OK`)**: Single reporter object matching ID `1`.
- **Response (`404 Not Found`)**: `{"error": "Reporter not found"}`

---

### 2. Issue Endpoints

#### 🟢 `POST /api/issues/` — Create an Issue
- **Request Body (Critical Priority)**:
  ```json
  {
    "id": 1,
    "title": "Login button not working on mobile",
    "description": "Users on iOS 17 cannot tap the login button",
    "status": "open",
    "priority": "critical",
    "reporter_id": 1
  }
  ```
- **Response (`201 Created`)**:
  ```json
  {
    "id": 1,
    "title": "Login button not working on mobile",
    "description": "Users on iOS 17 cannot tap the login button",
    "status": "open",
    "priority": "critical",
    "reporter_id": 1,
    "created_at": "2026-10-09 21:30:40.123456",
    "message": "[URGENT] Login button not working on mobile — needs immediate attention"
  }
  ```

- **Error Response (`400 Bad Request` - Empty Title)**:
  ```json
  {
    "error": "Title cannot be empty"
  }
  ```

- **Error Response (`404 Not Found` - Invalid Reporter ID)**:
  ```json
  {
    "error": "Reporter with ID 999 not found"
  }
  ```

#### 🔵 `GET /api/issues/` — Get All Issues
- **Response (`200 OK`)**: List of all issues.

#### 🔵 `GET /api/issues/?id=1` — Get Issue by ID
- **Response (`200 OK`)**: Single issue object matching ID `1`.

#### 🔵 `GET /api/issues/?status=open` — Filter Issues by Status
- **Response (`200 OK`)**: Array of issues where `status` equals `"open"`.

---

## 🎯 Key Design Decision & Rationale

**Design Decision**: Using **Polymorphic Class Factory & Overridden Methods** for Priority Description Handling.

**Rationale**:
Rather than cluttering `views.py` with multi-branch `if-else` string construction logic, we instantiated specialized subclasses (`CriticalIssue` and `LowPriorityIssue`) inheriting from `Issue`. Each subclass overrides its own `describe()` method. 

This decision:
1. **Adheres to the Open-Closed Principle (OCP)**: New priority types (e.g., `BlockerIssue`) can be added by creating a new subclass in `models.py` without modifying core view formatting logic.
2. **Decouples Domain Logic from HTTP Handlers**: Keeps `views.py` clean, readable, and focused solely on request handling and JSON persistence.

---

## 📸 Postman Screenshots & Test Results

### 1. Reporter Creation Success (`POST /api/reporters/` - 201 Created)
![Reporter Creation Successful](screenshots/Reporter%20Creation%20Successful.png)

### 2. Issue Creation Success (`POST /api/issues/` - 201 Created)
![Issue Creation Successful](screenshots/Issue%20Creation%20Successful.png)

### 3. Issue Validation Failure (`POST /api/issues/` - 400 Bad Request)
![Issue Creation Failure](screenshots/Issue%20Creation%20Failure.png)

