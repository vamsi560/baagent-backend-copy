# phase3_templates.py
# Template Management System for Document Generation

import os
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from jinja2 import Template, Environment, FileSystemLoader
from pathlib import Path

# Custom imports
from database import get_db, Document, Analysis
from langchain_integration import langchain_integration

class TemplateManager:
    """Advanced template management system for document generation"""
    
    def __init__(self):
        self.templates_dir = Path("templates")
        self.templates_dir.mkdir(exist_ok=True)
        
        self.template_categories = {
            "TRD": "Technical Requirements Document",
            "HLD": "High-Level Design",
            "LLD": "Low-Level Design",
            "Backlog": "Project Backlog",
            "TestPlan": "Test Plan",
            "Deployment": "Deployment Guide",
            "UserManual": "User Manual",
            "API": "API Documentation"
        }
        
        self.industry_templates = {
            "finance": "Financial Services",
            "healthcare": "Healthcare",
            "ecommerce": "E-commerce",
            "education": "Education",
            "manufacturing": "Manufacturing",
            "retail": "Retail",
            "technology": "Technology",
            "government": "Government"
        }
        
        self.setup_default_templates()
    
    def setup_default_templates(self):
        """Initialize default templates"""
        self.create_default_trd_template()
        self.create_default_hld_template()
        self.create_default_lld_template()
        self.create_default_backlog_template()
        self.create_default_test_plan_template()
        self.create_default_deployment_template()
        self.create_default_user_manual_template()
        self.create_default_api_template()
    
    def create_default_trd_template(self):
        """Create default TRD template"""
        template_content = """# TECHNICAL REQUIREMENTS DOCUMENT

## 1. EXECUTIVE SUMMARY
### 1.1 Project Overview
{{ project_overview }}

### 1.2 Key Objectives
{% for objective in key_objectives %}
- {{ objective }}
{% endfor %}

### 1.3 Success Criteria
{% for criterion in success_criteria %}
- {{ criterion }}
{% endfor %}

## 2. SYSTEM OVERVIEW
### 2.1 High-Level Architecture
{{ high_level_architecture }}

### 2.2 System Components
{% for component in system_components %}
- **{{ component.name }}**: {{ component.description }}
{% endfor %}

### 2.3 Technology Stack
{% for tech in technology_stack %}
- **{{ tech.category }}**: {{ tech.technologies | join(', ') }}
{% endfor %}

## 3. FUNCTIONAL REQUIREMENTS
### 3.1 User Stories
{% for story in user_stories %}
#### {{ story.title }}
**As a** {{ story.actor }}  
**I want** {{ story.action }}  
**So that** {{ story.benefit }}

**Acceptance Criteria:**
{% for criterion in story.acceptance_criteria %}
- {{ criterion }}
{% endfor %}

**Priority**: {{ story.priority }}  
**Effort**: {{ story.effort }} story points
{% endfor %}

### 3.2 Business Rules
{% for rule in business_rules %}
- **{{ rule.name }}**: {{ rule.description }}
{% endfor %}

## 4. NON-FUNCTIONAL REQUIREMENTS
### 4.1 Performance Requirements
- **Response Time**: {{ performance.response_time }}
- **Throughput**: {{ performance.throughput }}
- **Scalability**: {{ performance.scalability }}

### 4.2 Security Requirements
{% for req in security_requirements %}
- {{ req }}
{% endfor %}

### 4.3 Availability Requirements
- **Uptime**: {{ availability.uptime }}
- **Recovery Time**: {{ availability.recovery_time }}

## 5. TECHNICAL SPECIFICATIONS
### 5.1 API Specifications
{% for api in api_specifications %}
#### {{ api.name }}
- **Endpoint**: {{ api.endpoint }}
- **Method**: {{ api.method }}
- **Parameters**: {{ api.parameters | join(', ') }}
- **Response**: {{ api.response }}
{% endfor %}

### 5.2 Database Design
{% for table in database_tables %}
#### {{ table.name }}
{% for column in table.columns %}
- **{{ column.name }}**: {{ column.type }} {% if column.constraints %}({{ column.constraints | join(', ') }}){% endif %}
{% endfor %}
{% endfor %}

## 6. SECURITY CONSIDERATIONS
### 6.1 Authentication & Authorization
{{ security.authentication }}

### 6.2 Data Protection
{{ security.data_protection }}

### 6.3 Compliance Requirements
{% for compliance in compliance_requirements %}
- {{ compliance }}
{% endfor %}

## 7. DEPLOYMENT & OPERATIONS
### 7.1 Infrastructure Requirements
{{ deployment.infrastructure }}

### 7.2 Deployment Strategy
{{ deployment.strategy }}

### 7.3 Monitoring & Maintenance
{{ deployment.monitoring }}

## 8. TESTING STRATEGY
### 8.1 Test Types
{% for test_type in test_types %}
- **{{ test_type.name }}**: {{ test_type.description }}
{% endfor %}

### 8.2 Quality Assurance
{{ quality_assurance }}

### 8.3 Acceptance Criteria
{% for criterion in acceptance_criteria %}
- {{ criterion }}
{% endfor %}

---
**Document Version**: {{ version }}  
**Last Updated**: {{ last_updated }}  
**Prepared By**: {{ prepared_by }}  
**Approved By**: {{ approved_by }}
"""
        
        self.save_template("TRD", "default", template_content)
    
    def create_default_hld_template(self):
        """Create default HLD template"""
        template_content = """# HIGH-LEVEL DESIGN DOCUMENT

## 1. SYSTEM ARCHITECTURE OVERVIEW
### 1.1 Architecture Pattern
{{ architecture_pattern }}

### 1.2 System Layers
{% for layer in system_layers %}
#### {{ layer.name }}
{{ layer.description }}

**Components:**
{% for component in layer.components %}
- {{ component }}
{% endfor %}
{% endfor %}

## 2. COMPONENT DIAGRAM
```mermaid
{{ mermaid_diagram }}
```

## 3. TECHNOLOGY STACK
### 3.1 Frontend Technologies
{% for tech in frontend_technologies %}
- **{{ tech.name }}**: {{ tech.version }} - {{ tech.purpose }}
{% endfor %}

### 3.2 Backend Technologies
{% for tech in backend_technologies %}
- **{{ tech.name }}**: {{ tech.version }} - {{ tech.purpose }}
{% endfor %}

### 3.3 Database Technologies
{% for tech in database_technologies %}
- **{{ tech.name }}**: {{ tech.version }} - {{ tech.purpose }}
{% endfor %}

### 3.4 Infrastructure Technologies
{% for tech in infrastructure_technologies %}
- **{{ tech.name }}**: {{ tech.version }} - {{ tech.purpose }}
{% endfor %}

## 4. INTEGRATION POINTS
### 4.1 External Systems
{% for system in external_systems %}
#### {{ system.name }}
- **Purpose**: {{ system.purpose }}
- **Integration Type**: {{ system.integration_type }}
- **Data Flow**: {{ system.data_flow }}
- **Security**: {{ system.security }}
{% endfor %}

### 4.2 Internal Services
{% for service in internal_services %}
#### {{ service.name }}
- **Purpose**: {{ service.purpose }}
- **API Endpoints**: {{ service.endpoints | join(', ') }}
- **Dependencies**: {{ service.dependencies | join(', ') }}
{% endfor %}

## 5. DATA FLOW
### 5.1 Data Architecture
{{ data_architecture }}

### 5.2 Data Flow Diagrams
{% for flow in data_flows %}
#### {{ flow.name }}
{{ flow.description }}
{% endfor %}

## 6. SECURITY ARCHITECTURE
### 6.1 Security Layers
{% for layer in security_layers %}
#### {{ layer.name }}
{{ layer.description }}
{% endfor %}

### 6.2 Authentication & Authorization
{{ security.auth_system }}

### 6.3 Data Protection
{{ security.data_protection }}

## 7. SCALABILITY CONSIDERATIONS
### 7.1 Horizontal Scaling
{{ scalability.horizontal }}

### 7.2 Vertical Scaling
{{ scalability.vertical }}

### 7.3 Load Balancing
{{ scalability.load_balancing }}

## 8. PERFORMANCE CONSIDERATIONS
### 8.1 Caching Strategy
{{ performance.caching }}

### 8.2 Database Optimization
{{ performance.database }}

### 8.3 CDN Strategy
{{ performance.cdn }}

---
**Document Version**: {{ version }}  
**Last Updated**: {{ last_updated }}  
**Prepared By**: {{ prepared_by }}  
**Approved By**: {{ approved_by }}
"""
        
        self.save_template("HLD", "default", template_content)
    
    def create_default_lld_template(self):
        """Create default LLD template"""
        template_content = """# LOW-LEVEL DESIGN DOCUMENT

## 1. DETAILED COMPONENT DESIGN
### 1.1 Component Architecture
{{ component_architecture }}

### 1.2 Class Diagrams
{% for diagram in class_diagrams %}
#### {{ diagram.name }}
```mermaid
{{ diagram.mermaid }}
```
{% endfor %}

## 2. DATABASE SCHEMA
### 2.1 Entity Relationship Diagram
```mermaid
{{ er_diagram }}
```

### 2.2 Table Definitions
{% for table in database_tables %}
#### {{ table.name }}
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
{% for column in table.columns %}
| {{ column.name }} | {{ column.type }} | {{ column.constraints | join(', ') }} | {{ column.description }} |
{% endfor %}

**Indexes:**
{% for index in table.indexes %}
- {{ index }}
{% endfor %}
{% endfor %}

## 3. API SPECIFICATIONS
### 3.1 REST API Endpoints
{% for endpoint in api_endpoints %}
#### {{ endpoint.name }}
- **URL**: {{ endpoint.url }}
- **Method**: {{ endpoint.method }}
- **Description**: {{ endpoint.description }}

**Request Parameters:**
{% for param in endpoint.parameters %}
- `{{ param.name }}` ({{ param.type }}) - {{ param.description }} {% if param.required %}[Required]{% endif %}
{% endfor %}

**Response:**
```json
{{ endpoint.response }}
```

**Error Codes:**
{% for error in endpoint.errors %}
- `{{ error.code }}`: {{ error.message }}
{% endfor %}
{% endfor %}

### 3.2 GraphQL Schema
```graphql
{{ graphql_schema }}
```

## 4. SEQUENCE DIAGRAMS
{% for diagram in sequence_diagrams %}
### {{ diagram.name }}
```mermaid
{{ diagram.mermaid }}
```
{% endfor %}

## 5. ERROR HANDLING
### 5.1 Error Categories
{% for category in error_categories %}
#### {{ category.name }}
{{ category.description }}

**Error Codes:**
{% for error in category.errors %}
- `{{ error.code }}`: {{ error.message }}
{% endfor %}
{% endfor %}

### 5.2 Exception Handling Strategy
{{ exception_handling }}

## 6. PERFORMANCE OPTIMIZATIONS
### 6.1 Caching Strategy
{% for cache in caching_strategies %}
#### {{ cache.name }}
- **Type**: {{ cache.type }}
- **Scope**: {{ cache.scope }}
- **TTL**: {{ cache.ttl }}
- **Implementation**: {{ cache.implementation }}
{% endfor %}

### 6.2 Database Optimizations
{% for optimization in database_optimizations %}
- **{{ optimization.name }}**: {{ optimization.description }}
{% endfor %}

### 6.3 Code Optimizations
{% for optimization in code_optimizations %}
- **{{ optimization.name }}**: {{ optimization.description }}
{% endfor %}

## 7. SECURITY IMPLEMENTATION
### 7.1 Input Validation
{{ security.input_validation }}

### 7.2 SQL Injection Prevention
{{ security.sql_injection }}

### 7.3 XSS Prevention
{{ security.xss_prevention }}

### 7.4 CSRF Protection
{{ security.csrf_protection }}

## 8. TESTING STRATEGY
### 8.1 Unit Testing
{{ testing.unit_testing }}

### 8.2 Integration Testing
{{ testing.integration_testing }}

### 8.3 Performance Testing
{{ testing.performance_testing }}

---
**Document Version**: {{ version }}  
**Last Updated**: {{ last_updated }}  
**Prepared By**: {{ prepared_by }}  
**Approved By**: {{ approved_by }}
"""
        
        self.save_template("LLD", "default", template_content)
    
    def create_default_backlog_template(self):
        """Create default backlog template"""
        template_content = """# PROJECT BACKLOG

## EPICS
{% for epic in epics %}
### {{ epic.title }}
**Description**: {{ epic.description }}  
**Priority**: {{ epic.priority }}  
**Effort**: {{ epic.effort }} story points  
**TRD Sections**: {{ epic.trd_sections | join(', ') }}  
**Requirements Covered**: {{ epic.requirements_covered | join(', ') }}

{% for feature in epic.features %}
#### {{ feature.title }}
**Description**: {{ feature.description }}  
**Priority**: {{ feature.priority }}  
**Effort**: {{ feature.effort }} story points  
**TRD Sections**: {{ feature.trd_sections | join(', ') }}  
**Requirements Covered**: {{ feature.requirements_covered | join(', ') }}

{% for story in feature.stories %}
##### {{ story.title }}
**Description**: {{ story.description }}  
**Priority**: {{ story.priority }}  
**Effort**: {{ story.effort }} story points  
**Acceptance Criteria:**
{% for criterion in story.acceptance_criteria %}
- {{ criterion }}
{% endfor %}
**TRD Sections**: {{ story.trd_sections | join(', ') }}  
**Requirements Covered**: {{ story.requirements_covered | join(', ') }}

{% endfor %}
{% endfor %}
{% endfor %}

## BACKLOG STATISTICS
- **Total Epics**: {{ statistics.total_epics }}
- **Total Features**: {{ statistics.total_features }}
- **Total User Stories**: {{ statistics.total_stories }}
- **Total Story Points**: {{ statistics.total_story_points }}
- **Average Story Points per Story**: {{ statistics.avg_story_points }}

## PRIORITY BREAKDOWN
{% for priority in priority_breakdown %}
- **{{ priority.level }}**: {{ priority.count }} items ({{ priority.story_points }} story points)
{% endfor %}

---
**Generated**: {{ generated_date }}  
**Project**: {{ project_name }}  
**Version**: {{ version }}
"""
        
        self.save_template("Backlog", "default", template_content)
    
    def create_default_test_plan_template(self):
        """Create default test plan template"""
        template_content = """# TEST PLAN

## 1. TEST STRATEGY
### 1.1 Testing Objectives
{% for objective in testing_objectives %}
- {{ objective }}
{% endfor %}

### 1.2 Testing Scope
{{ testing_scope }}

### 1.3 Testing Approach
{{ testing_approach }}

## 2. TEST TYPES
{% for test_type in test_types %}
### 2.{{ loop.index }} {{ test_type.name }}
**Purpose**: {{ test_type.purpose }}  
**Scope**: {{ test_type.scope }}  
**Tools**: {{ test_type.tools | join(', ') }}  
**Timeline**: {{ test_type.timeline }}

**Test Cases:**
{% for test_case in test_type.test_cases %}
#### {{ test_case.title }}
- **Objective**: {{ test_case.objective }}
- **Preconditions**: {{ test_case.preconditions }}
- **Test Steps**: {{ test_case.steps | join('; ') }}
- **Expected Result**: {{ test_case.expected_result }}
- **Priority**: {{ test_case.priority }}
{% endfor %}
{% endfor %}

## 3. TEST ENVIRONMENT
### 3.1 Environment Setup
{{ environment.setup }}

### 3.2 Test Data Requirements
{% for data_req in test_data_requirements %}
- **{{ data_req.name }}**: {{ data_req.description }}
{% endfor %}

## 4. TEST EXECUTION
### 4.1 Test Schedule
{{ test_schedule }}

### 4.2 Test Execution Process
{{ execution_process }}

## 5. DEFECT MANAGEMENT
### 5.1 Defect Lifecycle
{{ defect_lifecycle }}

### 5.2 Defect Reporting
{{ defect_reporting }}

---
**Document Version**: {{ version }}  
**Last Updated**: {{ last_updated }}  
**Prepared By**: {{ prepared_by }}
"""
        
        self.save_template("TestPlan", "default", template_content)
    
    def create_default_deployment_template(self):
        """Create default deployment template"""
        template_content = """# DEPLOYMENT GUIDE

## 1. DEPLOYMENT OVERVIEW
### 1.1 Deployment Strategy
{{ deployment_strategy }}

### 1.2 Deployment Phases
{% for phase in deployment_phases %}
#### Phase {{ phase.number }}: {{ phase.name }}
- **Objective**: {{ phase.objective }}
- **Timeline**: {{ phase.timeline }}
- **Success Criteria**: {{ phase.success_criteria }}
{% endfor %}

## 2. INFRASTRUCTURE REQUIREMENTS
### 2.1 Server Requirements
{% for server in server_requirements %}
#### {{ server.name }}
- **CPU**: {{ server.cpu }}
- **RAM**: {{ server.ram }}
- **Storage**: {{ server.storage }}
- **OS**: {{ server.os }}
{% endfor %}

### 2.2 Network Requirements
{{ network_requirements }}

### 2.3 Security Requirements
{{ security_requirements }}

## 3. DEPLOYMENT STEPS
{% for step in deployment_steps %}
### 3.{{ loop.index }} {{ step.title }}
**Description**: {{ step.description }}  
**Commands**: {{ step.commands | join('; ') }}  
**Validation**: {{ step.validation }}
{% endfor %}

## 4. CONFIGURATION
### 4.1 Environment Variables
{% for env_var in environment_variables %}
- **{{ env_var.name }}**: {{ env_var.description }} {% if env_var.required %}[Required]{% endif %}
{% endfor %}

### 4.2 Configuration Files
{% for config in configuration_files %}
#### {{ config.name }}
```{{ config.language }}
{{ config.content }}
```
{% endfor %}

## 5. MONITORING AND MAINTENANCE
### 5.1 Monitoring Setup
{{ monitoring_setup }}

### 5.2 Health Checks
{% for check in health_checks %}
- **{{ check.name }}**: {{ check.description }}
{% endfor %}

### 5.3 Backup Strategy
{{ backup_strategy }}

---
**Document Version**: {{ version }}  
**Last Updated**: {{ last_updated }}  
**Prepared By**: {{ prepared_by }}
"""
        
        self.save_template("Deployment", "default", template_content)
    
    def create_default_user_manual_template(self):
        """Create default user manual template"""
        template_content = """# USER MANUAL

## 1. INTRODUCTION
### 1.1 Purpose
{{ purpose }}

### 1.2 Target Audience
{{ target_audience }}

### 1.3 System Overview
{{ system_overview }}

## 2. GETTING STARTED
### 2.1 Prerequisites
{% for prerequisite in prerequisites %}
- {{ prerequisite }}
{% endfor %}

### 2.2 Installation
{{ installation_steps }}

### 2.3 First Login
{{ first_login }}

## 3. USER INTERFACE
### 3.1 Main Dashboard
{{ main_dashboard }}

### 3.2 Navigation
{{ navigation }}

### 3.3 Menu Structure
{% for menu in menu_structure %}
#### {{ menu.name }}
{% for item in menu.items %}
- **{{ item.name }}**: {{ item.description }}
{% endfor %}
{% endfor %}

## 4. FEATURES AND FUNCTIONS
{% for feature in features %}
### 4.{{ loop.index }} {{ feature.name }}
**Description**: {{ feature.description }}

**How to Use:**
{% for step in feature.steps %}
{{ loop.index }}. {{ step }}
{% endfor %}

**Screenshots:**
{% for screenshot in feature.screenshots %}
![{{ screenshot.caption }}]({{ screenshot.url }})
{% endfor %}
{% endfor %}

## 5. TROUBLESHOOTING
### 5.1 Common Issues
{% for issue in common_issues %}
#### {{ issue.title }}
**Problem**: {{ issue.problem }}  
**Solution**: {{ issue.solution }}  
**Prevention**: {{ issue.prevention }}
{% endfor %}

### 5.2 Error Messages
{% for error in error_messages %}
- **{{ error.code }}**: {{ error.message }} - {{ error.solution }}
{% endfor %}

## 6. FAQ
{% for faq in faqs %}
### {{ faq.question }}
{{ faq.answer }}
{% endfor %}

---
**Document Version**: {{ version }}  
**Last Updated**: {{ last_updated }}  
**Prepared By**: {{ prepared_by }}
"""
        
        self.save_template("UserManual", "default", template_content)
    
    def create_default_api_template(self):
        """Create default API documentation template"""
        template_content = """# API DOCUMENTATION

## 1. OVERVIEW
### 1.1 API Description
{{ api_description }}

### 1.2 Base URL
{{ base_url }}

### 1.3 Authentication
{{ authentication }}

## 2. ENDPOINTS
{% for endpoint in endpoints %}
### 2.{{ loop.index }} {{ endpoint.name }}
**URL**: {{ endpoint.url }}  
**Method**: {{ endpoint.method }}  
**Description**: {{ endpoint.description }}

**Parameters:**
{% for param in endpoint.parameters %}
- `{{ param.name }}` ({{ param.type }}) - {{ param.description }} {% if param.required %}[Required]{% endif %}
{% endfor %}

**Request Example:**
```{{ endpoint.request_format }}
{{ endpoint.request_example }}
```

**Response:**
```{{ endpoint.response_format }}
{{ endpoint.response_example }}
```

**Error Codes:**
{% for error in endpoint.errors %}
- `{{ error.code }}`: {{ error.message }}
{% endfor %}
{% endfor %}

## 3. DATA MODELS
{% for model in data_models %}
### 3.{{ loop.index }} {{ model.name }}
```json
{{ model.schema }}
```

**Fields:**
{% for field in model.fields %}
- **{{ field.name }}** ({{ field.type }}) - {{ field.description }} {% if field.required %}[Required]{% endif %}
{% endfor %}
{% endfor %}

## 4. AUTHENTICATION
### 4.1 API Keys
{{ api_keys }}

### 4.2 OAuth 2.0
{{ oauth }}

## 5. RATE LIMITING
{{ rate_limiting }}

## 6. ERROR HANDLING
### 6.1 Error Response Format
```json
{{ error_response_format }}
```

### 6.2 Common Error Codes
{% for error in common_errors %}
- **{{ error.code }}**: {{ error.message }} - {{ error.solution }}
{% endfor %}

## 7. SDK EXAMPLES
{% for sdk in sdks %}
### 7.{{ loop.index }} {{ sdk.language }}
```{{ sdk.language }}
{{ sdk.example }}
```
{% endfor %}

---
**API Version**: {{ version }}  
**Last Updated**: {{ last_updated }}  
**Prepared By**: {{ prepared_by }}
"""
        
        self.save_template("API", "default", template_content)
    
    def save_template(self, category: str, name: str, content: str) -> bool:
        """Save a template to file"""
        try:
            template_file = self.templates_dir / f"{category}_{name}.jinja2"
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving template: {e}")
            return False
    
    def load_template(self, category: str, name: str) -> Optional[str]:
        """Load a template from file"""
        try:
            template_file = self.templates_dir / f"{category}_{name}.jinja2"
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Error loading template: {e}")
            return None
    
    def list_templates(self, category: str = None) -> List[Dict[str, Any]]:
        """List available templates"""
        templates = []
        
        for template_file in self.templates_dir.glob("*.jinja2"):
            if category and not template_file.name.startswith(category):
                continue
            
            # Parse template name
            parts = template_file.stem.split('_', 1)
            if len(parts) == 2:
                template_category, template_name = parts
                templates.append({
                    "category": template_category,
                    "name": template_name,
                    "file_path": str(template_file),
                    "last_modified": datetime.fromtimestamp(template_file.stat().st_mtime)
                })
        
        return templates
    
    def render_template(self, category: str, name: str, data: Dict[str, Any]) -> Optional[str]:
        """Render a template with data"""
        try:
            template_content = self.load_template(category, name)
            if not template_content:
                return None
            
            template = Template(template_content)
            return template.render(**data)
        except Exception as e:
            print(f"Error rendering template: {e}")
            return None
    
    def create_custom_template(self, category: str, name: str, content: str, description: str = "") -> bool:
        """Create a custom template"""
        try:
            # Validate template syntax
            Template(content)
            
            # Save template
            success = self.save_template(category, name, content)
            
            if success:
                # Save metadata
                metadata = {
                    "category": category,
                    "name": name,
                    "description": description,
                    "created": datetime.now().isoformat(),
                    "custom": True
                }
                
                metadata_file = self.templates_dir / f"{category}_{name}_metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
            
            return success
        except Exception as e:
            print(f"Error creating custom template: {e}")
            return False
    
    def delete_template(self, category: str, name: str) -> bool:
        """Delete a template"""
        try:
            template_file = self.templates_dir / f"{category}_{name}.jinja2"
            metadata_file = self.templates_dir / f"{category}_{name}_metadata.json"
            
            if template_file.exists():
                template_file.unlink()
            
            if metadata_file.exists():
                metadata_file.unlink()
            
            return True
        except Exception as e:
            print(f"Error deleting template: {e}")
            return False
    
    def get_template_metadata(self, category: str, name: str) -> Optional[Dict[str, Any]]:
        """Get template metadata"""
        try:
            metadata_file = self.templates_dir / f"{category}_{name}_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading template metadata: {e}")
            return None
    
    def apply_template_to_analysis(self, analysis_id: str, template_category: str, template_name: str) -> Dict[str, Any]:
        """Apply a template to an existing analysis"""
        db = get_db()
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                return {"error": "Analysis not found"}
            
            # Parse analysis results
            results = analysis.results
            
            # Prepare template data
            template_data = self._prepare_template_data(results, analysis)
            
            # Render template
            rendered_content = self.render_template(template_category, template_name, template_data)
            
            if rendered_content:
                return {
                    "success": True,
                    "content": rendered_content,
                    "template_category": template_category,
                    "template_name": template_name
                }
            else:
                return {"error": "Failed to render template"}
                
        except Exception as e:
            return {"error": f"Template application failed: {str(e)}"}
        finally:
            db.close()
    
    def _prepare_template_data(self, results: Dict, analysis: Analysis) -> Dict[str, Any]:
        """Prepare data for template rendering"""
        data = {
            "project_name": analysis.title or "Project",
            "version": "1.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "prepared_by": "BA Agent",
            "approved_by": "TBD",
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add results-specific data
        if 'trd' in results:
            data.update(self._extract_trd_data(results['trd']))
        
        if 'backlog' in results:
            try:
                backlog_data = json.loads(results['backlog'])
                data.update(self._extract_backlog_data(backlog_data))
            except:
                pass
        
        return data
    
    def _extract_trd_data(self, trd_content: str) -> Dict[str, Any]:
        """Extract structured data from TRD content"""
        # This is a simplified extraction - in practice, you'd use more sophisticated parsing
        data = {
            "project_overview": "Project overview extracted from TRD",
            "key_objectives": ["Objective 1", "Objective 2"],
            "success_criteria": ["Criterion 1", "Criterion 2"],
            "high_level_architecture": "Architecture description",
            "system_components": [
                {"name": "Component 1", "description": "Description 1"},
                {"name": "Component 2", "description": "Description 2"}
            ],
            "technology_stack": [
                {"category": "Frontend", "technologies": ["React", "TypeScript"]},
                {"category": "Backend", "technologies": ["Python", "Flask"]}
            ],
            "user_stories": [
                {
                    "title": "User Story 1",
                    "actor": "User",
                    "action": "perform action",
                    "benefit": "achieve benefit",
                    "acceptance_criteria": ["Criterion 1", "Criterion 2"],
                    "priority": "High",
                    "effort": 5
                }
            ],
            "business_rules": [
                {"name": "Rule 1", "description": "Description 1"},
                {"name": "Rule 2", "description": "Description 2"}
            ],
            "performance": {
                "response_time": "< 2 seconds",
                "throughput": "1000 requests/second",
                "scalability": "Horizontal scaling"
            },
            "security_requirements": [
                "Authentication required",
                "Data encryption in transit"
            ],
            "availability": {
                "uptime": "99.9%",
                "recovery_time": "< 4 hours"
            },
            "api_specifications": [
                {
                    "name": "API 1",
                    "endpoint": "/api/v1/resource",
                    "method": "GET",
                    "parameters": ["param1", "param2"],
                    "response": '{"status": "success"}',
                    "errors": [
                        {"code": 400, "message": "Bad Request"},
                        {"code": 404, "message": "Not Found"}
                    ]
                }
            ],
            "database_tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "INTEGER", "constraints": ["PRIMARY KEY"], "description": "User ID"},
                        {"name": "name", "type": "VARCHAR(255)", "constraints": ["NOT NULL"], "description": "User name"}
                    ],
                    "indexes": ["idx_users_email"]
                }
            ],
            "security": {
                "authentication": "OAuth 2.0 with JWT tokens",
                "data_protection": "AES-256 encryption"
            },
            "compliance_requirements": [
                "GDPR compliance",
                "SOC 2 Type II"
            ],
            "deployment": {
                "infrastructure": "Cloud-native deployment",
                "strategy": "Blue-green deployment",
                "monitoring": "Comprehensive logging and monitoring"
            },
            "test_types": [
                {"name": "Unit Tests", "description": "Component-level testing"},
                {"name": "Integration Tests", "description": "System integration testing"}
            ],
            "quality_assurance": "Automated testing with 90% code coverage",
            "acceptance_criteria": [
                "All functional requirements met",
                "Performance benchmarks achieved"
            ]
        }
        
        return data
    
    def _extract_backlog_data(self, backlog_data: Dict) -> Dict[str, Any]:
        """Extract structured data from backlog"""
        data = {
            "epics": [],
            "statistics": {
                "total_epics": 0,
                "total_features": 0,
                "total_stories": 0,
                "total_story_points": 0,
                "avg_story_points": 0
            },
            "priority_breakdown": []
        }
        
        if 'backlog' in backlog_data:
            epics = backlog_data['backlog']
            data["epics"] = epics
            
            # Calculate statistics
            total_epics = len(epics)
            total_features = 0
            total_stories = 0
            total_story_points = 0
            
            for epic in epics:
                for feature in epic.get('children', []):
                    total_features += 1
                    for story in feature.get('children', []):
                        total_stories += 1
                        effort = story.get('effort', 0)
                        if isinstance(effort, str) and effort.isdigit():
                            total_story_points += int(effort)
                        elif isinstance(effort, int):
                            total_story_points += effort
            
            data["statistics"] = {
                "total_epics": total_epics,
                "total_features": total_features,
                "total_stories": total_stories,
                "total_story_points": total_story_points,
                "avg_story_points": total_story_points / total_stories if total_stories > 0 else 0
            }
        
        return data

# Global instance
template_manager = TemplateManager()
