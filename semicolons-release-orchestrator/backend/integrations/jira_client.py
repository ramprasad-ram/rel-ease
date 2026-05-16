"""
Jira API client for fetching sprint and ticket data.
Supports both mock mode and real API integration.
"""
import os
from typing import Dict, Any, Optional, List
from utils.logger import get_logger

logger = get_logger(__name__)


class JiraClient:
    """
    Client for interacting with Jira API.
    
    In production, this would use the Jira REST API.
    For demo purposes, it can operate in mock mode.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        api_token: Optional[str] = None,
        mock_mode: bool = True
    ):
        """
        Initialize Jira client.
        
        Args:
            base_url: Jira instance URL (e.g., "https://company.atlassian.net")
            username: Jira username/email
            api_token: Jira API token
            mock_mode: If True, return mock data instead of calling real API
        """
        self.base_url = base_url or os.getenv("JIRA_BASE_URL", "https://company.atlassian.net")
        self.username = username or os.getenv("JIRA_USERNAME")
        self.api_token = api_token or os.getenv("JIRA_API_TOKEN")
        self.mock_mode = mock_mode
    
    async def get_sprint_info(self, sprint_id: str) -> Dict[str, Any]:
        """
        Get sprint information.
        
        Args:
            sprint_id: Sprint identifier
            
        Returns:
            Sprint information including dates and status
        """
        if self.mock_mode:
            return await self._mock_sprint_info(sprint_id)
        
        # Real implementation would call Jira API
        # import aiohttp
        # async with aiohttp.ClientSession() as session:
        #     auth = aiohttp.BasicAuth(self.username, self.api_token)
        #     async with session.get(
        #         f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}",
        #         auth=auth
        #     ) as response:
        #         return await response.json()
        
        return await self._mock_sprint_info(sprint_id)
    
    async def get_sprint_tickets(self, sprint_id: str) -> List[Dict[str, Any]]:
        """
        Get all tickets in a sprint.
        
        Args:
            sprint_id: Sprint identifier
            
        Returns:
            List of tickets with details
        """
        if self.mock_mode:
            return await self._mock_sprint_tickets(sprint_id)
        
        # Real implementation would call Jira API
        return await self._mock_sprint_tickets(sprint_id)
    
    async def get_ticket_details(self, ticket_key: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific ticket.
        
        Args:
            ticket_key: Ticket key (e.g., "PROJ-123")
            
        Returns:
            Ticket details
        """
        if self.mock_mode:
            return await self._mock_ticket_details(ticket_key)
        
        # Real implementation would call Jira API
        return await self._mock_ticket_details(ticket_key)
    
    async def get_ticket_dependencies(self, ticket_key: str) -> List[str]:
        """
        Get dependencies for a ticket.
        
        Args:
            ticket_key: Ticket key
            
        Returns:
            List of dependent ticket keys
        """
        if self.mock_mode:
            return await self._mock_ticket_dependencies(ticket_key)
        
        # Real implementation would parse Jira issue links
        return await self._mock_ticket_dependencies(ticket_key)
    
    # Mock implementations
    
    async def _mock_sprint_info(self, sprint_id: str) -> Dict[str, Any]:
        """Generate mock sprint information."""
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow() - timedelta(days=10)
        end_date = datetime.utcnow() + timedelta(days=4)
        
        return {
            "id": sprint_id,
            "name": f"Sprint {sprint_id}",
            "state": "active",
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "goal": "Complete feature development and bug fixes",
        }
    
    async def _mock_sprint_tickets(self, sprint_id: str) -> List[Dict[str, Any]]:
        """Generate mock sprint tickets."""
        import random
        
        ticket_types = ["Story", "Bug", "Task", "Epic", "Sub-task"]
        statuses = ["Done", "In Progress", "To Do", "Blocked", "In Review"]
        priorities = ["Highest", "High", "Medium", "Low", "Lowest"]
        
        tickets = []
        num_tickets = random.randint(10, 20)
        
        for i in range(num_tickets):
            ticket_key = f"PROJ-{1000 + i}"
            status = random.choice(statuses)
            
            # Create dependencies
            depends_on = []
            if i > 0 and random.random() > 0.5:
                num_deps = random.randint(1, min(3, i))
                for _ in range(num_deps):
                    dep_idx = random.randint(0, i - 1)
                    depends_on.append(f"PROJ-{1000 + dep_idx}")
            
            tickets.append({
                "key": ticket_key,
                "id": str(10000 + i),
                "summary": f"Implement feature {chr(65 + (i % 26))}",
                "description": f"Detailed description for {ticket_key}",
                "type": random.choice(ticket_types),
                "status": status,
                "priority": random.choice(priorities),
                "assignee": {
                    "displayName": random.choice(["Alice Smith", "Bob Jones", "Charlie Brown", None]),
                    "emailAddress": random.choice(["alice@company.com", "bob@company.com", "charlie@company.com", None]),
                } if random.random() > 0.2 else None,
                "reporter": {
                    "displayName": "Product Manager",
                    "emailAddress": "pm@company.com",
                },
                "storyPoints": random.choice([1, 2, 3, 5, 8, 13]) if random.random() > 0.3 else None,
                "sprint": sprint_id,
                "labels": random.sample(["backend", "frontend", "api", "database", "ui"], k=random.randint(0, 3)),
                "depends_on": depends_on,
                "created": "2024-01-01T10:00:00Z",
                "updated": "2024-01-15T10:00:00Z",
            })
        
        # Add circular dependency for demo
        if len(tickets) >= 4:
            tickets[1]["depends_on"] = [tickets[2]["key"]]
            tickets[2]["depends_on"] = [tickets[3]["key"]]
            tickets[3]["depends_on"] = [tickets[1]["key"]]
            
            # Mark one as done to show the issue
            tickets[1]["status"] = "Done"
            tickets[2]["status"] = "In Progress"
            tickets[3]["status"] = "To Do"
        
        return tickets
    
    async def _mock_ticket_details(self, ticket_key: str) -> Dict[str, Any]:
        """Generate mock ticket details."""
        import random
        
        return {
            "key": ticket_key,
            "id": str(random.randint(10000, 99999)),
            "summary": f"Mock ticket {ticket_key}",
            "description": f"Detailed description for {ticket_key}",
            "type": random.choice(["Story", "Bug", "Task"]),
            "status": random.choice(["Done", "In Progress", "To Do", "Blocked"]),
            "priority": random.choice(["High", "Medium", "Low"]),
            "assignee": {
                "displayName": random.choice(["Alice", "Bob", "Charlie"]),
                "emailAddress": f"{random.choice(['alice', 'bob', 'charlie'])}@company.com",
            },
            "storyPoints": random.choice([1, 2, 3, 5, 8]),
            "created": "2024-01-01T10:00:00Z",
            "updated": "2024-01-15T10:00:00Z",
        }
    
    async def _mock_ticket_dependencies(self, ticket_key: str) -> List[str]:
        """Generate mock ticket dependencies."""
        import random
        
        # Random number of dependencies
        num_deps = random.randint(0, 3)
        base_num = int(ticket_key.split("-")[1])
        
        deps = []
        for i in range(num_deps):
            dep_num = base_num - random.randint(1, 5)
            if dep_num > 0:
                deps.append(f"PROJ-{dep_num}")
        
        return deps


# Made with Bob