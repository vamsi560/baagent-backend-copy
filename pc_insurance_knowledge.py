# pc_insurance_knowledge.py
# P&C Insurance Domain Knowledge for Phase 2

from typing import List

P_C_INSURANCE_TEMPLATES = {
    "personal_auto": {
        "keywords": ["auto insurance", "car insurance", "vehicle", "driver", "policy", "personal auto", "private passenger"],
        "requirements": ["liability coverage", "collision coverage", "comprehensive coverage", "uninsured motorist", "medical payments"],
        "regulations": ["state minimums", "no-fault laws", "tort laws", "financial responsibility laws", "mandatory coverage"],
        "analysis_focus": ["risk assessment", "driver history", "vehicle type", "usage patterns", "geographic location", "credit score impact"],
        "technical_considerations": ["telematics integration", "usage-based pricing", "claims automation", "fraud detection", "customer portal"]
    },
    "commercial_auto": {
        "keywords": ["commercial vehicle", "fleet", "business auto", "commercial driver", "trucking", "delivery"],
        "requirements": ["higher liability limits", "fleet management", "driver training", "safety programs", "cargo coverage"],
        "regulations": ["DOT regulations", "commercial licensing", "safety requirements", "hours of service", "vehicle inspections"],
        "analysis_focus": ["fleet size", "driver qualifications", "safety records", "business type", "operating radius", "cargo type"],
        "technical_considerations": ["fleet management systems", "GPS tracking", "driver monitoring", "maintenance scheduling", "compliance reporting"]
    },
    "homeowners": {
        "keywords": ["home insurance", "property", "dwelling", "personal property", "homeowners", "residential"],
        "requirements": ["dwelling coverage", "personal property", "liability protection", "loss of use", "medical payments"],
        "regulations": ["building codes", "zoning laws", "flood requirements", "windstorm coverage", "earthquake exclusions"],
        "analysis_focus": ["property value", "location risks", "construction type", "safety features", "replacement cost", "market conditions"],
        "technical_considerations": ["property inspection tools", "risk modeling", "claims processing", "underwriting automation", "customer self-service"]
    },
    "general_liability": {
        "keywords": ["liability", "third party", "bodily injury", "property damage", "general liability", "commercial liability"],
        "requirements": ["occurrence basis", "claims-made basis", "aggregate limits", "per occurrence limits", "defense costs"],
        "regulations": ["state liability laws", "industry standards", "contract requirements", "regulatory compliance", "tort reform"],
        "analysis_focus": ["business operations", "risk exposure", "claim history", "industry type", "geographic scope", "contractual obligations"],
        "technical_considerations": ["risk assessment tools", "claims management", "legal research integration", "compliance monitoring", "policy administration"]
    },
    "workers_comp": {
        "keywords": ["workers compensation", "workplace injury", "employee benefits", "employer liability", "occupational"],
        "requirements": ["medical benefits", "disability benefits", "rehabilitation", "death benefits", "employer liability"],
        "regulations": ["state workers comp laws", "OSHA requirements", "return to work programs", "medical fee schedules", "dispute resolution"],
        "analysis_focus": ["industry classification", "payroll exposure", "safety programs", "claim frequency", "medical costs", "return to work success"],
        "technical_considerations": ["injury reporting systems", "medical case management", "return to work tracking", "safety program management", "compliance reporting"]
    },
    "cyber": {
        "keywords": ["cyber insurance", "cybersecurity", "data breach", "privacy", "network security", "digital risk"],
        "requirements": ["data breach response", "business interruption", "cyber extortion", "privacy liability", "network security liability"],
        "regulations": ["GDPR", "CCPA", "HIPAA", "SOX", "state breach notification laws", "industry standards"],
        "analysis_focus": ["data sensitivity", "security controls", "breach history", "industry regulations", "vendor management", "incident response"],
        "technical_considerations": ["security assessment tools", "breach response services", "forensic capabilities", "compliance monitoring", "risk scoring models"]
    },
    "property": {
        "keywords": ["property insurance", "commercial property", "building", "equipment", "inventory", "business interruption"],
        "requirements": ["building coverage", "contents coverage", "business interruption", "extra expense", "equipment breakdown"],
        "regulations": ["building codes", "fire codes", "sprinkler requirements", "alarm systems", "occupancy restrictions"],
        "analysis_focus": ["property value", "construction type", "occupancy", "protection features", "business interruption exposure", "replacement cost"],
        "technical_considerations": ["property inspection tools", "valuation models", "business interruption modeling", "claims processing", "risk engineering"]
    },
    "professional_liability": {
        "keywords": ["professional liability", "errors and omissions", "malpractice", "professional services", "consulting"],
        "requirements": ["errors and omissions", "defense costs", "prior acts coverage", "retroactive date", "claims-made basis"],
        "regulations": ["professional licensing", "industry standards", "contractual requirements", "regulatory compliance", "ethical guidelines"],
        "analysis_focus": ["professional services", "client base", "contract terms", "claim history", "risk management practices", "professional standards"],
        "technical_considerations": ["contract review tools", "risk assessment", "claims management", "professional development tracking", "compliance monitoring"]
    }
}

P_C_ANALYSIS_TEMPLATES = {
    "business_requirements": """
    Based on the provided P&C insurance document, analyze the following:

    1. **Line of Business Classification**:
       - Primary LOB: [Identify main insurance line]
       - Secondary LOBs: [List any additional lines]
       - Market Segment: [Personal/Commercial/Specialty]
       - Geographic Scope: [State/Regional/National/International]

    2. **Key Requirements Analysis**:
       - Coverage Requirements: [List specific coverages needed]
       - Policy Limits: [Identify coverage limits and deductibles]
       - Endorsements: [List any special endorsements or riders]
       - Exclusions: [Identify key exclusions and limitations]

    3. **Risk Assessment**:
       - Risk Factors: [Identify key risk factors]
       - Underwriting Considerations: [List underwriting criteria]
       - Loss Control Measures: [Suggest risk mitigation strategies]
       - Rating Factors: [Identify pricing considerations]

    4. **Regulatory Compliance**:
       - State Requirements: [List applicable state regulations]
       - Industry Standards: [Identify industry best practices]
       - Compliance Gaps: [Highlight any compliance issues]
       - Reporting Requirements: [Specify regulatory reporting needs]

    5. **Technical Requirements**:
       - System Integration: [Identify system requirements]
       - Data Requirements: [List data collection needs]
       - Reporting Requirements: [Specify reporting needs]
       - Workflow Requirements: [Define process workflows]

    6. **Business Impact**:
       - Market Opportunity: [Assess market potential]
       - Competitive Position: [Analyze competitive landscape]
       - Revenue Potential: [Estimate premium volume]
       - Operational Impact: [Assess operational requirements]
    """,
    
    "technical_requirements": """
    Create a comprehensive Technical Requirements Document for the P&C insurance system with proper formatting:

    1. **EXECUTIVE SUMMARY**:
       - Project Overview: [Provide clear project description and objectives]
       - Key Objectives: [List primary goals and success criteria]
       - Success Metrics: [Define measurable success indicators]

    2. **SYSTEM OVERVIEW**:
       - High-Level Architecture: [Describe system architecture with clear component relationships]
       - System Components: [List and describe all major system components]
       - Technology Stack: [Specify programming languages, databases, frameworks, cloud platforms]
       - Integration Points: [Detail all external system integrations]

    3. **FUNCTIONAL REQUIREMENTS**:
       - Core Features: [Detail main system functionalities]
       - Business Rules: [Define business logic and validation rules]
       - Data Requirements: [Specify data models, quality standards, and governance]
       - User Roles and Permissions: [Define access control and user management]

    4. **NON-FUNCTIONAL REQUIREMENTS**:
       - Performance Requirements: [Specify response times, throughput, and scalability]
       - Security Requirements: [Define security standards, compliance, and data protection]
       - Availability Requirements: [Specify uptime, reliability, and disaster recovery]
       - Usability Requirements: [Define user experience and interface standards]

    5. **TECHNICAL SPECIFICATIONS**:
       - System Architecture: [Detailed technical architecture]
       - Database Design: [Data models, schemas, and relationships]
       - API Specifications: [RESTful API design and documentation]
       - Integration Specifications: [External system integration details]

    6. **IMPLEMENTATION PLAN**:
       - Development Phases: [Break down into logical phases]
       - Timeline: [Provide realistic timeline estimates]
       - Resource Requirements: [Specify team and infrastructure needs]
       - Risk Mitigation: [Identify risks and mitigation strategies]

    **CRITICAL TABLE FORMATTING REQUIREMENTS:**
    - Use simple, readable tables with 3-5 columns maximum
    - Keep table content concise and focused
    - Use proper markdown table syntax with | characters
    - Ensure column headers are clear and descriptive
    - Limit cell content to 2-3 sentences maximum
    - Use bullet points within cells for better readability
    - Avoid overly complex or wide tables
    - Break large tables into smaller, focused tables
    - Use consistent formatting across all tables
    """,
    
    "risk_assessment": """
    Conduct a comprehensive risk assessment for the P&C insurance product:

    1. **Underwriting Risk Analysis**:
       - Risk Classification: [Categorize risk levels]
       - Rating Factors: [Identify key rating variables]
       - Loss Experience: [Analyze historical loss data]
       - Risk Trends: [Identify emerging risk patterns]

    2. **Operational Risk Assessment**:
       - Process Risks: [Identify operational vulnerabilities]
       - Technology Risks: [Assess system risks]
       - Compliance Risks: [Evaluate regulatory risks]
       - Fraud Risks: [Identify fraud exposure]

    3. **Market Risk Analysis**:
       - Competitive Landscape: [Analyze market competition]
       - Regulatory Environment: [Assess regulatory changes]
       - Economic Factors: [Consider economic impacts]
       - Catastrophe Exposure: [Evaluate catastrophe risks]

    4. **Financial Risk Assessment**:
       - Pricing Adequacy: [Assess pricing sufficiency]
       - Reserve Requirements: [Calculate reserve needs]
       - Capital Requirements: [Determine capital needs]
       - Reinsurance Strategy: [Plan reinsurance approach]

    5. **Risk Mitigation Strategies**:
       - Underwriting Controls: [Implement risk controls]
       - Loss Prevention: [Develop loss control programs]
       - Technology Solutions: [Deploy risk management tools]
       - Monitoring Systems: [Establish monitoring processes]
    """
}

P_C_PROMPT_TEMPLATES = {
    "document_analysis": """
    You are an expert P&C insurance business analyst with deep knowledge of {lob} insurance.
    
    **Domain Context:**
    - Line of Business: {lob}
    - Key Focus Areas: {focus_areas}
    - Regulatory Framework: {regulations}
    - Technical Considerations: {technical_considerations}
    
    **Document to Analyze:**
    {document_content}
    
    **Analysis Instructions:**
    {analysis_template}
    
    Please provide a comprehensive analysis following the structure above.
    Focus on P&C insurance specific insights and recommendations.
    Use industry terminology and best practices.
    """,
    
    "technical_generation": """
    Based on the following P&C insurance business analysis:
    
    {analysis_results}
    
    **Technical Requirements Generation:**
    {technical_template}
    
    Generate a detailed technical requirements document specifically for P&C insurance systems.
    Include industry-specific technical considerations and best practices.
    Focus on practical implementation requirements.
    
    **CRITICAL FORMATTING REQUIREMENTS:**
    1. Use proper markdown formatting with clear headers (##, ###)
    2. Format all tables properly with aligned columns using | characters
    3. Use bullet points (-) and numbered lists for better readability
    4. Include code blocks (```) for technical specifications when appropriate
    5. Ensure all sections are properly structured and easy to read
    6. DO NOT include user stories - focus on technical requirements and specifications
    7. Use consistent formatting throughout the document
    8. Make sure tables have proper headers and are well-aligned
    9. Use bold text (**text**) for emphasis on important points
    10. Structure the document with clear sections and subsections
    
    **SPECIAL TABLE FORMATTING RULES:**
    - Keep tables simple and readable (max 4-5 columns)
    - Use concise content in each cell (2-3 sentences max)
    - Break complex information into bullet points within cells
    - Ensure proper column alignment with | characters
    - Use clear, descriptive column headers
    - Avoid overly wide or complex tables
    - Split large tables into smaller, focused tables
    - Use consistent formatting across all tables
    - Prioritize readability over information density
    - Test table formatting for proper display
    """,
    
    "risk_assessment": """
    Conduct a risk assessment for the following P&C insurance scenario:
    
    {scenario_description}
    
    **Risk Assessment Framework:**
    {risk_template}
    
    Provide a comprehensive risk assessment with specific recommendations.
    Include quantitative and qualitative risk measures where applicable.
    """
}

class PCPromptEngine:
    def __init__(self):
        self.templates = P_C_ANALYSIS_TEMPLATES
        self.knowledge = P_C_INSURANCE_TEMPLATES
        self.prompts = P_C_PROMPT_TEMPLATES
    
    def create_analysis_prompt(self, document_content: str, lob: str) -> str:
        """Create specialized prompt for P&C insurance analysis"""
        lob_knowledge = self.knowledge.get(lob, {})
        
        # Get focus areas and other details
        focus_areas = ', '.join(lob_knowledge.get('analysis_focus', []))
        regulations = ', '.join(lob_knowledge.get('regulations', []))
        technical_considerations = ', '.join(lob_knowledge.get('technical_considerations', []))
        
        prompt = self.prompts["document_analysis"].format(
            lob=lob,
            focus_areas=focus_areas,
            regulations=regulations,
            technical_considerations=technical_considerations,
            document_content=document_content,
            analysis_template=self.templates['business_requirements']
        )
        
        return prompt
    
    def create_technical_prompt(self, analysis_results: str) -> str:
        """Create prompt for technical requirements generation"""
        prompt = self.prompts["technical_generation"].format(
            analysis_results=analysis_results,
            technical_template=self.templates['technical_requirements']
        )
        
        return prompt
    
    def create_risk_assessment_prompt(self, scenario_description: str) -> str:
        """Create prompt for risk assessment"""
        prompt = self.prompts["risk_assessment"].format(
            scenario_description=scenario_description,
            risk_template=self.templates['risk_assessment']
        )
        
        return prompt
    
    def get_lob_keywords(self, lob: str) -> List[str]:
        """Get keywords for a specific LOB"""
        return self.knowledge.get(lob, {}).get('keywords', [])
    
    def get_lob_requirements(self, lob: str) -> List[str]:
        """Get requirements for a specific LOB"""
        return self.knowledge.get(lob, {}).get('requirements', [])
    
    def classify_lob(self, text: str) -> str:
        """Classify the LOB based on text content"""
        text_lower = text.lower()
        max_matches = 0
        best_lob = "general_liability"  # default
        
        for lob, info in self.knowledge.items():
            keywords = info.get('keywords', [])
            matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            
            if matches > max_matches:
                max_matches = matches
                best_lob = lob
        
        return best_lob

# Test function
def test_pc_knowledge():
    """Test the P&C insurance knowledge base"""
    print("🧪 Testing P&C Insurance Knowledge Base...")
    
    engine = PCPromptEngine()
    
    # Test LOB classification
    test_text = "Personal auto insurance policy for a 35-year-old driver with clean record"
    classified_lob = engine.classify_lob(test_text)
    print(f"✅ LOB Classification: {classified_lob}")
    
    # Test prompt generation
    prompt = engine.create_analysis_prompt(test_text, classified_lob)
    print(f"✅ Generated prompt length: {len(prompt)} characters")
    
    # Test keywords
    keywords = engine.get_lob_keywords(classified_lob)
    print(f"✅ Keywords for {classified_lob}: {keywords[:3]}...")
    
    return {
        "classification": classified_lob,
        "prompt_length": len(prompt),
        "keywords_count": len(keywords)
    }

if __name__ == "__main__":
    test_pc_knowledge()
