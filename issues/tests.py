import json
import os
from django.test import TestCase, Client
from issues.views import REPORTERS_FILE, ISSUES_FILE


class DevTrackAPITestCase(TestCase):

    def setUp(self):
        self.client = Client()
        # Clean up files before test run
        if os.path.exists(REPORTERS_FILE):
            os.remove(REPORTERS_FILE)
        if os.path.exists(ISSUES_FILE):
            os.remove(ISSUES_FILE)

    def tearDown(self):
        # Clean up files after test run
        if os.path.exists(REPORTERS_FILE):
            os.remove(REPORTERS_FILE)
        if os.path.exists(ISSUES_FILE):
            os.remove(ISSUES_FILE)

    def test_create_and_get_reporter(self):
        # 1. POST /api/reporters/ - Create reporter
        payload = {
            "id": 1,
            "name": "Alice Developer",
            "email": "alice@company.com",
            "team": "backend"
        }
        response = self.client.post(
            '/api/reporters/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Alice Developer")

        # 2. GET /api/reporters/ - List all reporters
        response = self.client.get('/api/reporters/')
        self.assertEqual(response.status_code, 200)
        reporters = response.json()
        self.assertEqual(len(reporters), 1)

        # 3. GET /api/reporters/?id=1 - Single reporter
        response = self.client.get('/api/reporters/?id=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "alice@company.com")

        # 4. GET /api/reporters/?id=999 - Non-existent reporter
        response = self.client.get('/api/reporters/?id=999')
        self.assertEqual(response.status_code, 404)

    def test_reporter_validation_failure(self):
        # Invalid email
        payload = {
            "id": 2,
            "name": "Bob",
            "email": "invalidemail.com",
            "team": "frontend"
        }
        response = self.client.post(
            '/api/reporters/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_create_and_filter_issues(self):
        # Create reporter first
        self.client.post(
            '/api/reporters/',
            data=json.dumps({"id": 1, "name": "Rahul", "email": "rahul@test.com", "team": "devops"}),
            content_type='application/json'
        )

        # 1. POST /api/issues/ - Create Critical Issue
        critical_payload = {
            "id": 1,
            "title": "Login button not working on mobile",
            "description": "Users on iOS 17 cannot tap the login button",
            "status": "open",
            "priority": "critical",
            "reporter_id": 1
        }
        response = self.client.post(
            '/api/issues/',
            data=json.dumps(critical_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        res_data = response.json()
        self.assertEqual(res_data["message"], "[URGENT] Login button not working on mobile — needs immediate attention")

        # 2. POST /api/issues/ - Create Low Priority Issue
        low_payload = {
            "id": 2,
            "title": "Fix typo in footer",
            "description": "Copyright year needs update",
            "status": "resolved",
            "priority": "low",
            "reporter_id": 1
        }
        response = self.client.post(
            '/api/issues/',
            data=json.dumps(low_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        res_data = response.json()
        self.assertEqual(res_data["message"], "Fix typo in footer — low priority, handle when free")

        # 3. GET /api/issues/ - Retrieve all issues
        response = self.client.get('/api/issues/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

        # 4. GET /api/issues/?id=1 - Single issue lookup
        response = self.client.get('/api/issues/?id=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Login button not working on mobile")

        # 5. GET /api/issues/?status=open - Filter issues by status
        response = self.client.get('/api/issues/?status=open')
        self.assertEqual(response.status_code, 200)
        open_issues = response.json()
        self.assertEqual(len(open_issues), 1)
        self.assertEqual(open_issues[0]["id"], 1)

    def test_issue_validation_failures(self):
        # Create reporter 1
        self.client.post(
            '/api/reporters/',
            data=json.dumps({"id": 1, "name": "Rahul", "email": "rahul@test.com", "team": "devops"}),
            content_type='application/json'
        )

        # Empty title
        payload = {
            "id": 10,
            "title": "",
            "description": "Empty title test",
            "status": "open",
            "priority": "high",
            "reporter_id": 1
        }
        response = self.client.post(
            '/api/issues/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Title cannot be empty")

        # Non-existent reporter_id
        payload_invalid_reporter = {
            "id": 11,
            "title": "Valid title",
            "description": "Valid desc",
            "status": "open",
            "priority": "high",
            "reporter_id": 999
        }
        response = self.client.post(
            '/api/issues/',
            data=json.dumps(payload_invalid_reporter),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["error"])
