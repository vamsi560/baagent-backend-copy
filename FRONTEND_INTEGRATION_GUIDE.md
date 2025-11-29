# Frontend Integration Guide

This guide outlines the changes needed in the frontend workspace to align with the backend updates.

## Summary of Backend Changes

1. ✅ **Removed OneDrive Integration** - All OneDrive endpoints removed
2. ✅ **Replaced Qdrant with Pinecone** - Vector database changed (backend-only, no frontend impact)
3. ✅ **Added TRD Section Selection** - New feature to select specific TRD sections
4. ✅ **Personal Auto LOB Focus** - Vector search supports LOB filtering

---

## 1. Remove OneDrive Integration from Frontend

### API Endpoints Removed (Do NOT call these):
- `GET /api/integrations/onedrive/status`
- `GET /api/integrations/onedrive/auth`
- `GET /api/integrations/onedrive/callback`
- `GET /api/integrations/onedrive/files`
- `GET /api/integrations/onedrive/download/<file_id>`
- `POST /api/integrations/onedrive/upload`

### Frontend Changes Required:

#### 1.1 Remove OneDrive UI Components
- Remove any OneDrive connection buttons/modals
- Remove OneDrive file browser components
- Remove OneDrive upload/download buttons
- Remove OneDrive status indicators

#### 1.2 Remove OneDrive API Service Calls
```typescript
// REMOVE these functions from your API service file:

// ❌ REMOVE
async getOneDriveStatus() { ... }
async getOneDriveAuthUrl() { ... }
async handleOneDriveCallback(code: string) { ... }
async getOneDriveFiles() { ... }
async downloadOneDriveFile(fileId: string) { ... }
async uploadToOneDrive(file: File) { ... }
```

#### 1.3 Update Integration Status Check
```typescript
// UPDATE your integration status API call
// The response will NO LONGER include onedrive_integration

// Before:
interface IntegrationStatus {
  onedrive_integration: boolean;  // ❌ REMOVE
  azure_devops: boolean;
}

// After:
interface IntegrationStatus {
  azure_devops: boolean;
  pinecone: boolean;  // ✅ NEW (optional, for status display)
}
```

---

## 2. Add TRD Section Selection Feature

### New API Endpoint

#### Get Available TRD Sections
```typescript
// GET /api/trd/sections
// Returns list of available TRD sections

interface TRDSection {
  key: string;
  title: string;
  description: string;
}

// Example Response:
{
  "sections": [
    {
      "key": "executive_summary",
      "title": "Executive Summary",
      "description": "Project overview, objectives, success criteria"
    },
    {
      "key": "system_overview",
      "title": "System Overview",
      "description": "Architecture, components, technology stack"
    },
    {
      "key": "functional_requirements",
      "title": "Functional Requirements",
      "description": "User stories, business rules, workflows"
    },
    {
      "key": "non_functional_requirements",
      "title": "Non-Functional Requirements",
      "description": "Performance, security, scalability"
    },
    {
      "key": "data_requirements",
      "title": "Data Requirements",
      "description": "Data models, storage, integration"
    },
    {
      "key": "security_requirements",
      "title": "Security Requirements",
      "description": "Authentication, authorization, compliance"
    },
    {
      "key": "integration_requirements",
      "title": "Integration Requirements",
      "description": "External systems, APIs, data exchange"
    },
    {
      "key": "testing_requirements",
      "title": "Testing Requirements",
      "description": "Test strategy, test cases, acceptance criteria"
    },
    {
      "key": "deployment_requirements",
      "title": "Deployment Requirements",
      "description": "Infrastructure, deployment process, rollback"
    },
    {
      "key": "maintenance_requirements",
      "title": "Maintenance Requirements",
      "description": "Monitoring, logging, support"
    }
  ]
}
```

### Frontend Implementation

#### 2.1 Create TRD Section Selector Component

```typescript
// components/TRDSectionSelector.tsx

import React, { useState, useEffect } from 'react';

interface TRDSection {
  key: string;
  title: string;
  description: string;
}

interface TRDSectionSelectorProps {
  selectedSections: string[];
  onChange: (sections: string[]) => void;
}

export const TRDSectionSelector: React.FC<TRDSectionSelectorProps> = ({
  selectedSections,
  onChange
}) => {
  const [sections, setSections] = useState<TRDSection[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTRDSections();
  }, []);

  const fetchTRDSections = async () => {
    try {
      const response = await fetch('/api/trd/sections');
      const data = await response.json();
      setSections(data.sections || []);
    } catch (error) {
      console.error('Failed to fetch TRD sections:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = (sectionKey: string) => {
    if (selectedSections.includes(sectionKey)) {
      onChange(selectedSections.filter(k => k !== sectionKey));
    } else {
      onChange([...selectedSections, sectionKey]);
    }
  };

  const handleSelectAll = () => {
    onChange(sections.map(s => s.key));
  };

  const handleDeselectAll = () => {
    onChange([]);
  };

  if (loading) {
    return <div>Loading sections...</div>;
  }

  return (
    <div className="trd-section-selector">
      <div className="section-selector-header">
        <h3>Select TRD Sections to Generate</h3>
        <div className="selector-actions">
          <button onClick={handleSelectAll}>Select All</button>
          <button onClick={handleDeselectAll}>Deselect All</button>
        </div>
      </div>
      
      <div className="sections-list">
        {sections.map((section) => (
          <div
            key={section.key}
            className={`section-item ${selectedSections.includes(section.key) ? 'selected' : ''}`}
            onClick={() => handleToggle(section.key)}
          >
            <input
              type="checkbox"
              checked={selectedSections.includes(section.key)}
              onChange={() => handleToggle(section.key)}
            />
            <div className="section-info">
              <h4>{section.title}</h4>
              <p>{section.description}</p>
            </div>
          </div>
        ))}
      </div>
      
      {selectedSections.length === 0 && (
        <div className="warning">
          ⚠️ Please select at least one section to generate
        </div>
      )}
    </div>
  );
};
```

#### 2.2 Update TRD Generation API Call

```typescript
// services/documentService.ts

// UPDATE the generate TRD function
async generateTRD(
  projectId: string,
  documentIds: string[],
  textInputIds: string[],
  selectedSections?: string[]  // ✅ NEW parameter
) {
  const formData = new FormData();
  
  // Add existing fields
  formData.append('document_ids', JSON.stringify(documentIds));
  formData.append('text_input_ids', JSON.stringify(textInputIds));
  
  // ✅ ADD selected sections
  if (selectedSections && selectedSections.length > 0) {
    formData.append('selected_sections', JSON.stringify(selectedSections));
  }
  
  const response = await fetch('/api/generate', {
    method: 'POST',
    body: formData
  });
  
  return response.json();
}

// OR for project analysis endpoint:
async analyzeProject(
  projectId: string,
  analysisType: 'trd' | 'hld' | 'lld',
  documentIds: string[],
  textInputIds: string[],
  selectedSections?: string[]  // ✅ NEW parameter
) {
  const response = await fetch(`/api/projects/${projectId}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`
    },
    body: JSON.stringify({
      type: analysisType,
      document_ids: documentIds,
      text_input_ids: textInputIds,
      selected_sections: selectedSections  // ✅ NEW field
    })
  });
  
  return response.json();
}
```

#### 2.3 Update TRD Generation UI

```typescript
// pages/GenerateTRD.tsx or similar

import { TRDSectionSelector } from '../components/TRDSectionSelector';

const GenerateTRDPage = () => {
  const [selectedSections, setSelectedSections] = useState<string[]>([]);
  const [generating, setGenerating] = useState(false);
  
  const handleGenerate = async () => {
    if (selectedSections.length === 0) {
      alert('Please select at least one section');
      return;
    }
    
    setGenerating(true);
    try {
      const result = await documentService.generateTRD(
        projectId,
        documentIds,
        textInputIds,
        selectedSections  // ✅ Pass selected sections
      );
      
      // Handle result...
    } catch (error) {
      console.error('Failed to generate TRD:', error);
    } finally {
      setGenerating(false);
    }
  };
  
  return (
    <div>
      <h1>Generate Technical Requirements Document</h1>
      
      {/* ✅ ADD section selector */}
      <TRDSectionSelector
        selectedSections={selectedSections}
        onChange={setSelectedSections}
      />
      
      <button
        onClick={handleGenerate}
        disabled={generating || selectedSections.length === 0}
      >
        {generating ? 'Generating...' : 'Generate TRD'}
      </button>
    </div>
  );
};
```

---

## 3. Update API Service Files

### 3.1 Remove OneDrive Service

```typescript
// services/integrationService.ts

// ❌ REMOVE entire OneDrive service class
class OneDriveService {
  // ... remove all methods
}

// ✅ KEEP only Azure DevOps service
class AzureDevOpsService {
  // ... existing methods
}
```

### 3.2 Update Integration Manager

```typescript
// services/integrationService.ts

class IntegrationManager {
  // ❌ REMOVE
  // getOneDriveStatus()
  // connectOneDrive()
  // getOneDriveFiles()
  
  // ✅ KEEP
  async getAzureDevOpsStatus() { ... }
  async connectAzureDevOps(orgUrl: string, patToken: string) { ... }
}
```

---

## 4. Update Environment Variables

### Remove OneDrive Environment Variables

```bash
# ❌ REMOVE from .env file
ONEDRIVE_CLIENT_ID=
ONEDRIVE_CLIENT_SECRET=
ONEDRIVE_TENANT_ID=
ONEDRIVE_REDIRECT_URI=
```

### Optional: Add Pinecone Status (if displaying)

```bash
# ✅ OPTIONAL - for status display only
PINECONE_ENABLED=true
```

---

## 5. Update Type Definitions

```typescript
// types/integrations.ts

// ❌ REMOVE
interface OneDriveIntegration {
  enabled: boolean;
  connected: boolean;
  files?: OneDriveFile[];
}

// ✅ UPDATE
interface IntegrationStatus {
  azure_devops: {
    enabled: boolean;
    connected: boolean;
  };
  pinecone?: {
    enabled: boolean;  // Optional, for status display
  };
}

// ✅ ADD
interface TRDSection {
  key: string;
  title: string;
  description: string;
}

interface TRDGenerationRequest {
  project_id: string;
  document_ids: string[];
  text_input_ids: string[];
  selected_sections?: string[];  // ✅ NEW
  analysis_type?: 'trd' | 'hld' | 'lld';
}
```

---

## 6. Testing Checklist

### OneDrive Removal
- [ ] Verify no OneDrive UI components are visible
- [ ] Verify no OneDrive API calls are made
- [ ] Verify integration status doesn't show OneDrive
- [ ] Test that file upload still works (local upload only)

### TRD Section Selection
- [ ] Verify `/api/trd/sections` endpoint returns sections
- [ ] Verify section selector component displays correctly
- [ ] Verify "Select All" / "Deselect All" buttons work
- [ ] Verify at least one section must be selected
- [ ] Verify selected sections are sent in API request
- [ ] Verify TRD generation only includes selected sections
- [ ] Test with different section combinations

### Integration
- [ ] Verify Azure DevOps integration still works
- [ ] Verify no errors in browser console
- [ ] Verify API calls use correct endpoints

---

## 7. Example Complete Integration

```typescript
// Complete example: TRD Generation with Section Selection

import React, { useState, useEffect } from 'react';
import { TRDSectionSelector } from '../components/TRDSectionSelector';
import { documentService } from '../services/documentService';

const TRDGenerationPage: React.FC = () => {
  const [selectedSections, setSelectedSections] = useState<string[]>([]);
  const [projectId, setProjectId] = useState<string>('');
  const [documentIds, setDocumentIds] = useState<string[]>([]);
  const [textInputIds, setTextInputIds] = useState<string[]>([]);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleGenerate = async () => {
    if (selectedSections.length === 0) {
      alert('Please select at least one TRD section');
      return;
    }

    setGenerating(true);
    try {
      const response = await documentService.analyzeProject(
        projectId,
        'trd',
        documentIds,
        textInputIds,
        selectedSections  // ✅ Pass selected sections
      );

      if (response.success) {
        setResult(response);
      } else {
        alert('Failed to generate TRD: ' + response.message);
      }
    } catch (error) {
      console.error('Error generating TRD:', error);
      alert('An error occurred while generating TRD');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="trd-generation-page">
      <h1>Generate Technical Requirements Document</h1>
      
      {/* Section Selector */}
      <TRDSectionSelector
        selectedSections={selectedSections}
        onChange={setSelectedSections}
      />
      
      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={generating || selectedSections.length === 0}
        className="generate-button"
      >
        {generating ? 'Generating TRD...' : 'Generate TRD'}
      </button>
      
      {/* Results */}
      {result && (
        <div className="trd-result">
          <h2>Generated TRD</h2>
          <pre>{result.trd}</pre>
        </div>
      )}
    </div>
  );
};

export default TRDGenerationPage;
```

---

## 8. Migration Steps

1. **Remove OneDrive Code**
   - Search for "onedrive" (case-insensitive) in your frontend codebase
   - Remove all OneDrive-related components, services, and API calls
   - Update integration status displays

2. **Add TRD Section Selection**
   - Create `TRDSectionSelector` component
   - Add API service method to fetch sections
   - Update TRD generation forms to include section selector
   - Update API calls to include `selected_sections` parameter

3. **Test Thoroughly**
   - Test TRD generation with different section combinations
   - Verify no OneDrive references remain
   - Verify all existing functionality still works

4. **Update Documentation**
   - Update user guides to reflect section selection feature
   - Remove OneDrive integration documentation

---

## Support

If you encounter any issues during integration, check:
1. Browser console for API errors
2. Network tab to verify correct API calls
3. Backend logs for request/response details

For questions, refer to the backend API documentation or contact the development team.

