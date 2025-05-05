# Trace Project Specification

## 1. Overview
* Trace identifies the **earliest verifiable origin** of text, image, audio, or video content.
* Request types → credit weights:  
  * **Light (1 credit):** URL / ≤500‑char text  
  * **Heavy (3 credits):** image or audio‑only  
  * **Video (8 credits):** clips or YouTube links (paid tiers only)

## 2. High‑level flow
1. **Ingest** – Accept URL, raw text, image, audio, or video.  
2. **Canonical hash** – Generate SHA‑256 (text) or perceptual hash (media) → Redis cache lookup.  
3. **Router** –  
   * Run cheap lexical + pgvector search.  
   * *Only* call **Perplexity API** if combined recall < 3 hits OR confidence < 0.80.  
4. **Ranker** – Merge local + remote hits, score by timestamp × engagement × similarity.  
5. **Lineage write** – Store origin edge immediately; fan‑out multi‑hop graph in nightly batch job.  
6. **Return** JSON with: origin object, spread table, confidence, credit burn.

## 3. Media specifics
* **Image:** Brave Search API fallback → TinEye bulk batch each hour (deduped Bloom filter).  
* **Audio:** Self‑hosted Whisper *tiny‑en* CPU service, fallback to ACRCloud fingerprint for music.  
* **Video:**  
  1. Audio fingerprint first (fast).  
  2. If inconclusive, push Job ID to **batch GPU queue** (RunPod spot).  
  3. FFmpeg grabs 3 keyframes → CLIP embeddings → vector search.  
  4. Results streamed back via SSE/WebSocket when batch (~60 s) completes.

## 4. Caching & cost guards
* Redis (Upstash) for Perplexity + origin cache (TTL 30–90 d).  
* Batch GPU jobs & TinEye calls reduce per‑video COGS to ≈ $0.03–0.04.  
* Credit ledger in Postgres (Supabase) enforces free‑tier + paid quotas.

## 5. Logical build order (milestones)
1. Auth & credit meter, pgvector search, Redis + Perplexity router.  
2. Image reverse flow (Brave) + TinEye batch.  
3. Whisper service + audio pipeline.  
4. GPU batch infra (RunPod) + FFmpeg keyframe sampler.  
5. Video pipeline integration & SSE progress UI.  
6. Nightly lineage graph (Neo4j Aura) & spread‑view endpoint.  
7. Stripe usage billing hooks, push/email notifications, prod hardening.

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

### 3. Change Requests System
- **Features**:
  - Open contribution (any user can add notes)
  - Voting system
  - Automated content moderation
- **Note Resolution**:
  - Majority voting determines highlighted notes
  - Close votes result in no highlighting
  - Significant vote differences trigger highlighting
- **Additional Features**:
  - Change requests

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
4. Change requests system
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