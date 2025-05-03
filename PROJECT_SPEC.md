# Source Trace Project Specification

## Overview
A web application that traces the origin and spread of content across multiple platforms, using AI to evaluate and determine the most likely original source and key viral points.

## Core Features

### 1. Search Functionality
- **Input Types**:
  - Text search
  - Image upload
  - URL submission
- **Trigger**:
  - "Trace" button click
  - Enter key press
- **Search Scope**:
  - Unified search across web, social media, and news sources via Perplexity Sonar API
  - Default limit of 4 surfaced URLs per query

### 2. Source Analysis
- **AI Engine**: OpenAI integration for source evaluation
- **Output**:
  - Original source identification
  - Top 3 viral points
  - AI-generated explanation for disputed sources
- **Virality Metrics**:
  - Engagement metrics
  - Visit counts
  - Platform-specific metrics

### 3. Community Notes System
- **Features**:
  - Open contribution (any user can add notes)
  - Voting system
  - Automated content moderation
- **Note Resolution**:
  - Majority voting determines highlighted notes
  - Close votes result in no highlighting
  - Significant vote differences trigger highlighting

## Technical Architecture

### Frontend
- **Framework**: React with TypeScript
- **State Management**: Redux Toolkit
- **API Integration**: Axios
- **Form Handling**: React Hook Form
- **UI Components**: Custom components with Subframe

### Backend
- **API Layer**: FastAPI
- **Database**: PostgreSQL with JSONB support
- **ORM**: SQLAlchemy
- **Data Validation**: Pydantic V2
- **Authentication**: JWT

### Data Storage
- **Primary Database**: PostgreSQL
  - Content metadata
  - User data
  - Community notes
  - Voting records
- **File Storage**: AWS S3
  - Uploaded images
  - Cached content

### External Integrations
- **OpenAI API**: Core LLM for multimodal understanding and orchestration
- **Perplexity Sonar API**: Unified retrieval layer for real-time web, social, and news content
- **Diffbot API**: Optional full-text extraction for selected URLs

## Development Approach

### Testing
- Test-Driven Development (TDD)
- pytest for backend testing
- React Testing Library for frontend testing
- Jest for JavaScript/TypeScript testing

### Code Quality
- PEP 8 compliance
- Type hints
- Comprehensive docstrings
- Black for code formatting
- Flake8 for linting

### Security
- Environment variables for sensitive data
- Parameterized queries
- Input validation
- Rate limiting
- Automated content moderation

## Implementation Phases

### Phase 1
1. Basic search functionality
2. OpenAI integration
3. Perplexity Sonar API integration
4. Community notes system
5. Basic UI implementation

### Phase 2
1. Data visualization
2. Advanced filtering
3. Sorting capabilities
4. Enhanced moderation tools
5. Cost/latency optimization (caching Sonar results, selective Diffbot fetching)

## Future Considerations
- User roles and permissions
- Advanced analytics
- Machine learning for source verification
- Real-time content tracking 