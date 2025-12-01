"""
Mock Data Generator for THE ROUNDTABLE Demo

This module simulates Notion data without requiring actual API credentials.
Perfect for testing and demonstrations.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

class MockNotionData:
    """Simulates Notion API responses with realistic mock data."""
    
    def __init__(self):
        self.projects = self._generate_projects()
        self.tasks = self._generate_tasks()
        self.calendar_events = self._generate_calendar_events()
        self.notes = self._generate_notes()
    
    def _generate_projects(self) -> List[Dict[str, Any]]:
        """Generate mock project data."""
        return [
            {
                "id": "proj-001",
                "title": "🚀 Launch New Product Line",
                "status": "In Progress",
                "priority": "High",
                "budget": "$150,000",
                "deadline": "2025-12-31",
                "team_size": 8,
                "description": "Develop and launch new AI-powered productivity tools"
            },
            {
                "id": "proj-002",
                "title": "📚 Complete Online Course",
                "status": "In Progress",
                "priority": "Medium",
                "budget": "$500",
                "deadline": "2025-11-30",
                "completion": "75%",
                "description": "Advanced machine learning specialization on Coursera"
            },
            {
                "id": "proj-003",
                "title": "🏠 Home Renovation",
                "status": "Planning",
                "priority": "Low",
                "budget": "$25,000",
                "deadline": "2026-03-01",
                "description": "Kitchen and bathroom remodeling"
            },
            {
                "id": "proj-004",
                "title": "💼 Career Transition Planning",
                "status": "Active",
                "priority": "High",
                "budget": "$5,000",
                "deadline": "2026-01-15",
                "description": "Transition from corporate to entrepreneurship"
            },
            {
                "id": "proj-005",
                "title": "🌍 World Travel Adventure",
                "status": "Research",
                "priority": "Medium",
                "budget": "$35,000",
                "deadline": "2026-06-01",
                "description": "6-month sabbatical traveling through Europe and Asia"
            }
        ]
    
    def _generate_tasks(self) -> List[Dict[str, Any]]:
        """Generate mock task data."""
        return [
            {"id": "task-001", "title": "Finalize product specs", "project": "Launch New Product Line", "due": "2025-12-05", "status": "Todo"},
            {"id": "task-002", "title": "Hire senior developer", "project": "Launch New Product Line", "due": "2025-12-10", "status": "In Progress"},
            {"id": "task-003", "title": "Complete module 4 assignments", "project": "Complete Online Course", "due": "2025-12-02", "status": "Todo"},
            {"id": "task-004", "title": "Submit final project", "project": "Complete Online Course", "due": "2025-11-28", "status": "Urgent"},
            {"id": "task-005", "title": "Get kitchen contractor quotes", "project": "Home Renovation", "due": "2026-01-15", "status": "Todo"},
            {"id": "task-006", "title": "Update LinkedIn profile", "project": "Career Transition Planning", "due": "2025-12-08", "status": "Todo"},
            {"id": "task-007", "title": "Network with 5 entrepreneurs", "project": "Career Transition Planning", "due": "2025-12-15", "status": "In Progress"},
            {"id": "task-008", "title": "Book flights to Europe", "project": "World Travel Adventure", "due": "2026-02-01", "status": "Todo"},
        ]
    
    def _generate_calendar_events(self) -> List[Dict[str, Any]]:
        """Generate mock calendar events for the next 30 days."""
        base_date = datetime.now()
        events = []
        
        # Weekly recurring meetings
        for week in range(4):
            # Team standup (Mon, Wed, Fri)
            for day in [0, 2, 4]:
                event_date = base_date + timedelta(days=(week * 7 + day))
                events.append({
                    "id": f"event-standup-w{week}-d{day}",
                    "title": "Team Standup",
                    "date": event_date.strftime("%Y-%m-%d"),
                    "time": "09:00 AM",
                    "duration": "30 min",
                    "type": "Meeting"
                })
        
        # Important deadlines
        events.extend([
            {
                "id": "event-deadline-1",
                "title": "Course Final Project Due",
                "date": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
                "time": "11:59 PM",
                "duration": "All day",
                "type": "Deadline",
                "priority": "Critical"
            },
            {
                "id": "event-deadline-2",
                "title": "Product Spec Review",
                "date": (base_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                "time": "02:00 PM",
                "duration": "2 hours",
                "type": "Meeting"
            },
            {
                "id": "event-networking-1",
                "title": "Coffee with Startup Founder",
                "date": (base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
                "time": "10:00 AM",
                "duration": "1 hour",
                "type": "Networking"
            },
            {
                "id": "event-personal-1",
                "title": "Doctor's Appointment",
                "date": (base_date + timedelta(days=9)).strftime("%Y-%m-%d"),
                "time": "03:30 PM",
                "duration": "1 hour",
                "type": "Personal"
            },
            {
                "id": "event-vacation-1",
                "title": "Family Holiday Trip",
                "date": (base_date + timedelta(days=25)).strftime("%Y-%m-%d"),
                "time": "All day",
                "duration": "5 days",
                "type": "Vacation"
            },
        ])
        
        return sorted(events, key=lambda x: x["date"])
    
    def _generate_notes(self) -> List[Dict[str, Any]]:
        """Generate mock note pages."""
        return [
            {
                "id": "note-001",
                "title": "Goals for 2026",
                "content": "1. Launch successful product\n2. Complete career transition\n3. Take extended sabbatical\n4. Improve work-life balance",
                "tags": ["goals", "planning"]
            },
            {
                "id": "note-002",
                "title": "Financial Status",
                "content": "Savings: $85,000\nMonthly income: $12,000\nMonthly expenses: $6,500\nInvestment portfolio: $145,000",
                "tags": ["finance", "budget"]
            },
            {
                "id": "note-003",
                "title": "Sabbatical Planning Notes",
                "content": "Countries to visit: Italy, Greece, Japan, Thailand\nEstimated cost: $35,000\nDuration: 6 months\nTiming: Q2 2026",
                "tags": ["travel", "sabbatical"]
            }
        ]
    
    def search(self, query: str) -> Dict[str, Any]:
        """Simulate Notion search."""
        query_lower = query.lower()
        results = []
        
        # Search projects
        for project in self.projects:
            if query_lower in project["title"].lower() or query_lower in project["description"].lower():
                results.append({
                    "type": "project",
                    "data": project
                })
        
        # Search tasks
        for task in self.tasks:
            if query_lower in task["title"].lower():
                results.append({
                    "type": "task",
                    "data": task
                })
        
        # Search notes
        for note in self.notes:
            if query_lower in note["title"].lower() or query_lower in note["content"].lower():
                results.append({
                    "type": "note",
                    "data": note
                })
        
        return {
            "results": results,
            "total": len(results)
        }
    
    def get_calendar_events(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Get upcoming calendar events."""
        cutoff_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        relevant_events = [e for e in self.calendar_events if e["date"] <= cutoff_date]
        
        return {
            "events": relevant_events,
            "total": len(relevant_events),
            "summary": f"{len(relevant_events)} events in the next {days_ahead} days"
        }
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        return self.projects
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks."""
        return self.tasks


# Global instance for easy access
mock_data = MockNotionData()
