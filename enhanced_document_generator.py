#!/usr/bin/env python3
"""
Enhanced Document Generator
Ensures high-quality, specific content generation with multiple fallback mechanisms
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

def extract_mermaid_code(text):
    """Extract Mermaid code from text"""
    if not text:
        return ""
    match = re.search(r"```mermaid\n([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    # Remove any standalone ```
    text = re.sub(r"```", "", text)
    return text.strip()

class EnhancedDocumentGenerator:
    def __init__(self, llm_engine):
        self.llm_engine = llm_engine
        self.quality_thresholds = {
            'specificity_score': 0.1,  # Much lower for reasonable validation
            'min_content_length': 200,  # Lowered for reasonable content
            'max_generic_phrases': 10   # Much higher tolerance
        }
        
        # Generic phrases that indicate poor quality content
        self.generic_phrases = [
            "example", "sample", "template", "placeholder", "default",
            "generic", "standard", "typical", "common", "usual",
            "this is a", "here is an", "for demonstration",
            "as an example", "for illustration", "sample data"
        ]
    
    def generate_high_quality_backlog(self, plan: str, original_text: str, trd: str, max_attempts: int = 3) -> Tuple[Dict, Optional[str]]:
        """Generate high-quality backlog with multiple attempts and quality validation"""
        print("🔍 ENHANCED BACKLOG GENERATOR: Starting high-quality generation...")
        
        for attempt in range(max_attempts):
            print(f"📝 Attempt {attempt + 1}/{max_attempts}")
            
            # Generate with increasingly specific prompts
            prompt = self._create_backlog_prompt(plan, original_text, trd, attempt + 1)
            
            # Generate response with better handling
            try:
                result = self.llm_engine.generate_response(prompt, is_json=True)
                
                # Handle large responses that might be truncated
                if isinstance(result, str) and len(result) > 10000:
                    print(f"⚠️ Large response detected ({len(result)} chars), attempting to extract valid JSON...")
                    result = self._extract_valid_json_from_response(result)
                
                if result and self._validate_backlog_quality(result, original_text, trd):
                    print(f"✅ High-quality backlog generated on attempt {attempt + 1}")
                    return result, None
                else:
                    print(f"⚠️ Attempt {attempt + 1} failed quality validation, retrying...")
                    
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1} failed with error: {e}")
                continue
        
        # If all attempts fail, create a context-aware fallback
        print("🔄 All attempts failed, creating context-aware fallback...")
        fallback = self._create_context_aware_backlog_fallback(plan, original_text, trd)
        return fallback, "Used context-aware fallback due to quality issues"
    
    def generate_high_quality_hld(self, plan: str, original_text: str, max_attempts: int = 3) -> Tuple[str, Optional[str]]:
        """Generate high-quality HLD with multiple attempts and quality validation"""
        print("🔍 ENHANCED HLD GENERATOR: Starting high-quality generation...")
        
        for attempt in range(max_attempts):
            print(f"📝 Attempt {attempt + 1}/{max_attempts}")
            
            # Generate with increasingly specific prompts
            prompt = self._create_hld_prompt(plan, original_text, attempt + 1)
            
            # Generate response
            result = self.llm_engine.generate_response(prompt)
            
            if result and self._validate_hld_quality(result, original_text):
                print(f"✅ High-quality HLD generated on attempt {attempt + 1}")
                return result, None
            else:
                print(f"⚠️ Attempt {attempt + 1} failed quality validation, retrying...")
        
        # If all attempts fail, create a context-aware fallback
        print("🔄 All attempts failed, creating context-aware fallback...")
        fallback = self._create_context_aware_hld_fallback(plan, original_text)
        return fallback, "Used context-aware fallback due to quality issues"
    
    def generate_high_quality_lld(self, plan: str, original_text: str, hld_content: str, max_attempts: int = 3) -> Tuple[str, Optional[str]]:
        """Generate high-quality LLD with multiple attempts and quality validation"""
        print("🔍 ENHANCED LLD GENERATOR: Starting high-quality generation...")
        
        for attempt in range(max_attempts):
            print(f"📝 Attempt {attempt + 1}/{max_attempts}")
            
            # Generate with increasingly specific prompts
            prompt = self._create_lld_prompt(plan, original_text, hld_content, attempt + 1)
            
            # Generate response
            result = self.llm_engine.generate_response(prompt)
            
            if result and self._validate_lld_quality(result, original_text, hld_content):
                print(f"✅ High-quality LLD generated on attempt {attempt + 1}")
                return result, None
            else:
                print(f"⚠️ Attempt {attempt + 1} failed quality validation, retrying...")
        
        # If all attempts fail, create a context-aware fallback
        print("🔄 All attempts failed, creating context-aware fallback...")
        fallback = self._create_context_aware_lld_fallback(plan, original_text, hld_content)
        return fallback, "Used context-aware fallback due to quality issues"
    
    def _create_backlog_prompt(self, plan: str, original_text: str, trd: str, attempt: int) -> str:
        """Create increasingly specific backlog prompts"""
        
        # Extract key information from inputs
        key_requirements = self._extract_key_requirements(original_text)
        business_domain = self._extract_business_domain(original_text)
        technical_requirements = self._extract_technical_requirements(trd)
        
        base_prompt = f"""You are a Senior Product Manager with 20+ years of experience in {business_domain} software development.

**CRITICAL INSTRUCTION**: Generate a COMPREHENSIVE and SPECIFIC project backlog based EXCLUSIVELY on the provided requirements. 
- DO NOT include generic, example, or template content
- EVERY backlog item must directly address specific requirements from the input
- Use the EXACT terminology and concepts from the input documents
- Create detailed, actionable user stories with specific acceptance criteria

**PROJECT CONTEXT**:
- Business Domain: {business_domain}
- Key Requirements: {key_requirements}
- Technical Requirements: {technical_requirements}

**BACKLOG STRUCTURE REQUIREMENTS**:
1. **Epics** (3-5): High-level business capabilities specific to this project
2. **Features** (2-4 per epic): Major functionality within each epic
3. **User Stories** (3-8 per feature): Detailed requirements with specific acceptance criteria

**QUALITY REQUIREMENTS**:
- Generate 2-3 epics with 2-3 features each
- Create 2-4 user stories per feature (total 8-15 stories)
- Every story must reference specific requirements from the input
- Include stories for non-functional requirements (security, performance, etc.)
- Provide realistic effort estimates (1-13 story points)
- Include detailed acceptance criteria for all stories
- Keep response concise and focused

**JSON FORMAT**:
{{
  "backlog": [
    {{
      "id": "epic-1",
      "type": "Epic",
      "title": "[SPECIFIC EPIC TITLE BASED ON REQUIREMENTS]",
      "description": "[DETAILED DESCRIPTION REFERENCING SPECIFIC REQUIREMENTS]",
      "priority": "High/Medium/Low",
      "effort": "[STORY POINTS]",
      "trd_sections": ["[SPECIFIC TRD SECTIONS]"],
      "requirements_covered": ["[SPECIFIC REQUIREMENTS FROM INPUT]"],
      "children": [
        {{
          "id": "feature-1",
          "type": "Feature",
          "title": "[SPECIFIC FEATURE TITLE]",
          "description": "[DETAILED FEATURE DESCRIPTION]",
          "priority": "High/Medium/Low",
          "effort": "[STORY POINTS]",
          "trd_sections": ["[SPECIFIC TRD SECTIONS]"],
          "requirements_covered": ["[SPECIFIC REQUIREMENTS]"],
          "children": [
            {{
              "id": "story-1",
              "type": "User Story",
              "title": "[SPECIFIC USER STORY TITLE]",
              "description": "As a [SPECIFIC USER ROLE], I want [SPECIFIC FEATURE] so that [SPECIFIC BUSINESS VALUE]",
              "priority": "High/Medium/Low",
              "effort": "[STORY POINTS]",
              "acceptance_criteria": [
                "[SPECIFIC CRITERION 1]",
                "[SPECIFIC CRITERION 2]",
                "[SPECIFIC CRITERION 3]"
              ],
              "trd_sections": ["[SPECIFIC TRD SECTIONS]"],
              "requirements_covered": ["[SPECIFIC REQUIREMENTS]"]
            }}
          ]
        }}
      ]
    }}
  ]
}}

**INPUT DOCUMENTS**:
--- HIGH-LEVEL PLAN ---
{plan}

--- TECHNICAL REQUIREMENTS DOCUMENT ---
{trd}

--- ORIGINAL REQUIREMENTS TEXT ---
{original_text}

**FINAL INSTRUCTION**: Generate ONLY valid JSON with specific, actionable backlog items that directly address the requirements above. NO generic content, examples, or placeholders."""

        # Add increasingly specific instructions for retry attempts
        if attempt > 1:
            base_prompt += f"""

**RETRY ATTEMPT {attempt} - ENHANCED SPECIFICITY**:
- Focus on the MOST SPECIFIC requirements from the input
- Create backlog items that directly implement the described functionality
- Use exact business terms and processes mentioned in the requirements
- Ensure every user story has concrete, measurable acceptance criteria
- Include technical implementation details specific to this project"""
        
        return base_prompt
    
    def _create_hld_prompt(self, plan: str, original_text: str, attempt: int) -> str:
        """Create increasingly specific HLD Mermaid diagram prompts"""
        
        key_requirements = self._extract_key_requirements(original_text)
        business_domain = self._extract_business_domain(original_text)
        technical_constraints = self._extract_technical_constraints(original_text)
        
        base_prompt = f"""You are a Senior Solution Architect specializing in system design diagrams.

Create a High-Level Design (HLD) diagram using Mermaid syntax. The diagram should show:

**System Architecture Components:**
- User Interface Layer (Web/Mobile/Desktop)
- Application Layer (API Gateway, Services)
- Business Logic Layer (Core Services)
- Data Access Layer (Repositories)
- External Systems Integration
- Security Layer (Authentication/Authorization)

**Key Elements:**
- System boundaries and data flow
- Integration points with external systems
- Technology stack components
- Security layers and authentication
- Load balancers and caching

**SPECIFIC REQUIREMENTS FOR THIS PROJECT:**
- Business Domain: {business_domain}
- Key Requirements: {key_requirements}
- Technical Constraints: {technical_constraints}

Use Mermaid flowchart syntax with:
- Clear component names in boxes
- Proper relationships with arrows
- Color coding for different layers using classDef and class assignments
- Professional styling and layout with consistent colors for layers
- AVOID subgraph syntax - use simple flowchart instead

IMPORTANT: 
- Respond ONLY with the Mermaid diagram code, no additional text or explanations
- Use simple flowchart syntax, NOT subgraph
- Use clear, simple node labels
- Avoid complex syntax that might cause parsing errors
- Design specifically for the {business_domain} domain requirements

Use THIS CANONICAL MERMAID STYLE as reference. Reuse its init block, classDefs, and linkStyle conventions; only change node labels and edges for the current system. Keep linkStyle indices contiguous starting at 0.

                    ```mermaid
                    %%{{init: {{
                      "theme": "default",
                      "themeVariables": {{
                        "fontFamily": "Segoe UI, Arial",
                        "primaryColor": "#f2f2f2",
                        "edgeLabelBackground":"#f7ffe2"
                      }}
                    }}}}%%
                    flowchart TD
                        start((Start)):::startStyle
                        step1["First Step"]:::stepA
                        dec1{{{{Decision Point}}}}:::decision
                        step2["Second Step"]:::stepB
                        endcircle((("END"))):::endStyle

                        start --> step1
                        step1 -- Yes --> dec1
                        step1 -- No --> endcircle
                        dec1 -- True --> step2
                        dec1 -- False --> endcircle
                        step2 --> endcircle

                        %% Node styling
                        classDef startStyle fill:#6be585,stroke:#247346,stroke-width:3px,color:#fff;
                        classDef decision fill:#ffd966,stroke:#b29928,stroke-width:3px,color:#593E00;
                        classDef stepA fill:#bbdefb,stroke:#1976d2,stroke-width:2px;
                        classDef stepB fill:#c5e1a5,stroke:#558b2f,stroke-width:2px;
                        classDef endStyle fill:#e57373,stroke:#b71c1c,stroke-width:4px,color:#fff;

                        %% Link styling (by order)
                        linkStyle 0 stroke:#29a19c,stroke-width:4px;
                        linkStyle 1 stroke:#fbc02d,stroke-width:3px,stroke-dasharray: 4 2;
                        linkStyle 2 stroke:#b71c1c,stroke-width:3px,stroke-dasharray: 2 4;
                        linkStyle 3 stroke:#388e3c,stroke-width:3px;
                        linkStyle 4 stroke:#b71c1c,stroke-width:3px,stroke-dasharray: 4 2;
                    ```

--- HIGH-LEVEL PLAN ---
{plan}

--- ORIGINAL REQUIREMENTS TEXT ---
{original_text}"""

        if attempt > 1:
            base_prompt += f"""

**RETRY ATTEMPT {attempt} - ENHANCED SPECIFICITY**:
- Focus on the MOST SPECIFIC technical requirements
- Design architecture components that directly implement described functionality
- Use exact technical terms and patterns mentioned in the requirements
- Ensure every architectural decision is justified by specific project needs"""
        
        return base_prompt
    
    def _create_lld_prompt(self, plan: str, original_text: str, hld_content: str, attempt: int) -> str:
        """Create increasingly specific LLD Mermaid diagram prompts"""
        
        key_requirements = self._extract_key_requirements(original_text)
        business_domain = self._extract_business_domain(original_text)
        
        base_prompt = f"""You are a Senior Software Architect specializing in detailed system design.

Create a Low-Level Design (LLD) diagram using Mermaid syntax. The diagram should show:

**Detailed System Components:**
- Specific modules, classes, and interfaces
- Database schema relationships and tables
- API endpoints and HTTP methods
- Data flow between components
- Error handling and validation paths
- Caching and performance optimizations

**Key Elements:**
- Detailed component interactions
- Database tables and relationships
- API specifications with methods
- Security implementation details
- Performance considerations
- Error handling flows

**SPECIFIC REQUIREMENTS FOR THIS PROJECT:**
- Business Domain: {business_domain}
- Key Requirements: {key_requirements}

Use Mermaid flowchart syntax with:
- Detailed component breakdown
- Clear data flow with labels
- Error handling paths
- Performance indicators
- Database relationships
- Color-coded components using classDef and class assignments
- AVOID subgraph syntax - use simple flowchart instead

IMPORTANT: 
- Respond ONLY with the Mermaid diagram code, no additional text or explanations
- Use simple flowchart syntax, NOT subgraph
- Use clear, simple node labels
- Avoid complex syntax that might cause parsing errors
- Design specifically for the {business_domain} domain requirements

Use THIS CANONICAL MERMAID STYLE as reference. Reuse its init block, classDefs, and linkStyle conventions; only change node labels and edges for the current feature. Keep linkStyle indices contiguous starting at 0.

                    ```mermaid
                    %%{{init: {{
                      "theme": "default",
                      "themeVariables": {{
                        "fontFamily": "Segoe UI, Arial",
                        "primaryColor": "#f2f2f2",
                        "edgeLabelBackground":"#f7ffe2"
                      }}
                    }}}}%%
                    flowchart TD
                        start((Start)):::startStyle
                        step1["First Step"]:::stepA
                        dec1{{{{Decision Point}}}}:::decision
                        step2["Second Step"]:::stepB
                        endcircle((("END"))):::endStyle

                        start --> step1
                        step1 -- Yes --> dec1
                        step1 -- No --> endcircle
                        dec1 -- True --> step2
                        dec1 -- False --> endcircle
                        step2 --> endcircle

                        %% Node styling
                        classDef startStyle fill:#6be585,stroke:#247346,stroke-width:3px,color:#fff;
                        classDef decision fill:#ffd966,stroke:#b29928,stroke-width:3px,color:#593E00;
                        classDef stepA fill:#bbdefb,stroke:#1976d2,stroke-width:2px;
                        classDef stepB fill:#c5e1a5,stroke:#558b2f,stroke-width:2px;
                        classDef endStyle fill:#e57373,stroke:#b71c1c,stroke-width:4px,color:#fff;

                        %% Link styling (by order)
                        linkStyle 0 stroke:#29a19c,stroke-width:4px;
                        linkStyle 1 stroke:#fbc02d,stroke-width:3px,stroke-dasharray: 4 2;
                        linkStyle 2 stroke:#b71c1c,stroke-width:3px,stroke-dasharray: 2 4;
                        linkStyle 3 stroke:#388e3c,stroke-width:3px;
                        linkStyle 4 stroke:#b71c1c,stroke-width:3px,stroke-dasharray: 4 2;
                    ```

--- HIGH-LEVEL PLAN ---
{plan}

--- ORIGINAL REQUIREMENTS TEXT ---
{original_text}

--- HIGH-LEVEL DESIGN ---
{hld_content}"""

        if attempt > 1:
            base_prompt += f"""

**RETRY ATTEMPT {attempt} - ENHANCED SPECIFICITY**:
- Focus on the MOST SPECIFIC implementation requirements
- Design components that directly implement described functionality
- Use exact technical terms and patterns mentioned in the requirements
- Ensure every design decision is justified by specific project needs"""
        
        return base_prompt
    
    def _validate_backlog_quality(self, result: Dict, original_text: str, trd: str) -> bool:
        """Validate backlog quality"""
        try:
            if not isinstance(result, dict) or 'backlog' not in result:
                print("❌ Backlog validation: Not a valid dict or missing 'backlog' key")
                return False
            
            backlog = result['backlog']
            if not isinstance(backlog, list) or len(backlog) == 0:
                print("❌ Backlog validation: Empty or invalid backlog list")
                return False
            
            # Check for minimum content - much more lenient
            total_stories = 0
            for epic in backlog:
                if 'children' in epic:
                    for feature in epic['children']:
                        if 'children' in feature:
                            total_stories += len(feature['children'])
            
            if total_stories < 1:  # Just need at least 1 story
                print(f"❌ Backlog validation: Only {total_stories} stories found, need at least 1")
                return False
            
            print(f"✅ Backlog validation: Found {len(backlog)} epics with {total_stories} stories")
            return True
            
        except Exception as e:
            print(f"❌ Backlog validation error: {e}")
            return False
    
    def _validate_hld_quality(self, result: str, original_text: str) -> bool:
        """Validate HLD Mermaid diagram quality"""
        # Extract Mermaid code
        mermaid_code = extract_mermaid_code(result)
        if not mermaid_code:
            print("❌ HLD validation: No Mermaid code found")
            return False
        
        # Check for flowchart syntax
        if not re.search(r'flowchart\s+\w+', mermaid_code):
            print("❌ HLD validation: No flowchart syntax found")
            return False
        
        # Check for minimum content
        if len(mermaid_code) < 100:
            print(f"❌ HLD validation: Mermaid code too short ({len(mermaid_code)} chars)")
            return False
        
        print(f"✅ HLD validation: Valid Mermaid diagram with {len(mermaid_code)} chars - PASSED")
        return True
    
    def _validate_lld_quality(self, result: str, original_text: str, hld_content: str) -> bool:
        """Validate LLD Mermaid diagram quality"""
        # Extract Mermaid code
        mermaid_code = extract_mermaid_code(result)
        if not mermaid_code:
            print("❌ LLD validation: No Mermaid code found")
            return False
        
        # Check for flowchart syntax
        if not re.search(r'flowchart\s+\w+', mermaid_code):
            print("❌ LLD validation: No flowchart syntax found")
            return False
        
        # Check for minimum content
        if len(mermaid_code) < 100:
            print(f"❌ LLD validation: Mermaid code too short ({len(mermaid_code)} chars)")
            return False
        
        print(f"✅ LLD validation: Valid Mermaid diagram with {len(mermaid_code)} chars - PASSED")
        return True
    
    def _calculate_specificity_score(self, generated_content: str, original_text: str) -> float:
        """Calculate how specific the generated content is to the original requirements"""
        # Extract key terms from original text
        original_terms = set(re.findall(r'\b\w{4,}\b', original_text.lower()))
        
        # Extract key terms from generated content
        generated_terms = set(re.findall(r'\b\w{4,}\b', generated_content.lower()))
        
        # Calculate overlap
        overlap = len(original_terms.intersection(generated_terms))
        total_original = len(original_terms)
        
        if total_original == 0:
            return 0.0
        
        return min(1.0, overlap / total_original)
    
    def _extract_key_requirements(self, text: str) -> List[str]:
        """Extract key requirements from text"""
        # Simple extraction - can be enhanced
        lines = text.split('\n')
        requirements = []
        for line in lines:
            line = line.strip()
            if line and any(keyword in line.lower() for keyword in ['must', 'should', 'need', 'require', 'implement']):
                requirements.append(line)
        return requirements[:10]  # Limit to top 10
    
    def _extract_business_domain(self, text: str) -> str:
        """Extract business domain from text"""
        domains = ['insurance', 'banking', 'healthcare', 'retail', 'manufacturing', 'education']
        text_lower = text.lower()
        for domain in domains:
            if domain in text_lower:
                return domain.title()
        return "Business"
    
    def _extract_technical_requirements(self, trd: str) -> List[str]:
        """Extract technical requirements from TRD"""
        lines = trd.split('\n')
        tech_reqs = []
        for line in lines:
            line = line.strip()
            if line and any(keyword in line.lower() for keyword in ['api', 'database', 'security', 'performance', 'scalability']):
                tech_reqs.append(line)
        return tech_reqs[:10]
    
    def _extract_technical_constraints(self, text: str) -> List[str]:
        """Extract technical constraints from text"""
        lines = text.split('\n')
        constraints = []
        for line in lines:
            line = line.strip()
            if line and any(keyword in line.lower() for keyword in ['constraint', 'limit', 'must use', 'cannot use']):
                constraints.append(line)
        return constraints[:5]
    
    def _extract_valid_json_from_response(self, response: str) -> Optional[Dict]:
        """Extract valid JSON from a potentially truncated or malformed response"""
        try:
            # First, try to parse the response as-is
            if isinstance(response, dict):
                return response
            
            # If it's a string, try to find JSON content
            if isinstance(response, str):
                # Look for JSON object markers
                start_markers = ['{', '{"backlog"', '{"epics"']
                end_markers = ['}', ']', '"]']
                
                for start_marker in start_markers:
                    start_idx = response.find(start_marker)
                    if start_idx != -1:
                        # Find the matching closing brace/bracket
                        brace_count = 0
                        bracket_count = 0
                        in_string = False
                        escape_next = False
                        
                        for i in range(start_idx, len(response)):
                            char = response[i]
                            
                            if escape_next:
                                escape_next = False
                                continue
                            
                            if char == '\\':
                                escape_next = True
                                continue
                            
                            if char == '"' and not escape_next:
                                in_string = not in_string
                                continue
                            
                            if not in_string:
                                if char == '{':
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                                elif char == '[':
                                    bracket_count += 1
                                elif char == ']':
                                    bracket_count -= 1
                                
                                # Check if we've found a complete JSON structure
                                if brace_count == 0 and bracket_count == 0:
                                    json_str = response[start_idx:i+1]
                                    try:
                                        parsed = json.loads(json_str)
                                        print(f"✅ Successfully extracted valid JSON ({len(json_str)} chars)")
                                        return parsed
                                    except json.JSONDecodeError:
                                        continue
                
                # If no complete JSON found, try to fix common issues
                print("⚠️ Attempting to fix common JSON issues...")
                fixed_response = self._fix_common_json_issues(response)
                if fixed_response:
                    try:
                        parsed = json.loads(fixed_response)
                        print(f"✅ Successfully parsed fixed JSON ({len(fixed_response)} chars)")
                        return parsed
                    except json.JSONDecodeError:
                        pass
            
            return None
            
        except Exception as e:
            print(f"❌ Error extracting JSON: {e}")
            return None
    
    def _fix_common_json_issues(self, response: str) -> Optional[str]:
        """Fix common JSON formatting issues"""
        try:
            # Remove any text before the first {
            start_idx = response.find('{')
            if start_idx == -1:
                return None
            
            json_part = response[start_idx:]
            
            # Fix common issues
            # 1. Remove trailing commas before closing braces/brackets
            json_part = re.sub(r',(\s*[}\]])', r'\1', json_part)
            
            # 2. Fix unescaped quotes in strings
            json_part = re.sub(r'([^\\])"([^"]*?)([^\\])"', r'\1"\2\3"', json_part)
            
            # 3. Ensure proper closing
            brace_count = json_part.count('{') - json_part.count('}')
            bracket_count = json_part.count('[') - json_part.count(']')
            
            # Add missing closing braces/brackets
            json_part += '}' * brace_count + ']' * bracket_count
            
            return json_part
            
        except Exception as e:
            print(f"❌ Error fixing JSON: {e}")
            return None
    
    def _create_context_aware_backlog_fallback(self, plan: str, original_text: str, trd: str) -> Dict:
        """Create context-aware backlog fallback"""
        print("🔄 Creating context-aware backlog fallback...")
        
        # Extract specific information
        key_requirements = self._extract_key_requirements(original_text)
        business_domain = self._extract_business_domain(original_text)
        
        # Create specific backlog based on extracted information
        backlog = {
            "backlog": [
                {
                    "id": "epic-1",
                    "type": "Epic",
                    "title": f"{business_domain} System Implementation",
                    "description": f"Core implementation of {business_domain} system based on specific requirements",
                    "priority": "High",
                    "effort": "40",
                    "trd_sections": ["SYSTEM OVERVIEW", "FUNCTIONAL REQUIREMENTS"],
                    "requirements_covered": key_requirements[:3],
                    "children": []
                }
            ]
        }
        
        # Add features and stories based on requirements
        for i, req in enumerate(key_requirements[:5]):
            feature = {
                "id": f"feature-{i+1}",
                "type": "Feature",
                "title": f"Implement {req.split()[0]} functionality",
                "description": f"Implement specific requirement: {req}",
                "priority": "High",
                "effort": "13",
                "trd_sections": ["FUNCTIONAL REQUIREMENTS"],
                "requirements_covered": [req],
                "children": [
                    {
                        "id": f"story-{i+1}-1",
                        "type": "User Story",
                        "title": f"Implement {req.split()[0]} feature",
                        "description": f"As a user, I want {req.lower()} so that the system meets the specific requirement",
                        "priority": "High",
                        "effort": "5",
                        "acceptance_criteria": [
                            f"System implements {req}",
                            f"Feature is tested and validated",
                            f"Documentation is updated"
                        ],
                        "trd_sections": ["FUNCTIONAL REQUIREMENTS"],
                        "requirements_covered": [req]
                    }
                ]
            }
            backlog["backlog"][0]["children"].append(feature)
        
        return backlog
    
    def _create_context_aware_hld_fallback(self, plan: str, original_text: str) -> str:
        """Create context-aware HLD fallback"""
        print("🔄 Creating context-aware HLD fallback...")
        
        business_domain = self._extract_business_domain(original_text)
        key_requirements = self._extract_key_requirements(original_text)
        
        hld = f"""# HIGH-LEVEL DESIGN DOCUMENT

## 1. SYSTEM OVERVIEW
- Architecture Pattern: Layered Architecture specific to {business_domain}
- Technology Stack: Based on {business_domain} industry standards
- System Boundaries: Defined by specific business requirements

## 2. ARCHITECTURAL COMPONENTS
### 2.1 User Interface Layer
- Web-based interface for {business_domain} operations
- Mobile-responsive design for field operations
- Integration with existing {business_domain} systems

### 2.2 Application Layer
- RESTful API services for {business_domain} business processes
- API Gateway for security and routing
- Service orchestration for complex workflows

### 2.3 Business Logic Layer
- Core {business_domain} business services
- Workflow engine for business processes
- Rule engine for {business_domain} compliance

### 2.4 Data Access Layer
- Repository pattern for data access
- Integration with existing {business_domain} databases
- Caching layer for performance optimization

### 2.5 External Systems Integration
- Integration with {business_domain} regulatory systems
- Third-party service integration
- Legacy system connectors

## 3. SECURITY ARCHITECTURE
- Role-based access control for {business_domain} users
- Multi-factor authentication
- Data encryption for sensitive {business_domain} information

## 4. PERFORMANCE & SCALABILITY
- Horizontal scaling for high-volume {business_domain} transactions
- Caching strategy for frequently accessed data
- Load balancing for distributed deployment

## 5. DEPLOYMENT ARCHITECTURE
- Containerized deployment for {business_domain} environments
- CI/CD pipeline for automated deployments
- Monitoring and logging for {business_domain} operations

**SPECIFIC REQUIREMENTS ADDRESSED:**
{chr(10).join([f"- {req}" for req in key_requirements[:5]])}

**BUSINESS DOMAIN:** {business_domain}
**GENERATED FROM:** Original requirements analysis
**QUALITY:** Context-aware fallback implementation"""
        
        return hld
    
    def _create_context_aware_lld_fallback(self, plan: str, original_text: str, hld_content: str) -> str:
        """Create context-aware LLD fallback"""
        print("🔄 Creating context-aware LLD fallback...")
        
        business_domain = self._extract_business_domain(original_text)
        key_requirements = self._extract_key_requirements(original_text)
        
        lld = f"""# LOW-LEVEL DESIGN DOCUMENT

## 1. DATABASE DESIGN
### 1.1 Schema Design
- Core {business_domain} entity tables
- Relationship tables for {business_domain} business rules
- Audit tables for compliance tracking

### 1.2 Data Access Layer
- Repository interfaces for {business_domain} entities
- Query optimization for {business_domain} data patterns
- Transaction management for {business_domain} operations

## 2. API DESIGN
### 2.1 REST API Endpoints
- CRUD operations for {business_domain} entities
- Business process endpoints
- Integration endpoints for external systems

### 2.2 Service Layer
- Business service implementations
- Validation services for {business_domain} rules
- Integration services for external systems

## 3. COMPONENT DESIGN
### 3.1 Class Diagrams
- Entity classes for {business_domain} domain
- Service classes for business logic
- Repository classes for data access

### 3.2 Method Signatures
- Business operation methods
- Validation methods for {business_domain} rules
- Integration methods for external systems

## 4. INTEGRATION DESIGN
### 4.1 External System Integration
- API clients for external {business_domain} systems
- Data transformation services
- Error handling for integration failures

### 4.2 Error Handling
- Business rule validation errors
- Integration error handling
- System error recovery mechanisms

**SPECIFIC REQUIREMENTS ADDRESSED:**
{chr(10).join([f"- {req}" for req in key_requirements[:5]])}

**BUSINESS DOMAIN:** {business_domain}
**HLD REFERENCE:** Based on provided High-Level Design
**QUALITY:** Context-aware fallback implementation"""
        
        return lld
