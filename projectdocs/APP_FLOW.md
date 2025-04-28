# Application Flow for Traceit iOS App

This flow outlines the user journey from opening the app to viewing detailed results with community notes.

## 1. Launch & Splash

- User taps the Traceit icon on their iOS device
- Splash Screen: App displays the Traceit logo with a subtle animation while:
  - Initializing resources
  - Checking session status
- Once initialization completes, automatically transition to the Search screen

## 2. Search Screen

### Layout
- A single, prominent search bar centered vertically
- Placeholder Text: "Search a thought, post, or URL…"
- Back/Logout (if authenticated) or Settings icon in the top corner

### User Interaction
- User enters a query and taps the Search button or keyboard return key
- Loading Indicator appears in place of the search bar while the query is processed by the AI backend

## 3. Results List

### Display
- Vertically scrollable list of Result Cards
- Cards load progressively; skeleton placeholders fill in until content arrives

### Result Card Contents
- Page Title
- AI-generated description snippet
- Publication date
- Source URL (truncated)
- Creator/Author name
- Share icon/button

### Navigation
- User can scroll through and tap any card to view details

## 4. Detail View

### Header
- Full page title
- Publication date
- Author

### Content
- AI Description: Expanded AI-generated summary or context
- Full URL with copy-to-clipboard functionality
- Share Bar: System share sheet trigger for sharing the URL or summary

### Navigation
- Back button returns to the Results List

## 5. Community Notes

### Display
- Community Notes section lists notes attached to this semantic result
- Note Card Contents:
  - Username (or "Anonymous") badge
  - Timestamp
  - Note text
  - Upvote/Downvote controls

### Interaction
- Add Note button floats at the bottom-right
- Tapping opens a modal to submit a new note
- Submitted notes are sent to the backend, linked semantically to the current result
- New notes appear immediately with a "Pending review" badge if moderation is enabled

## 6. Optional: Semantic Clusters

### Future Enhancement
- After scrolling past the first few notes, suggest "See related searches" clusters
- Guides users to semantically similar thoughts

## End of Flow 