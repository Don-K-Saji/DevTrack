import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Reporter, Issue, CriticalIssue, LowPriorityIssue

REPORTERS_FILE = 'reporters.json'
ISSUES_FILE = 'issues.json'


def read_json_file(filename):
    """Utility function to read JSON data from file safely."""
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, OSError):
        return []


def write_json_file(filename, data):
    """Utility function to write JSON data to file safely."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


@csrf_exempt
def reporter_views(request):
    """
    Handles Reporter API endpoints:
    - POST /api/reporters/ : Create a new reporter
    - GET /api/reporters/ : Retrieve all reporters
    - GET /api/reporters/?id=1 : Retrieve a single reporter by ID
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, TypeError):
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)

        # Instantiate Reporter object
        reporter = Reporter(
            id=data.get('id'),
            name=data.get('name'),
            email=data.get('email'),
            team=data.get('team')
        )

        # Validate Reporter OOP rules
        try:
            reporter.validate()
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

        reporters = read_json_file(REPORTERS_FILE)

        # Prevent duplicate Reporter ID
        if any(r.get('id') == reporter.id for r in reporters):
            return JsonResponse({'error': f'Reporter with ID {reporter.id} already exists'}, status=400)

        # Save to JSON file
        reporter_data = reporter.to_dict()
        reporters.append(reporter_data)
        write_json_file(REPORTERS_FILE, reporters)

        return JsonResponse(reporter_data, status=201)

    elif request.method == 'GET':
        reporters = read_json_file(REPORTERS_FILE)
        reporter_id = request.GET.get('id')

        # Single reporter lookup by ID
        if reporter_id is not None:
            try:
                target_id = int(reporter_id)
            except ValueError:
                return JsonResponse({'error': 'Invalid ID parameter'}, status=400)

            for reporter in reporters:
                if reporter.get('id') == target_id:
                    return JsonResponse(reporter, status=200)
            return JsonResponse({'error': 'Reporter not found'}, status=404)

        # List all reporters
        return JsonResponse(reporters, safe=False, status=200)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def issue_views(request):
    """
    Handles Issue API endpoints:
    - POST /api/issues/ : Create a new issue (instantiates class based on priority)
    - GET /api/issues/ : Retrieve all issues
    - GET /api/issues/?id=1 : Retrieve a single issue by ID
    - GET /api/issues/?status=open : Retrieve all issues filtered by status
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, TypeError):
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)

        priority = data.get('priority')

        # OOP Polymorphic instantiation based on priority
        if priority == 'critical':
            issue = CriticalIssue(
                id=data.get('id'),
                title=data.get('title'),
                description=data.get('description'),
                status=data.get('status'),
                priority=data.get('priority'),
                reporter_id=data.get('reporter_id')
            )
        elif priority == 'low':
            issue = LowPriorityIssue(
                id=data.get('id'),
                title=data.get('title'),
                description=data.get('description'),
                status=data.get('status'),
                priority=data.get('priority'),
                reporter_id=data.get('reporter_id')
            )
        else:
            issue = Issue(
                id=data.get('id'),
                title=data.get('title'),
                description=data.get('description'),
                status=data.get('status'),
                priority=data.get('priority'),
                reporter_id=data.get('reporter_id')
            )

        # Validate Issue rules
        try:
            issue.validate()
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

        # Verify reporter existence in reporters.json
        reporters = read_json_file(REPORTERS_FILE)
        if not any(r.get('id') == issue.reporter_id for r in reporters):
            return JsonResponse({'error': f'Reporter with ID {issue.reporter_id} not found'}, status=404)

        issues = read_json_file(ISSUES_FILE)

        # Prevent duplicate Issue ID
        if any(item.get('id') == issue.id for item in issues):
            return JsonResponse({'error': f'Issue with ID {issue.id} already exists'}, status=400)

        # Prepare response payload with describe() message
        response_data = issue.to_dict()
        response_data['message'] = issue.describe()

        # Save to issues.json
        issues.append(response_data)
        write_json_file(ISSUES_FILE, issues)

        return JsonResponse(response_data, status=201)

    elif request.method == 'GET':
        issues = read_json_file(ISSUES_FILE)
        issue_id = request.GET.get('id')
        status = request.GET.get('status')

        # Get single issue by ID
        if issue_id is not None:
            try:
                target_id = int(issue_id)
            except ValueError:
                return JsonResponse({'error': 'Invalid ID parameter'}, status=400)

            for issue in issues:
                if issue.get('id') == target_id:
                    return JsonResponse(issue, status=200)
            return JsonResponse({'error': 'Issue not found'}, status=404)

        # Filter issues by status
        if status is not None:
            filtered_issues = [issue for issue in issues if issue.get('status') == status]
            return JsonResponse(filtered_issues, safe=False, status=200)

        # List all issues
        return JsonResponse(issues, safe=False, status=200)

    return JsonResponse({'error': 'Method not allowed'}, status=405)
