# Database Schema for Traceit iOS App

This schema supports user searches, semantic AI processing, result cards, and community notes on semantically linked searches.

## Tables

### 1. users
- `id` (UUID, Primary Key)
- `email` (String, Unique, Not Null)
- `name` (String)
- `password_hash` (String)
- `created_at` (Timestamp, Not Null)
- `updated_at` (Timestamp)

### 2. searches
Stores each time a user searches for a query.
- `id` (UUID, Primary Key)
- `user_id` (Foreign Key → users.id, Not Null)
- `query_text` (Text, Not Null)
- `input_type` (Enum: 'social_media', 'news_site', 'text', Not Null)
- `status` (Enum: 'pending', 'completed', 'error', Not Null)
- `error_message` (Text, Nullable)
- `created_at` (Timestamp, Not Null)
- `completed_at` (Timestamp, Nullable)

### 3. semantic_concepts
Represents the canonical concepts extracted or clustered from searches for linking.
- `id` (UUID, Primary Key)
- `concept_text` (Text, Not Null)
- `embedding` (Vector/BLOB, Nullable)
- `created_at` (Timestamp, Not Null)

### 4. search_concepts
Links searches to the semantic_concepts they belong to.
- `id` (UUID, Primary Key)
- `search_id` (Foreign Key → searches.id, Not Null)
- `concept_id` (Foreign Key → semantic_concepts.id, Not Null)
- `similarity_score` (Float, Not Null)

### 5. results
Each result card returned for a search.
- `id` (UUID, Primary Key)
- `search_id` (Foreign Key → searches.id, Not Null)
- `page_title` (String, Not Null)
- `ai_description` (Text, Not Null)
- `published_at` (Timestamp, Not Null)
- `url` (Text, Not Null)
- `creator_id` (Foreign Key → creators.id, Nullable)
- `first_seen_at` (Timestamp, Nullable)
- `most_viral` (Boolean, Default: false)
- `created_at` (Timestamp, Not Null)

### 6. creators
Stores metadata about the original authors or publishers.
- `id` (UUID, Primary Key)
- `name` (String, Not Null)
- `profile_url` (Text, Nullable)
- `source_type` (Enum: 'social_media', 'news_site', 'other', Not Null)
- `created_at` (Timestamp, Not Null)

### 7. community_notes
User annotations on a semantic concept cluster.
- `id` (UUID, Primary Key)
- `concept_id` (Foreign Key → semantic_concepts.id, Not Null)
- `user_id` (Foreign Key → users.id, Not Null)
- `note_text` (Text, Not Null)
- `created_at` (Timestamp, Not Null)
- `updated_at` (Timestamp)

### 8. shares
Tracks share actions from result cards.
- `id` (UUID, Primary Key)
- `result_id` (Foreign Key → results.id, Not Null)
- `user_id` (Foreign Key → users.id, Nullable)
- `platform` (Enum: 'twitter', 'facebook', 'email', 'other')
- `created_at` (Timestamp, Not Null)

## Indexes & Constraints

### Unique Constraints
- Unique(user_id, query_text) on searches to dedupe repeated queries

### Indexes
- Index on semantic_concepts.embedding for vector similarity searches
- Composite index on search_concepts(concept_id, similarity_score DESC) for fast concept retrieval

### Foreign Key Constraints
- All foreign key constraints include ON DELETE CASCADE for dependent records 