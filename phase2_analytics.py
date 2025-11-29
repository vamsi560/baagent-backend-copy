"""
Phase 2 Analytics Module for BA Agent

This module provides advanced analytics capabilities:
- Bulk Document Upload with parallel processing
- Dependency Mapping with visual requirement relationships
- Gantt Chart generation with project timelines
- 3D Architecture Visualization with interactive components
"""

import os
import asyncio
import concurrent.futures
import time
import json
import uuid
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed

# Analytics and visualization libraries
import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# LangChain for enhanced processing
from langchain_integration import langchain_agent
from main import (
    call_generative_agent, agent_extract_content, agent_planner, 
    agent_trd_writer, agent_diagrammer, agent_backlog_creator,
    extract_mermaid_code, add_ids_to_backlog
)

# phase2_analytics.py
# Advanced Analytics and Business Intelligence Module

import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# LangChain imports
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
# Using Pinecone for vector storage
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Custom imports
from database import get_db, Document, Analysis, embedding_model, PINECONE_ENABLED, search_vector_db
from langchain_integration import langchain_integration

class AdvancedAnalytics:
    """Advanced analytics and business intelligence for the BA Agent"""
    
    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.setup_components()
    
    def setup_components(self):
        """Initialize analytics components"""
        try:
            if embedding_model:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'}
                )
            
            if PINECONE_ENABLED:
                # Pinecone is used via custom database functions
                self.vector_store_enabled = True
            else:
                self.vector_store_enabled = False
            
            print("✅ Advanced Analytics components initialized")
            
        except Exception as e:
            print(f"⚠️ Analytics setup warning: {e}")
    
    def generate_project_insights(self, analysis_id: str) -> Dict[str, Any]:
        """Generate comprehensive project insights from analysis"""
        
        db = get_db()
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                return {"error": "Analysis not found"}
            
            results = analysis.results
            original_text = analysis.original_text
            
            insights = {
                "project_overview": self._analyze_project_overview(results, original_text),
                "complexity_analysis": self._analyze_complexity(results),
                "risk_assessment": self._assess_risks(results, original_text),
                "effort_estimation": self._estimate_effort(results),
                "technology_recommendations": self._recommend_technologies(results),
                "timeline_analysis": self._analyze_timeline(results),
                "resource_requirements": self._analyze_resources(results),
                "quality_metrics": self._calculate_quality_metrics(results),
                "trends_and_patterns": self._identify_trends(results),
                "comparative_analysis": self._compare_with_similar_projects(results)
            }
            
            return insights
            
        except Exception as e:
            return {"error": f"Failed to generate insights: {str(e)}"}
        finally:
            db.close()
    
    def _analyze_project_overview(self, results: Dict, original_text: str) -> Dict[str, Any]:
        """Analyze project overview and key metrics"""
        
        overview = {
            "total_requirements": 0,
            "functional_requirements": 0,
            "non_functional_requirements": 0,
            "user_stories": 0,
            "epics": 0,
            "features": 0,
            "estimated_story_points": 0,
            "complexity_level": "Medium",
            "project_scope": "Standard",
            "key_technologies": [],
            "integration_points": 0
        }
        
        # Analyze TRD
        if 'trd' in results:
            trd_content = results['trd']
            overview["total_requirements"] = trd_content.count("requirement") + trd_content.count("Requirement")
            overview["functional_requirements"] = trd_content.count("functional") + trd_content.count("Functional")
            overview["non_functional_requirements"] = trd_content.count("non-functional") + trd_content.count("Non-functional")
        
        # Analyze backlog
        if 'backlog' in results:
            try:
                backlog_data = json.loads(results['backlog'])
                overview["user_stories"] = self._count_backlog_items(backlog_data, "User Story")
                overview["epics"] = self._count_backlog_items(backlog_data, "Epic")
                overview["features"] = self._count_backlog_items(backlog_data, "Feature")
                overview["estimated_story_points"] = self._calculate_total_story_points(backlog_data)
            except:
                pass
        
        # Determine complexity level
        total_items = overview["user_stories"] + overview["features"] + overview["epics"]
        if total_items > 50:
            overview["complexity_level"] = "High"
        elif total_items < 20:
            overview["complexity_level"] = "Low"
        
        return overview
    
    def _analyze_complexity(self, results: Dict) -> Dict[str, Any]:
        """Analyze project complexity factors"""
        
        complexity = {
            "technical_complexity": "Medium",
            "business_complexity": "Medium",
            "integration_complexity": "Medium",
            "data_complexity": "Medium",
            "security_complexity": "Medium",
            "overall_complexity_score": 0,
            "complexity_factors": []
        }
        
        # Analyze technical complexity
        if 'hld' in results:
            hld_content = results['hld'].lower()
            if any(tech in hld_content for tech in ['microservices', 'distributed', 'cloud-native']):
                complexity["technical_complexity"] = "High"
            elif any(tech in hld_content for tech in ['monolithic', 'simple', 'basic']):
                complexity["technical_complexity"] = "Low"
        
        # Analyze business complexity
        if 'trd' in results:
            trd_content = results['trd'].lower()
            if any(term in trd_content for term in ['compliance', 'regulatory', 'audit', 'governance']):
                complexity["business_complexity"] = "High"
            elif any(term in trd_content for term in ['simple', 'basic', 'standard']):
                complexity["business_complexity"] = "Low"
        
        # Calculate overall complexity score
        complexity_levels = {
            "Low": 1,
            "Medium": 2,
            "High": 3
        }
        
        complexity["overall_complexity_score"] = sum([
            complexity_levels[complexity["technical_complexity"]],
            complexity_levels[complexity["business_complexity"]],
            complexity_levels[complexity["integration_complexity"]],
            complexity_levels[complexity["data_complexity"]],
            complexity_levels[complexity["security_complexity"]]
        ]) / 5
        
        return complexity
    
    def _assess_risks(self, results: Dict, original_text: str) -> Dict[str, Any]:
        """Assess project risks and mitigation strategies"""
        
        risks = {
            "high_risks": [],
            "medium_risks": [],
            "low_risks": [],
            "risk_score": 0,
            "mitigation_strategies": []
        }
        
        # Analyze technical risks
        if 'hld' in results:
            hld_content = results['hld'].lower()
            if 'integration' in hld_content and 'external' in hld_content:
                risks["high_risks"].append({
                    "category": "Technical",
                    "risk": "External Integration Complexity",
                    "description": "Multiple external system integrations increase technical risk",
                    "probability": "High",
                    "impact": "High"
                })
        
        # Analyze business risks
        if 'trd' in results:
            trd_content = results['trd'].lower()
            if 'compliance' in trd_content:
                risks["high_risks"].append({
                    "category": "Business",
                    "risk": "Compliance Requirements",
                    "description": "Regulatory compliance requirements increase project risk",
                    "probability": "Medium",
                    "impact": "High"
                })
        
        # Calculate risk score
        risk_weights = {"High": 3, "Medium": 2, "Low": 1}
        total_risk_score = 0
        total_risks = 0
        
        for risk_level in ["high_risks", "medium_risks", "low_risks"]:
            for risk in risks[risk_level]:
                total_risk_score += risk_weights[risk["probability"]] * risk_weights[risk["impact"]]
                total_risks += 1
        
        if total_risks > 0:
            risks["risk_score"] = total_risk_score / total_risks
        
        return risks
    
    def _estimate_effort(self, results: Dict) -> Dict[str, Any]:
        """Estimate project effort and timeline"""
        
        effort = {
            "total_story_points": 0,
            "estimated_weeks": 0,
            "team_size_recommendation": "3-5 developers",
            "effort_breakdown": {
                "development": 0,
                "testing": 0,
                "documentation": 0,
                "deployment": 0
            },
            "critical_path_items": []
        }
        
        # Calculate story points from backlog
        if 'backlog' in results:
            try:
                backlog_data = json.loads(results['backlog'])
                effort["total_story_points"] = self._calculate_total_story_points(backlog_data)
                
                # Estimate weeks (assuming 1 story point = 1 day, 5 days per week)
                effort["estimated_weeks"] = max(1, effort["total_story_points"] // 5)
                
                # Adjust team size based on timeline
                if effort["estimated_weeks"] > 20:
                    effort["team_size_recommendation"] = "5-8 developers"
                elif effort["estimated_weeks"] < 8:
                    effort["team_size_recommendation"] = "2-3 developers"
                
                # Effort breakdown
                effort["effort_breakdown"]["development"] = effort["total_story_points"] * 0.6
                effort["effort_breakdown"]["testing"] = effort["total_story_points"] * 0.2
                effort["effort_breakdown"]["documentation"] = effort["total_story_points"] * 0.1
                effort["effort_breakdown"]["deployment"] = effort["total_story_points"] * 0.1
                
            except:
                pass
        
        return effort
    
    def _recommend_technologies(self, results: Dict) -> Dict[str, Any]:
        """Recommend technology stack based on requirements"""
        
        recommendations = {
            "frontend": [],
            "backend": [],
            "database": [],
            "cloud": [],
            "devops": [],
            "reasoning": []
        }
        
        # Analyze requirements for technology recommendations
        if 'trd' in results:
            trd_content = results['trd'].lower()
            
            # Frontend recommendations
            if 'mobile' in trd_content:
                recommendations["frontend"].append("React Native")
                recommendations["reasoning"].append("Mobile app requirement detected")
            elif 'web' in trd_content:
                recommendations["frontend"].append("React.js")
                recommendations["reasoning"].append("Web application requirement")
            
            # Backend recommendations
            if 'microservices' in trd_content:
                recommendations["backend"].append("Node.js/Express")
                recommendations["backend"].append("Spring Boot")
                recommendations["reasoning"].append("Microservices architecture detected")
            else:
                recommendations["backend"].append("Python/Flask")
                recommendations["reasoning"].append("Standard web application")
            
            # Database recommendations
            if 'real-time' in trd_content or 'streaming' in trd_content:
                recommendations["database"].append("MongoDB")
                recommendations["database"].append("Redis")
                recommendations["reasoning"].append("Real-time data requirements")
            else:
                recommendations["database"].append("PostgreSQL")
                recommendations["reasoning"].append("Relational data requirements")
        
        return recommendations
    
    def _analyze_timeline(self, results: Dict) -> Dict[str, Any]:
        """Analyze project timeline and milestones"""
        
        timeline = {
            "phases": [],
            "milestones": [],
            "dependencies": [],
            "critical_path": [],
            "buffer_time": 0
        }
        
        # Create phases based on backlog
        if 'backlog' in results:
            try:
                backlog_data = json.loads(results['backlog'])
                
                # Define phases
                phases = [
                    {"name": "Planning & Design", "duration": "2-3 weeks"},
                    {"name": "Development Phase 1", "duration": "4-6 weeks"},
                    {"name": "Development Phase 2", "duration": "4-6 weeks"},
                    {"name": "Testing & QA", "duration": "2-3 weeks"},
                    {"name": "Deployment", "duration": "1-2 weeks"}
                ]
                
                timeline["phases"] = phases
                
                # Add milestones
                timeline["milestones"] = [
                    {"name": "Requirements Finalized", "week": 1},
                    {"name": "Design Approved", "week": 3},
                    {"name": "Phase 1 Complete", "week": 9},
                    {"name": "Phase 2 Complete", "week": 15},
                    {"name": "Testing Complete", "week": 18},
                    {"name": "Production Ready", "week": 20}
                ]
                
            except:
                pass
        
        return timeline
    
    def _analyze_resources(self, results: Dict) -> Dict[str, Any]:
        """Analyze resource requirements"""
        
        resources = {
            "team_roles": [],
            "skill_requirements": [],
            "external_dependencies": [],
            "budget_estimate": 0,
            "resource_availability": "High"
        }
        
        # Determine team roles based on requirements
        if 'trd' in results:
            trd_content = results['trd'].lower()
            
            resources["team_roles"] = [
                "Project Manager",
                "Business Analyst",
                "Frontend Developer",
                "Backend Developer",
                "DevOps Engineer",
                "QA Engineer"
            ]
            
            if 'ui/ux' in trd_content or 'design' in trd_content:
                resources["team_roles"].append("UI/UX Designer")
            
            if 'data' in trd_content or 'analytics' in trd_content:
                resources["team_roles"].append("Data Engineer")
        
        # Estimate budget (rough calculation)
        team_size = len(resources["team_roles"])
        estimated_weeks = 20  # Default
        if 'backlog' in results:
            try:
                backlog_data = json.loads(results['backlog'])
                story_points = self._calculate_total_story_points(backlog_data)
                estimated_weeks = max(1, story_points // 5)
            except:
                pass
        
        # Rough budget calculation ($1000 per person per week)
        resources["budget_estimate"] = team_size * estimated_weeks * 1000
        
        return resources
    
    def _calculate_quality_metrics(self, results: Dict) -> Dict[str, Any]:
        """Calculate quality metrics for the project"""
        
        metrics = {
            "requirements_completeness": 0.8,
            "technical_feasibility": 0.9,
            "business_alignment": 0.85,
            "risk_mitigation": 0.75,
            "overall_quality_score": 0,
            "quality_improvements": []
        }
        
        # Calculate completeness based on document coverage
        if all(key in results for key in ['trd', 'hld', 'lld', 'backlog']):
            metrics["requirements_completeness"] = 0.9
        elif len(results) >= 3:
            metrics["requirements_completeness"] = 0.7
        else:
            metrics["requirements_completeness"] = 0.5
        
        # Calculate overall quality score
        metrics["overall_quality_score"] = sum([
            metrics["requirements_completeness"],
            metrics["technical_feasibility"],
            metrics["business_alignment"],
            metrics["risk_mitigation"]
        ]) / 4
        
        # Suggest improvements
        if metrics["requirements_completeness"] < 0.8:
            metrics["quality_improvements"].append("Add missing requirement specifications")
        
        if metrics["risk_mitigation"] < 0.8:
            metrics["quality_improvements"].append("Enhance risk mitigation strategies")
        
        return metrics
    
    def _identify_trends(self, results: Dict) -> Dict[str, Any]:
        """Identify trends and patterns in requirements"""
        
        trends = {
            "technology_trends": [],
            "business_trends": [],
            "architecture_patterns": [],
            "common_requirements": [],
            "emerging_patterns": []
        }
        
        # Analyze technology trends
        if 'hld' in results:
            hld_content = results['hld'].lower()
            if 'cloud' in hld_content:
                trends["technology_trends"].append("Cloud-Native Architecture")
            if 'microservices' in hld_content:
                trends["technology_trends"].append("Microservices Pattern")
            if 'api' in hld_content:
                trends["technology_trends"].append("API-First Design")
        
        # Analyze business trends
        if 'trd' in results:
            trd_content = results['trd'].lower()
            if 'mobile' in trd_content:
                trends["business_trends"].append("Mobile-First Strategy")
            if 'analytics' in trd_content:
                trends["business_trends"].append("Data-Driven Decision Making")
            if 'automation' in trd_content:
                trends["business_trends"].append("Process Automation")
        
        return trends
    
    def _compare_with_similar_projects(self, results: Dict) -> Dict[str, Any]:
        """Compare current project with similar historical projects"""
        
        comparison = {
            "similarity_score": 0.75,
            "common_patterns": [],
            "differentiators": [],
            "lessons_learned": [],
            "best_practices": []
        }
        
        # This would typically involve querying a database of historical projects
        # For now, we'll provide generic insights
        
        comparison["common_patterns"] = [
            "User authentication and authorization",
            "Data validation and error handling",
            "API integration requirements",
            "Reporting and analytics features"
        ]
        
        comparison["differentiators"] = [
            "Unique business domain requirements",
            "Specific compliance needs",
            "Custom integration requirements"
        ]
        
        comparison["lessons_learned"] = [
            "Early stakeholder engagement is crucial",
            "Clear requirement documentation reduces rework",
            "Regular feedback loops improve quality"
        ]
        
        comparison["best_practices"] = [
            "Use iterative development approach",
            "Implement comprehensive testing strategy",
            "Plan for scalability from the beginning"
        ]
        
        return comparison
    
    def _count_backlog_items(self, backlog_data: Dict, item_type: str) -> int:
        """Count backlog items of specific type"""
        count = 0
        
        def count_items(items):
            nonlocal count
            for item in items:
                if item.get('type') == item_type:
                    count += 1
                if 'children' in item:
                    count_items(item['children'])
        
        if 'backlog' in backlog_data:
            count_items(backlog_data['backlog'])
        
        return count
    
    def _calculate_total_story_points(self, backlog_data: Dict) -> int:
        """Calculate total story points from backlog"""
        total_points = 0
        
        def sum_points(items):
            nonlocal total_points
            for item in items:
                effort = item.get('effort', '0')
                if isinstance(effort, str) and effort.isdigit():
                    total_points += int(effort)
                elif isinstance(effort, int):
                    total_points += effort
                if 'children' in item:
                    sum_points(item['children'])
        
        if 'backlog' in backlog_data:
            sum_points(backlog_data['backlog'])
        
        return total_points
    
    def generate_analytics_dashboard(self, analysis_id: str) -> Dict[str, Any]:
        """Generate comprehensive analytics dashboard"""
        
        insights = self.generate_project_insights(analysis_id)
        
        dashboard = {
            "insights": insights,
            "charts": self._generate_charts(insights),
            "recommendations": self._generate_recommendations(insights),
            "metrics": self._calculate_metrics(insights),
            "timeline": self._generate_timeline(insights)
        }
        
        return dashboard
    
    def _generate_charts(self, insights: Dict) -> Dict[str, Any]:
        """Generate chart data for dashboard"""
        
        charts = {
            "complexity_radar": {
                "labels": ["Technical", "Business", "Integration", "Data", "Security"],
                "data": [
                    insights.get("complexity_analysis", {}).get("technical_complexity", "Medium"),
                    insights.get("complexity_analysis", {}).get("business_complexity", "Medium"),
                    insights.get("complexity_analysis", {}).get("integration_complexity", "Medium"),
                    insights.get("complexity_analysis", {}).get("data_complexity", "Medium"),
                    insights.get("complexity_analysis", {}).get("security_complexity", "Medium")
                ]
            },
            "effort_distribution": {
                "labels": ["Development", "Testing", "Documentation", "Deployment"],
                "data": list(insights.get("effort_estimation", {}).get("effort_breakdown", {}).values())
            },
            "risk_matrix": {
                "high_risks": len(insights.get("risk_assessment", {}).get("high_risks", [])),
                "medium_risks": len(insights.get("risk_assessment", {}).get("medium_risks", [])),
                "low_risks": len(insights.get("risk_assessment", {}).get("low_risks", []))
            }
        }
        
        return charts
    
    def _generate_recommendations(self, insights: Dict) -> List[Dict]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Risk-based recommendations
        risk_score = insights.get("risk_assessment", {}).get("risk_score", 0)
        if risk_score > 6:
            recommendations.append({
                "category": "Risk Management",
                "priority": "High",
                "recommendation": "Implement comprehensive risk mitigation strategies",
                "action": "Create detailed risk management plan"
            })
        
        # Complexity-based recommendations
        complexity_score = insights.get("complexity_analysis", {}).get("overall_complexity_score", 0)
        if complexity_score > 2.5:
            recommendations.append({
                "category": "Project Management",
                "priority": "High",
                "recommendation": "Consider breaking down into smaller phases",
                "action": "Create phased delivery plan"
            })
        
        # Quality-based recommendations
        quality_score = insights.get("quality_metrics", {}).get("overall_quality_score", 0)
        if quality_score < 0.8:
            recommendations.append({
                "category": "Quality Assurance",
                "priority": "Medium",
                "recommendation": "Enhance requirement documentation",
                "action": "Review and improve TRD completeness"
            })
        
        return recommendations
    
    def _calculate_metrics(self, insights: Dict) -> Dict[str, Any]:
        """Calculate key performance metrics"""
        
        metrics = {
            "project_health_score": 0,
            "delivery_confidence": 0,
            "resource_efficiency": 0,
            "quality_index": 0
        }
        
        # Calculate project health score
        risk_score = insights.get("risk_assessment", {}).get("risk_score", 0)
        quality_score = insights.get("quality_metrics", {}).get("overall_quality_score", 0)
        complexity_score = insights.get("complexity_analysis", {}).get("overall_complexity_score", 0)
        
        metrics["project_health_score"] = (quality_score * 0.4 + (1 - risk_score/9) * 0.3 + (1 - complexity_score/3) * 0.3)
        metrics["delivery_confidence"] = min(1.0, quality_score * 0.6 + (1 - risk_score/9) * 0.4)
        metrics["resource_efficiency"] = 0.8  # Placeholder
        metrics["quality_index"] = quality_score
        
        return metrics
    
    def _generate_timeline(self, insights: Dict) -> Dict[str, Any]:
        """Generate project timeline visualization"""
        
        timeline = insights.get("timeline_analysis", {})
        
        return {
            "phases": timeline.get("phases", []),
            "milestones": timeline.get("milestones", []),
            "critical_path": timeline.get("critical_path", []),
            "dependencies": timeline.get("dependencies", [])
        }

# Global instance
advanced_analytics = AdvancedAnalytics()
