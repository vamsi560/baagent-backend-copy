# document_generation_engine.py
# Specialized Document Generation Engine for HLD, LLD, and Backlog

from typing import Dict, List, Any, Optional
from pc_insurance_knowledge import PCPromptEngine
from custom_llm import CustomLLMEngine

class DocumentGenerationEngine:
    def __init__(self):
        self.pc_engine = PCPromptEngine()
        self.llm_engine = CustomLLMEngine()
        
        # Document templates with specific focus on input-based generation
        self.hld_template = self._create_hld_template()
        self.lld_template = self._create_lld_template()
        self.backlog_template = self._create_backlog_template()
    
    def _create_hld_template(self) -> str:
        """Create HLD template that focuses on input-specific content"""
        return """
        **HIGH-LEVEL DESIGN DOCUMENT**
        
        **IMPORTANT**: This document MUST be based EXCLUSIVELY on the provided input requirements. Do NOT include generic content or default sections that are not relevant to the specific project.
        
        **INPUT ANALYSIS**:
        {input_analysis}
        
        **PROJECT CONTEXT**:
        - Project Name: {project_name}
        - Business Domain: {business_domain}
        - Key Requirements: {key_requirements}
        - Technical Constraints: {technical_constraints}
        
        **SYSTEM ARCHITECTURE**:
        Based on the specific requirements above, design the system architecture:
        
        1. **System Overview**:
           - Architecture Pattern: [Based on requirements]
           - Technology Stack: [Specific to project needs]
           - Integration Points: [Only those mentioned in requirements]
        
        2. **Component Design**:
           - Core Components: [Only those required by the project]
           - Data Flow: [Based on specific business processes]
           - External Dependencies: [Only those mentioned in requirements]
        
        3. **Security & Compliance**:
           - Security Requirements: [Based on specific compliance needs]
           - Data Protection: [Specific to the business domain]
        
        4. **Scalability & Performance**:
           - Performance Requirements: [Based on specific metrics]
           - Scalability Strategy: [Tailored to project needs]
        
        **CRITICAL REQUIREMENTS**:
        - Every section must reference specific requirements from the input
        - No generic content or default sections
        - All technical decisions must be justified by the input requirements
        - Architecture must be specifically designed for this project
        """
    
    def _create_lld_template(self) -> str:
        """Create LLD template that focuses on input-specific content"""
        return """
        **LOW-LEVEL DESIGN DOCUMENT**
        
        **IMPORTANT**: This document MUST be based EXCLUSIVELY on the provided input requirements and HLD. Do NOT include generic content or default implementations.
        
        **INPUT ANALYSIS**:
        {input_analysis}
        
        **HLD REFERENCE**:
        {hld_reference}
        
        **DETAILED DESIGN**:
        Based on the specific requirements above, provide detailed design:
        
        1. **Database Design**:
           - Schema Design: [Based on specific data requirements]
           - Relationships: [Only those needed for the project]
           - Indexing Strategy: [Based on specific query patterns]
        
        2. **API Design**:
           - Endpoints: [Only those required by the project]
           - Request/Response Models: [Based on specific business needs]
           - Authentication: [Based on specific security requirements]
        
        3. **Component Implementation**:
           - Class Diagrams: [Only for components mentioned in requirements]
           - Method Signatures: [Based on specific functionality]
           - Error Handling: [Based on specific business rules]
        
        4. **Integration Design**:
           - External APIs: [Only those mentioned in requirements]
           - Data Transformation: [Based on specific data formats]
           - Error Handling: [Based on specific integration needs]
        
        **CRITICAL REQUIREMENTS**:
        - Every design decision must be justified by the input requirements
        - No generic implementations or default patterns
        - All components must serve specific business needs
        - Design must be implementable based on the provided constraints
        """
    
    def _create_backlog_template(self) -> str:
        """Create Backlog template that focuses on input-specific content"""
        return """
        **PROJECT BACKLOG**
        
        **IMPORTANT**: This backlog MUST be based EXCLUSIVELY on the provided input requirements. Do NOT include generic user stories or default features.
        
        **INPUT ANALYSIS**:
        {input_analysis}
        
        **PROJECT SCOPE**:
        - Project Name: {project_name}
        - Business Objectives: {business_objectives}
        - Key Features: {key_features}
        - Success Criteria: {success_criteria}
        
        **USER STORIES & TASKS**:
        Based on the specific requirements above, create detailed backlog items:
        
        1. **Epics** (High-level features):
           - Epic 1: [Based on specific business requirement]
           - Epic 2: [Based on specific business requirement]
           - Epic 3: [Based on specific business requirement]
        
        2. **User Stories** (Detailed requirements):
           - Story 1: [Specific to the project requirements]
           - Story 2: [Specific to the project requirements]
           - Story 3: [Specific to the project requirements]
        
        3. **Technical Tasks**:
           - Task 1: [Based on specific technical requirement]
           - Task 2: [Based on specific technical requirement]
           - Task 3: [Based on specific technical requirement]
        
        4. **Acceptance Criteria**:
           - Criteria 1: [Based on specific business rule]
           - Criteria 2: [Based on specific business rule]
           - Criteria 3: [Based on specific business rule]
        
        **CRITICAL REQUIREMENTS**:
        - Every backlog item must be derived from the input requirements
        - No generic user stories or default features
        - All stories must serve specific business objectives
        - Acceptance criteria must be measurable and specific
        """
    
    def analyze_input(self, input_text: str) -> Dict[str, Any]:
        """Analyze input to extract key information for document generation"""
        analysis = {
            "project_name": "",
            "business_domain": "",
            "key_requirements": [],
            "technical_constraints": [],
            "business_objectives": [],
            "key_features": [],
            "success_criteria": [],
            "lob_classification": "",
            "specific_requirements": []
        }
        
        # Classify LOB
        analysis["lob_classification"] = self.pc_engine.classify_lob(input_text)
        
        # Extract project information
        lines = input_text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                # Extract project name
                if any(keyword in line.lower() for keyword in ['project', 'system', 'application']):
                    if not analysis["project_name"]:
                        analysis["project_name"] = line
                
                # Extract requirements
                if line.startswith('-') or line.startswith('•'):
                    requirement = line[1:].strip()
                    if requirement:
                        analysis["key_requirements"].append(requirement)
                
                # Extract technical constraints
                if any(keyword in line.lower() for keyword in ['technology', 'framework', 'database', 'api', 'cloud']):
                    analysis["technical_constraints"].append(line)
                
                # Extract business objectives
                if any(keyword in line.lower() for keyword in ['objective', 'goal', 'purpose', 'aim']):
                    analysis["business_objectives"].append(line)
                
                # Extract features
                if any(keyword in line.lower() for keyword in ['feature', 'functionality', 'capability']):
                    analysis["key_features"].append(line)
        
        # If no specific requirements found, use the entire input
        if not analysis["key_requirements"]:
            analysis["key_requirements"] = [input_text]
        
        return analysis
    
    def generate_hld(self, input_text: str, project_context: Dict[str, Any] = None) -> str:
        """Generate High-Level Design document based on specific input"""
        
        # Analyze input
        analysis = self.analyze_input(input_text)
        
        # Merge with project context if provided
        if project_context:
            analysis.update(project_context)
        
        # Create input-specific prompt
        prompt = self.hld_template.format(
            input_analysis=self._format_analysis(analysis),
            project_name=analysis.get("project_name", "Project"),
            business_domain=analysis.get("lob_classification", "P&C Insurance"),
            key_requirements="\n".join([f"- {req}" for req in analysis.get("key_requirements", [])]),
            technical_constraints="\n".join([f"- {constraint}" for constraint in analysis.get("technical_constraints", [])])
        )
        
        # Generate HLD
        response = self.llm_engine.generate_response(
            prompt=prompt,
            max_tokens=3000,
            use_fallback=True
        )
        
        return response
    
    def generate_lld(self, input_text: str, hld_content: str, project_context: Dict[str, Any] = None) -> str:
        """Generate Low-Level Design document based on specific input and HLD"""
        
        # Analyze input
        analysis = self.analyze_input(input_text)
        
        # Merge with project context if provided
        if project_context:
            analysis.update(project_context)
        
        # Create input-specific prompt
        prompt = self.lld_template.format(
            input_analysis=self._format_analysis(analysis),
            hld_reference=self._summarize_hld(hld_content)
        )
        
        # Generate LLD
        response = self.llm_engine.generate_response(
            prompt=prompt,
            max_tokens=3000,
            use_fallback=True
        )
        
        return response
    
    def generate_backlog(self, input_text: str, project_context: Dict[str, Any] = None) -> str:
        """Generate Project Backlog based on specific input"""
        
        # Analyze input
        analysis = self.analyze_input(input_text)
        
        # Merge with project context if provided
        if project_context:
            analysis.update(project_context)
        
        # Create input-specific prompt
        prompt = self.backlog_template.format(
            input_analysis=self._format_analysis(analysis),
            project_name=analysis.get("project_name", "Project"),
            business_objectives="\n".join([f"- {obj}" for obj in analysis.get("business_objectives", [])]),
            key_features="\n".join([f"- {feature}" for feature in analysis.get("key_features", [])]),
            success_criteria="\n".join([f"- {criteria}" for criteria in analysis.get("success_criteria", [])])
        )
        
        # Generate Backlog
        response = self.llm_engine.generate_response(
            prompt=prompt,
            max_tokens=3000,
            use_fallback=True
        )
        
        return response
    
    def _format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format analysis for inclusion in prompts"""
        formatted = f"""
        **Project Analysis Results:**
        
        **LOB Classification**: {analysis.get('lob_classification', 'Not specified')}
        **Project Name**: {analysis.get('project_name', 'Not specified')}
        
        **Key Requirements**:
        {chr(10).join([f"- {req}" for req in analysis.get('key_requirements', [])])}
        
        **Technical Constraints**:
        {chr(10).join([f"- {constraint}" for constraint in analysis.get('technical_constraints', [])])}
        
        **Business Objectives**:
        {chr(10).join([f"- {obj}" for obj in analysis.get('business_objectives', [])])}
        
        **Key Features**:
        {chr(10).join([f"- {feature}" for feature in analysis.get('key_features', [])])}
        """
        return formatted
    
    def _summarize_hld(self, hld_content: str) -> str:
        """Summarize HLD content for LLD reference"""
        # Extract key points from HLD
        lines = hld_content.split('\n')
        summary_points = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('**') and line.endswith('**'):
                summary_points.append(line)
            elif line.startswith('-') or line.startswith('•'):
                summary_points.append(line)
        
        return "\n".join(summary_points[:10])  # Limit to first 10 points
    
    def validate_document_quality(self, document: str, input_text: str) -> Dict[str, Any]:
        """Validate that the generated document is specific to the input"""
        
        # Check for generic/default content indicators
        generic_indicators = [
            "generic", "default", "example", "sample", "template",
            "typical", "standard", "common", "usual", "basic"
        ]
        
        # Check for input-specific content
        input_words = set(input_text.lower().split())
        document_words = set(document.lower().split())
        
        # Calculate specificity score
        input_specific_words = input_words.intersection(document_words)
        specificity_score = len(input_specific_words) / len(input_words) if input_words else 0
        
        # Check for generic content
        generic_content_found = any(indicator in document.lower() for indicator in generic_indicators)
        
        return {
            "specificity_score": specificity_score,
            "generic_content_found": generic_content_found,
            "input_specific_words": list(input_specific_words),
            "quality_score": specificity_score * (0.5 if generic_content_found else 1.0)
        }

# Test function
def test_document_generation():
    """Test the document generation engine"""
    print("🧪 Testing Document Generation Engine...")
    
    engine = DocumentGenerationEngine()
    
    # Test input
    test_input = """
    SOV AUTOMATION PROJECT:
    
    This project aims to streamline the underwriting process for Property's Middle Market submissions by automating the Statement of Values (SOV) ingestion and processing. It leverages Generative AI (GenAI) for initial submission classification and process automation.
    
    Key Requirements:
    - Automate identification of Middle Market submissions
    - Automate retrieval, cleansing, and ingestion of SOVs
    - Reduce manual effort in SOV scrubbing and CAT modeling processes
    - Improve data quality and consistency
    - Accelerate quoting process and increase quote volume
    
    System Components:
    - Operations Workbench/SMS (Existing): Modified to identify Middle Market submissions
    - AI Platform (GenAI): Classifies submissions as Middle Market or Shared & Layered
    - SOV Automation Framework: Core component for SOV processing
    - UW Workbench (Existing): Enhanced to display SOV data and modeling results
    - ImageRight (IR): Document management system for storing SOVs
    - PING API: Third-party service for SOV cleansing
    - Touchstone: CAT modeling service
    - Guidewire PolicyCenter (GWPC): Policy administration system
    
    Technology Stack:
    - Programming Languages: Java, Python (for AI Platform integration)
    - Database: PostgreSQL
    - API Technologies: RESTful APIs, JSON
    - Cloud Platform: AWS
    - Message Queue: Kafka
    - Operating System: Linux
    - Frameworks: Spring Boot, React (for UI)
    """
    
    # Test input analysis
    analysis = engine.analyze_input(test_input)
    print(f"✅ Input Analysis:")
    print(f"   LOB Classification: {analysis['lob_classification']}")
    print(f"   Key Requirements: {len(analysis['key_requirements'])} items")
    print(f"   Technical Constraints: {len(analysis['technical_constraints'])} items")
    
    # Test HLD generation
    print(f"\n📄 Generating HLD...")
    hld_content = engine.generate_hld(test_input)
    print(f"✅ HLD Generated: {len(hld_content)} characters")
    
    # Test LLD generation
    print(f"\n🔧 Generating LLD...")
    lld_content = engine.generate_lld(test_input, hld_content)
    print(f"✅ LLD Generated: {len(lld_content)} characters")
    
    # Test Backlog generation
    print(f"\n📋 Generating Backlog...")
    backlog_content = engine.generate_backlog(test_input)
    print(f"✅ Backlog Generated: {len(backlog_content)} characters")
    
    # Validate document quality
    print(f"\n📊 Validating Document Quality...")
    hld_quality = engine.validate_document_quality(hld_content, test_input)
    lld_quality = engine.validate_document_quality(lld_content, test_input)
    backlog_quality = engine.validate_document_quality(backlog_content, test_input)
    
    print(f"   HLD Quality Score: {hld_quality['quality_score']:.2f}")
    print(f"   LLD Quality Score: {lld_quality['quality_score']:.2f}")
    print(f"   Backlog Quality Score: {backlog_quality['quality_score']:.2f}")
    
    return {
        "analysis": analysis,
        "hld_content": hld_content,
        "lld_content": lld_content,
        "backlog_content": backlog_content,
        "quality_scores": {
            "hld": hld_quality['quality_score'],
            "lld": lld_quality['quality_score'],
            "backlog": backlog_quality['quality_score']
        }
    }

if __name__ == "__main__":
    test_document_generation()
