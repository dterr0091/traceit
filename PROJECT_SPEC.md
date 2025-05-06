# Trace Project Specification

## 1. Overview
* Trace identifies the **earliest verifiable origin** of text, image, audio, or video content.
* Request types → credit weights:  
  * **Light (1 credit):** URL / ≤500‑char text  
  * **Heavy (3 credits):** image or audio‑only  
  * **Video (8 credits):** clips or YouTube links (paid tiers only)
* Trace supports "Search Bundles" where a user attaches up to 5 artifacts (URLs, files, or raw text) under one `jobId`. Each artifact is processed independently, then an Aggregator merges the extracted claims/entities into a unified query before the Router step.

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
* **Video (composite‑aware pipeline):**  
  1. **Audio fingerprint first** – rapid CPU check via self‑hosted Whisper *tiny‑en* + ACRCloud.  
  2. **Always enqueue a 3‑frame batch job** (RunPod GPU) – frames sampled at 0 s, mid‑point, end via FFmpeg.  
  3. **Visual origin detection** – CLIP embeddings → pgvector search.  
  4. **Composite decision:**  
     * If ≥ 2 of 3 frames match the **same external source** (CLIP dist ≤ 0.20) **and** that source's `channelId` ≠ audio's `channelId`, mark the video **`isComposite = true`**.  
     * Store both `audioOrigin` and `visualOrigin` objects in the lineage graph.  
  5. **UI contract:**  
     * Return `origins: { audio?: OriginObj, visual?: OriginObj }`.  
     * Front‑end shows stacked cards: "Visuals from X (date)" + "Voice‑over by Y (date)".  
  6. **Cost guard:** If audio *and* first‑frame MD5 share the **same** channel, cancel GPU batch to save cost.

## 4. Caching & cost guards
* Redis (Upstash) for Perplexity + origin cache (TTL 30–90 d).  
* Batch GPU jobs & TinEye calls reduce per‑video COGS to ≈ $0.03–0.04.  
* Credit ledger in Postgres (Supabase) enforces free‑tier + paid quotas.
* Composite videos add ≤ $0.01 per search (extra CLIP embeds); hit rate ≈ 20 % of all video searches.
* Each extra image artifact adds ≈ $0.001 (OCR + embed); negligible versus video COGS.
* Sonar Standard probe = $0.01 per 1 M tok; Pro escalation only on low‑confidence misses.

## 5. Perplexity‑powered features

1. **Canonical claim generator**  
   *Use Sonar Pro (`structured=true`) to normalize messy snippets into one `canonical_claim` + `key_entities[]`. Cuts duplicate vector inserts.*

2. **First‑seen timestamp cross‑check**  
   *Query Sonar's crawl for earliest public‑web date; flag discrepancies with our lineage graph.*

3. **Domain‑scoped re‑ranking**  
   *Expose UI toggles ("Academic", "News", "Social") → pass `search_domain:"..."` param to Sonar.*

4. **Composite‑video reasoning**  
   *Single Sonar prompt checks if audio creator = visual creator; overrides heuristic when confidence ≥ 0.9.*

5. **Trending‑spread snapshots**  
   *Nightly job: send 50 newest claims → store top‑3 citations for external spread view.*

6. **Cost‑killer router**  
   *Call cheap `model:"sonar"` first; escalate to Sonar Pro only if < 3 citations or `<0.80` confidence. Expected 40‑60 % Perplexity cost reduction.*

7. **Explain‑why UI**  
   *Surface Sonar citations as hover cards; zero extra scraping.*

## 6. Logical build order (milestones)
1. Auth & credit meter, pgvector search, Redis + Perplexity router.  
2. Image reverse flow (Brave) + TinEye batch.  
3. Implement Session / Bundle model and Aggregator function (OCR + entity merge)
4. Whisper service + audio pipeline.  
5. GPU batch infra (RunPod) + FFmpeg keyframe sampler.  
6. Video pipeline integration & SSE progress UI.  
7. Implement composite‑media checker (audio vs visual origin reconciliation)
8. Nightly lineage graph (Neo4j Aura) & spread‑view endpoint.  
9. Stripe usage billing hooks, push/email notifications, prod hardening.

**Weekly implementation schedule:**
- **Week 1** – Integrate *Canonical claim generator* + *Cost‑killer router*.  
- **Week 2** – Add *Domain‑scoped re‑ranking* toggle.  
- **Week 3** – Implement *Composite‑video reasoning* via Sonar prompt.  
- **Week 4** – Schedule *Trending‑spread snapshot* nightly cron.  
- **Week 4** – Add *Explain‑why UI* hover cards (uses Sonar citations—no extra backend).

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