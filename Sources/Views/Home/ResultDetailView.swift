import SwiftUI

struct ResultDetailView: View {
    let result: SearchResult
    @State private var comments: [Comment] = []
    @State private var newComment: String = ""
    
    private var dateFormatter: DateFormatter {
        let formatter = DateFormatter()
        formatter.dateFormat = "MMM d, yyyy 'at' h:mm a"
        return formatter
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Custom header
            HStack {
                Text("Details")
                    .font(.title)
                    .fontWeight(.bold)
                Spacer()
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(Color.white)
            
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    // Source info
                    Text(result.source)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    
                    Text(result.title)
                        .font(.title)
                        .fontWeight(.bold)
                    
                    HStack {
                        Text(result.author)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        
                        Text("•")
                            .foregroundColor(.secondary)
                        
                        Text(result.publishedDate, formatter: dateFormatter)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    
                    Text(result.description)
                        .font(.body)
                        .foregroundColor(.secondary)
                    
                    Link(destination: result.url) {
                        Text(result.url.absoluteString)
                            .foregroundColor(.blue)
                            .font(.subheadline)
                    }
                    
                    Divider()
                        .padding(.vertical)
                    
                    // Comments section
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Comments")
                            .font(.headline)
                            .fontWeight(.bold)
                        
                        if result.comments.isEmpty {
                            Text("No comments yet. Be the first to comment!")
                                .foregroundColor(.secondary)
                                .padding(.vertical)
                        } else {
                            ForEach(result.comments) { comment in
                                commentView(for: comment)
                            }
                        }
                        
                        // Add comment section
                        HStack {
                            TextField("Add your title...", text: $newComment)
                                .textFieldStyle(RoundedBorderTextFieldStyle())
                            
                            Button(action: addComment) {
                                Image(systemName: "paperplane.fill")
                                    .foregroundColor(.blue)
                            }
                            .disabled(newComment.isEmpty)
                        }
                        .padding(.top, 8)
                    }
                }
                .padding()
            }
            .frame(maxHeight: .infinity, alignment: .top)
        }
        .background(Color(UIColor.systemGroupedBackground))
    }
    
    private func commentView(for comment: Comment) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(comment.title)
                .font(.subheadline)
                .fontWeight(.medium)
            
            Text(comment.comment)
                .font(.caption)
                .foregroundColor(.secondary)
            
            Text(comment.isHelpful ? "Helpful" : "Not Helpful")
                .font(.caption)
                .foregroundColor(.blue)
            
            Divider()
        }
        .padding(.vertical, 4)
    }
    
    private func addComment() {
        guard !newComment.isEmpty else { return }
        
        let comment = Comment(
            id: UUID().uuidString,
            resultId: result.id,
            title: "Title",
            comment: newComment,
            isHelpful: true
        )
        
        // Note: we can't modify the result directly as it's immutable
        // This would need to be handled by a view model in a real app
        comments.append(comment)
        newComment = ""
        
        // TODO: Save comment to backend
    }
}

#Preview {
    ResultDetailView(result: SearchResult(
        id: "1",
        source: "Sample Source",
        title: "Sample Result",
        description: "This is a sample search result description that provides more details about the content.",
        author: "John Doe",
        publishedDate: Date(),
        url: URL(string: "https://example.com")!,
        comments: [
            Comment(id: "1", resultId: "1", title: "Title", comment: "Comment", isHelpful: true),
            Comment(id: "2", resultId: "1", title: "Title", comment: "Comment", isHelpful: true)
        ]
    ))
} 