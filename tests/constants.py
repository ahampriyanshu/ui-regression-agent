"""Shared constants for regression test expectations."""

NON_UI_EXPECTATIONS = {
    "BE-001": {
        "status": "in_progress",
        "priority": "high",
        "type": "feature",
        "assignee": "backend.dev",
        "reporter": "product.manager",
        "title": "Implement Oauth 2.0",
    },
    "BE-002": {
        "status": "todo",
        "priority": "medium",
        "type": "fix",
        "assignee": "backend.dev",
        "reporter": "product.tester",
        "title": "Fix password reset email service",
    },
    "DOPS-001": {
        "status": "in_progress",
        "priority": "high",
        "type": "feature",
        "assignee": "backend.dev",
        "reporter": "product.manager",
        "title": "Update Qlty check",
    },
    "DATA-001": {
        "status": "todo",
        "priority": "medium",
        "type": "perf_improvement",
        "assignee": "backend.dev",
        "reporter": "product.manager",
        "title": "Optimize user analytics database queries",
    },
}
