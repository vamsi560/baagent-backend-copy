# langchain_integration.py
# Advanced LangChain Integration for Business Analyst Agent

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

# LangChain Core
from langchain_core.prompts import PromptTemplate
try:
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# LangChain Memory
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory

# LangChain Tools and Agents
from langchain.tools import Tool, tool
from langchain.agents import AgentExecutor, create_openai_tools_agent

# Handle import differences between LangChain versions
try:
    from langchain.agents.format_scratchpad import format_log_to_messages
except ImportError:
    try:
        from langchain.agents.format_scratchpad import format_to_openai_tool_messages as format_log_to_messages
    except ImportError:
        format_log_to_messages = None

try:
    from langchain.agents.output_parsers import OpenAIToolsAgentOutputParser
except ImportError:
    OpenAIToolsAgentOutputParser = None

# LangChain Document Processing
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# LangChain Chains
from langchain.chains import LLMChain, SequentialChain, ConversationChain
try:
    from langchain.chains.question_answering import load_qa_chain
except ImportError:
    from langchain_community.chains.question_answering import load_qa_chain

try:
    from langchain.chains.summarize import load_summarize_chain
except ImportError:
    from langchain_community.chains.summarize import load_summarize_chain

# LangChain Callbacks
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager

# Custom imports
from database import get_db, Document, Analysis, embedding_model, PINECONE_ENABLED, pinecone_client, PINECONE_INDEX_NAME, search_vector_db
from config import GEMINI_API_KEY

class LangChainIntegration:
    """Advanced LangChain integration for enhanced AI capabilities"""
    
    def __init__(self):
        self.llm = None
        self.memory = None
        self.vector_store = None
        self.text_splitter = None
        self.setup_components()
    
    def setup_components(self):
        """Initialize LangChain components"""
        try:
            # Initialize text splitter for document processing
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            # Initialize embeddings
            if embedding_model:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'}
                )
            
            # Initialize memory
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            print("✅ LangChain components initialized successfully")
            
        except Exception as e:
            print(f"⚠️ LangChain initialization warning: {e}")
    
    def create_document_chain(self, document_type: str) -> LLMChain:
        """Create specialized document generation chains"""
        
        if document_type == "TRD":
            prompt = PromptTemplate(
                input_variables=["requirements", "context", "chat_history"],
                template="""
                You are an expert Technical Requirements Document writer with 20+ years of experience.
                
                Previous conversation context:
                {chat_history}
                
                Create a comprehensive Technical Requirements Document based on the following requirements:
                
                Requirements: {requirements}
                Additional Context: {context}
                
                Structure the document with:
                1. Executive Summary
                2. System Overview
                3. Functional Requirements
                4. Non-Functional Requirements
                5. Technical Specifications
                6. Security Considerations
                7. Deployment & Operations
                8. Testing Strategy
                
                Make it comprehensive, technical, and actionable for development teams.
                """
            )
        
        elif document_type == "HLD":
            prompt = PromptTemplate(
                input_variables=["requirements", "context", "chat_history"],
                template="""
                You are a Senior Solution Architect specializing in High-Level Design.
                
                Previous conversation context:
                {chat_history}
                
                Create a High-Level Design document based on:
                
                Requirements: {requirements}
                Additional Context: {context}
                
                Include:
                1. System Architecture Overview
                2. Component Diagram (Mermaid format)
                3. Technology Stack
                4. Integration Points
                5. Data Flow
                6. Security Architecture
                7. Scalability Considerations
                
                Focus on architectural decisions and system-level design.
                """
            )
        
        elif document_type == "LLD":
            prompt = PromptTemplate(
                input_variables=["requirements", "context", "chat_history"],
                template="""
                You are a Senior Software Architect specializing in Low-Level Design.
                
                Previous conversation context:
                {chat_history}
                
                Create a detailed Low-Level Design document based on:
                
                Requirements: {requirements}
                Additional Context: {context}
                
                Include:
                1. Detailed Component Design
                2. Database Schema
                3. API Specifications
                4. Class Diagrams (Mermaid format)
                5. Sequence Diagrams
                6. Error Handling
                7. Performance Optimizations
                
                Focus on implementation details and technical specifications.
                """
            )
        
        return LLMChain(
            llm=self._get_llm(),
            prompt=prompt,
            memory=self.memory,
            verbose=True
        )
    
    def create_analysis_chain(self) -> SequentialChain:
        """Create a sequential chain for comprehensive analysis"""
        
        # Step 1: Requirements Analysis
        requirements_prompt = PromptTemplate(
            input_variables=["input_text"],
            template="""
            Analyze the following business requirements and extract key information:
            
            {input_text}
            
            Extract:
            1. Business objectives
            2. Functional requirements
            3. Non-functional requirements
            4. User stories
            5. Technical constraints
            6. Integration requirements
            
            Provide a structured analysis in JSON format.
            """
        )
        
        # Step 2: Gap Analysis
        gap_prompt = PromptTemplate(
            input_variables=["requirements_analysis"],
            template="""
            Based on the requirements analysis, identify gaps and missing information:
            
            {requirements_analysis}
            
            Identify:
            1. Missing requirements
            2. Ambiguous specifications
            3. Technical risks
            4. Dependencies
            5. Assumptions made
            
            Provide a gap analysis report.
            """
        )
        
        # Step 3: Recommendations
        recommendations_prompt = PromptTemplate(
            input_variables=["requirements_analysis", "gap_analysis"],
            template="""
            Based on the requirements analysis and gap analysis, provide recommendations:
            
            Requirements Analysis: {requirements_analysis}
            Gap Analysis: {gap_analysis}
            
            Provide:
            1. Technical recommendations
            2. Architecture suggestions
            3. Risk mitigation strategies
            4. Implementation approach
            5. Timeline estimates
            
            Structure as actionable recommendations.
            """
        )
        
        # Create chains
        requirements_chain = LLMChain(
            llm=self._get_llm(),
            prompt=requirements_prompt,
            output_key="requirements_analysis"
        )
        
        gap_chain = LLMChain(
            llm=self._get_llm(),
            prompt=gap_prompt,
            output_key="gap_analysis"
        )
        
        recommendations_chain = LLMChain(
            llm=self._get_llm(),
            prompt=recommendations_prompt,
            output_key="recommendations"
        )
        
        # Combine into sequential chain
        return SequentialChain(
            chains=[requirements_chain, gap_chain, recommendations_chain],
            input_variables=["input_text"],
            output_variables=["requirements_analysis", "gap_analysis", "recommendations"],
            verbose=True
        )
    
    def create_qa_chain(self) -> Any:
        """Create a question-answering chain with document retrieval"""
        
        # Create retriever from vector store
        if self.vector_store:
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            # Create QA chain
            qa_chain = load_qa_chain(
                llm=self._get_llm(),
                chain_type="stuff",
                verbose=True
            )
            
            return qa_chain, retriever
        
        return None, None
    
    def create_summarization_chain(self) -> Any:
        """Create a document summarization chain"""
        
        return load_summarize_chain(
            llm=self._get_llm(),
            chain_type="map_reduce",
            verbose=True
        )
    
    def process_documents_with_langchain(self, documents: List[Dict]) -> Dict[str, Any]:
        """Process documents using LangChain for enhanced analysis"""
        
        results = {
            "summaries": [],
            "key_points": [],
            "questions": [],
            "recommendations": []
        }
        
        for doc in documents:
            # Split document into chunks
            chunks = self.text_splitter.split_text(doc.get('content', ''))
            
            # Create summarization chain
            summarize_chain = self.create_summarization_chain()
            
            # Generate summary
            if chunks:
                summary = summarize_chain.run(chunks)
                results["summaries"].append({
                    "document_id": doc.get('id'),
                    "summary": summary
                })
            
            # Extract key points
            key_points_prompt = PromptTemplate(
                input_variables=["text"],
                template="""
                Extract the key points from the following text:
                
                {text}
                
                Provide a list of key points in JSON format.
                """
            )
            
            key_points_chain = LLMChain(
                llm=self._get_llm(),
                prompt=key_points_prompt
            )
            
            key_points = key_points_chain.run(doc.get('content', ''))
            results["key_points"].append({
                "document_id": doc.get('id'),
                "key_points": key_points
            })
        
        return results
    
    def create_agent_with_tools(self) -> AgentExecutor:
        """Create an agent with custom tools for business analysis"""
        
        @tool
        def analyze_requirements(text: str) -> str:
            """Analyze business requirements and extract key information"""
            analysis_chain = self.create_analysis_chain()
            return analysis_chain.run({"input_text": text})
        
        @tool
        def generate_document(doc_type: str, requirements: str) -> str:
            """Generate technical documents (TRD, HLD, LLD)"""
            doc_chain = self.create_document_chain(doc_type)
            return doc_chain.run({
                "requirements": requirements,
                "context": "",
                "chat_history": ""
            })
        
        @tool
        def search_documents(query: str) -> str:
            """Search through stored documents for relevant information"""
            if self.vector_store:
                docs = self.vector_store.similarity_search(query, k=3)
                return "\n\n".join([doc.page_content for doc in docs])
            return "Vector store not available"
        
        @tool
        def create_backlog(requirements: str) -> str:
            """Create a project backlog from requirements"""
            backlog_prompt = PromptTemplate(
                input_variables=["requirements"],
                template="""
                Create a comprehensive project backlog from the following requirements:
                
                {requirements}
                
                Structure as:
                1. Epics
                2. Features
                3. User Stories
                4. Acceptance Criteria
                
                Provide in JSON format.
                """
            )
            
            backlog_chain = LLMChain(
                llm=self._get_llm(),
                prompt=backlog_prompt
            )
            
            return backlog_chain.run({"requirements": requirements})
        
        # Create tools list
        tools = [
            analyze_requirements,
            generate_document,
            search_documents,
            create_backlog
        ]
        
        # Create agent with fallback for missing imports
        try:
            if format_log_to_messages and OpenAIToolsAgentOutputParser:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are an expert Business Analyst Agent. Use the available tools to help analyze requirements and generate documents."),
                    ("human", "{input}"),
                    ("human", "{agent_scratchpad}")
                ])
                
                agent = create_openai_tools_agent(
                    llm=self._get_llm(),
                    tools=tools,
                    prompt=prompt
                )
                
                return AgentExecutor(
                    agent=agent,
                    tools=tools,
                    verbose=True,
                    memory=self.memory
                )
            else:
                # Fallback to simple agent creation
                from langchain.agents import initialize_agent, AgentType
                agent = initialize_agent(
                    tools=tools,
                    llm=self._get_llm(),
                    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                    verbose=True
                )
                return agent
        except Exception as e:
            print(f"⚠️ Agent creation failed: {e}")
            # Return a simple executor as fallback
            from langchain.agents import initialize_agent, AgentType
            agent = initialize_agent(
                tools=tools,
                llm=self._get_llm(),
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True
            )
            return agent
    
    def _get_llm(self):
        """Get LLM instance (placeholder for now)"""
        # This would be replaced with actual LLM initialization
        # For now, we'll use the existing Gemini integration
        return None
    
    def setup_vector_store(self, documents: List[Dict]):
        """Set up vector store with documents using Pinecone"""
        if not self.embeddings or not PINECONE_ENABLED or not pinecone_client:
            return
        
        try:
            # For Pinecone, we use our custom database functions
            # Documents are already stored via add_to_vector_db
            # This method is kept for compatibility but doesn't create a LangChain vector store
            print(f"SUCCESS: Vector store ready (using Pinecone)")
            
        except Exception as e:
            print(f"WARNING: Vector store setup failed: {e}")
    
    def search_similar_documents(self, query: str, lob: str = None, limit: int = 5):
        """Search for similar documents using Pinecone"""
        if not PINECONE_ENABLED:
            return []
        
        try:
            from database import search_vector_db
            results = search_vector_db(query, lob=lob, limit=limit)
            return results
        except Exception as e:
            print(f"WARNING: Vector search failed: {e}")
            return []
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history from memory"""
        if self.memory:
            return self.memory.chat_memory.messages
        return []
    
    def clear_memory(self):
        """Clear conversation memory"""
        if self.memory:
            self.memory.clear()

# Global instance
langchain_integration = LangChainIntegration()

