# integration_services.py
# Integration services for Azure DevOps

import os
import tempfile

# Ensure a writable cache/home directory on serverless platforms (Vercel, AWS Lambda, etc.)
# The azure-devops package attempts to create cache directories under the user's home
# at import time which fails on read-only filesystems. Force XDG_CACHE_HOME and HOME
# to a writable temporary directory when the default home is not writable.
try:
    home = os.environ.get('HOME', '')
    # If HOME is not writable (common in some serverless environments), use a temp dir
    if home and not os.access(home, os.W_OK):
        tmp = tempfile.mkdtemp(prefix='baagent_cache_')
        os.environ['XDG_CACHE_HOME'] = tmp
        os.environ['HOME'] = tmp
    # If HOME not set at all, set it to a temp dir as well
    if not os.environ.get('HOME'):
        tmp = tempfile.mkdtemp(prefix='baagent_cache_')
        os.environ['XDG_CACHE_HOME'] = tmp
        os.environ['HOME'] = tmp
except Exception:
    # If anything goes wrong, fall back to existing env vars and hope import succeeds
    pass
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import base64
from urllib.parse import urlencode
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import uuid

class AzureDevOpsService:
    """Azure DevOps integration service"""
    
    def __init__(self, organization_url: str, personal_access_token: str):
        self.organization_url = organization_url
        self.pat_token = personal_access_token
        self.credentials = BasicAuthentication('', personal_access_token)
        self.connection = Connection(base_url=organization_url, creds=self.credentials)
    
    def get_projects(self) -> List[Dict]:
        """Get all projects in the organization"""
        try:
            core_client = self.connection.clients.get_core_client()
            projects = core_client.get_projects()
            
            return [
                {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'state': project.state,
                    'visibility': project.visibility
                }
                for project in projects
            ]
            
        except Exception as e:
            print(f"❌ Error getting Azure DevOps projects: {e}")
            return []
    
    def get_work_items(self, project_id: str, query: str = None) -> List[Dict]:
        """Get work items from a project"""
        try:
            wit_client = self.connection.clients.get_work_item_tracking_client()
            
            if query:
                # Use custom query
                wiql_query = query
            else:
                # Default query to get all user stories, features, and epics
                wiql_query = f"""
                SELECT [System.Id], [System.Title], [System.Description], [System.WorkItemType], [System.State]
                FROM WorkItems
                WHERE [System.TeamProject] = '{project_id}'
                AND [System.WorkItemType] IN ('User Story', 'Feature', 'Epic', 'Requirement')
                ORDER BY [System.ChangedDate] DESC
                """
            
            wiql_results = wit_client.query_by_wiql(wiql_query)
            
            work_items = []
            if wiql_results.work_items:
                # Get detailed information for each work item
                work_item_ids = [wi.id for wi in wiql_results.work_items]
                detailed_items = wit_client.get_work_items(work_item_ids)
                
                for item in detailed_items:
                    work_items.append({
                        'id': item.id,
                        'title': item.fields.get('System.Title', ''),
                        'description': item.fields.get('System.Description', ''),
                        'type': item.fields.get('System.WorkItemType', ''),
                        'state': item.fields.get('System.State', ''),
                        'assigned_to': item.fields.get('System.AssignedTo', {}).get('displayName', ''),
                        'created_date': item.fields.get('System.CreatedDate', ''),
                        'changed_date': item.fields.get('System.ChangedDate', ''),
                        'priority': item.fields.get('Microsoft.VSTS.Common.Priority', ''),
                        'area_path': item.fields.get('System.AreaPath', ''),
                        'iteration_path': item.fields.get('System.IterationPath', '')
                    })
            
            return work_items
            
        except Exception as e:
            print(f"❌ Error getting Azure DevOps work items: {e}")
            return []
    
    def get_work_item_by_id(self, work_item_id: int) -> Optional[Dict]:
        """Get specific work item by ID"""
        try:
            wit_client = self.connection.clients.get_work_item_tracking_client()
            work_item = wit_client.get_work_item(work_item_id)
            
            return {
                'id': work_item.id,
                'title': work_item.fields.get('System.Title', ''),
                'description': work_item.fields.get('System.Description', ''),
                'type': work_item.fields.get('System.WorkItemType', ''),
                'state': work_item.fields.get('System.State', ''),
                'assigned_to': work_item.fields.get('System.AssignedTo', {}).get('displayName', ''),
                'created_date': work_item.fields.get('System.CreatedDate', ''),
                'changed_date': work_item.fields.get('System.ChangedDate', ''),
                'priority': work_item.fields.get('Microsoft.VSTS.Common.Priority', ''),
                'area_path': work_item.fields.get('System.AreaPath', ''),
                'iteration_path': work_item.fields.get('System.IterationPath', ''),
                'tags': work_item.fields.get('System.Tags', ''),
                'acceptance_criteria': work_item.fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', '')
            }
            
        except Exception as e:
            print(f"❌ Error getting Azure DevOps work item: {e}")
            return None
    
    def create_work_item(self, project_id: str, work_item_type: str, title: str, description: str = None) -> Optional[Dict]:
        """Create a new work item"""
        try:
            wit_client = self.connection.clients.get_work_item_tracking_client()
            
            # Prepare work item fields
            fields = [
                {
                    'op': 'add',
                    'path': '/fields/System.Title',
                    'value': title
                }
            ]
            
            if description:
                fields.append({
                    'op': 'add',
                    'path': '/fields/System.Description',
                    'value': description
                })
            
            # Create work item
            work_item = wit_client.create_work_item(
                document=fields,
                project=project_id,
                type=work_item_type
            )
            
            return {
                'id': work_item.id,
                'url': work_item.url,
                'title': title,
                'type': work_item_type
            }
            
        except Exception as e:
            print(f"❌ Error creating Azure DevOps work item: {e}")
            return None
    
    def update_work_item(self, work_item_id: int, fields: Dict) -> bool:
        """Update an existing work item"""
        try:
            wit_client = self.connection.clients.get_work_item_tracking_client()
            
            # Prepare update operations
            operations = []
            for field_path, value in fields.items():
                operations.append({
                    'op': 'add',
                    'path': f'/fields/{field_path}',
                    'value': value
                })
            
            # Update work item
            wit_client.update_work_item(
                document=operations,
                id=work_item_id
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating Azure DevOps work item: {e}")
            return False
    
    def get_boards(self, project_id: str) -> List[Dict]:
        """Get boards for a project"""
        try:
            work_client = self.connection.clients.get_work_client()
            boards = work_client.get_boards(project_id)
            
            return [
                {
                    'id': board.id,
                    'name': board.name,
                    'url': board.url
                }
                for board in boards
            ]
            
        except Exception as e:
            print(f"❌ Error getting Azure DevOps boards: {e}")
            return []

class IntegrationManager:
    """Manager for all integrations"""
    
    def __init__(self):
        self.ado_services = {}  # Store ADO services per organization
    
    def setup_azure_devops(self, organization_url: str, personal_access_token: str) -> bool:
        """Setup Azure DevOps connection"""
        try:
            ado_service = AzureDevOpsService(organization_url, personal_access_token)
            # Test connection by getting projects
            projects = ado_service.get_projects()
            if projects:
                self.ado_services[organization_url] = ado_service
                return True
            return False
        except Exception as e:
            print(f"❌ Error setting up Azure DevOps: {e}")
            return False
    
    def get_ado_projects(self, organization_url: str) -> List[Dict]:
        """Get projects from Azure DevOps"""
        if organization_url in self.ado_services:
            return self.ado_services[organization_url].get_projects()
        return []
    
    def get_ado_work_items(self, organization_url: str, project_id: str, query: str = None) -> List[Dict]:
        """Get work items from Azure DevOps"""
        if organization_url in self.ado_services:
            return self.ado_services[organization_url].get_work_items(project_id, query)
        return []
    
    def import_requirements_from_ado(self, organization_url: str, project_id: str) -> List[Dict]:
        """Import requirements from Azure DevOps work items"""
        work_items = self.get_ado_work_items(organization_url, project_id)
        
        requirements = []
        for item in work_items:
            if item['type'] in ['User Story', 'Feature', 'Epic', 'Requirement']:
                requirements.append({
                    'source': 'azure_devops',
                    'source_id': item['id'],
                    'title': item['title'],
                    'description': item['description'],
                    'type': item['type'],
                    'priority': item.get('priority', ''),
                    'assigned_to': item.get('assigned_to', ''),
                    'tags': item.get('tags', ''),
                    'acceptance_criteria': item.get('acceptance_criteria', ''),
                    'content': f"# {item['title']}\n\n{item['description']}\n\n**Type:** {item['type']}\n**Priority:** {item.get('priority', 'N/A')}\n**Assigned To:** {item.get('assigned_to', 'N/A')}"
                })
        
        return requirements

# Test function
def test_integrations():
    """Test integration services"""
    print("🧪 Testing Integration Services...")
    
    # Test Azure DevOps service (requires valid credentials)
    print("\n🔧 Testing Azure DevOps Integration:")
    ado_url = os.getenv('ADO_ORGANIZATION_URL')
    ado_token = os.getenv('ADO_PAT_TOKEN')
    
    if ado_url and ado_token:
        ado_service = AzureDevOpsService(ado_url, ado_token)
        projects = ado_service.get_projects()
        print(f"✅ Found {len(projects)} Azure DevOps projects")
    else:
        print("⚠️ Azure DevOps credentials not configured")
        projects = []
    
    # Test Integration Manager
    print("\n🔗 Testing Integration Manager:")
    manager = IntegrationManager()
    
    if ado_url and ado_token:
        success = manager.setup_azure_devops(ado_url, ado_token)
        print(f"✅ Azure DevOps setup: {success}")
    
    return {
        'ado_configured': bool(ado_url and ado_token),
        'projects_count': len(projects) if ado_url and ado_token else 0
    }

if __name__ == "__main__":
    test_integrations()
