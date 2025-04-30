import SwiftUI

struct CommentSection: View {
    @ObservedObject var viewModel: CommentViewModel
    @FocusState private var isCommentFieldFocused: Bool
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Comments")
                .font(.interBold(size: 18))
                .foregroundColor(Color.appSmokyBlack)
            
            if viewModel.comments.isEmpty {
                Text("No comments yet. Be the first to comment!")
                    .font(.interRegular(size: 14))
                    .foregroundColor(Color.appSmokyBlack.opacity(0.6))
                    .padding(.vertical, 8)
            } else {
                // Comment list
                ForEach(viewModel.comments) { comment in
                    CommentRow(comment: comment)
                    
                    if comment.id != viewModel.comments.last?.id {
                        Divider()
                            .background(Color.appSmokyBlack.opacity(0.1))
                    }
                }
            }
            
            // New comment input
            VStack(spacing: 8) {
                HStack(alignment: .top) {
                    // User avatar placeholder
                    Circle()
                        .fill(Color.appSandyBrown.opacity(0.5))
                        .frame(width: 36, height: 36)
                        .overlay(
                            Image(systemName: "person.fill")
                                .foregroundColor(Color.white)
                        )
                    
                    // Comment text field
                    ZStack(alignment: .topLeading) {
                        if viewModel.newCommentText.isEmpty {
                            Text("Add a comment...")
                                .font(.interRegular(size: 14))
                                .foregroundColor(Color.appSmokyBlack.opacity(0.4))
                                .padding(.top, 8)
                                .padding(.leading, 8)
                        }
                        
                        TextEditor(text: $viewModel.newCommentText)
                            .font(.interRegular(size: 14))
                            .foregroundColor(Color.appSmokyBlack)
                            .frame(minHeight: 80, maxHeight: 120)
                            .focused($isCommentFieldFocused)
                            .padding(4)
                            .background(Color.white)
                    }
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.appSmokyBlack.opacity(0.2), lineWidth: 1)
                    )
                }
                
                HStack {
                    Spacer()
                    Button(action: {
                        viewModel.addComment()
                        isCommentFieldFocused = false
                    }) {
                        Text("Post")
                            .font(.interMedium(size: 14))
                            .foregroundColor(.white)
                            .padding(.vertical, 8)
                            .padding(.horizontal, 16)
                            .background(viewModel.newCommentText.isEmpty ? Color.gray : Color.appSandyBrown)
                            .cornerRadius(20)
                    }
                    .disabled(viewModel.newCommentText.isEmpty)
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.appSmokyBlack.opacity(0.05), radius: 5, x: 0, y: 2)
    }
}

struct CommentRow: View {
    let comment: Comment
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            // User avatar
            if let avatar = comment.avatarImage {
                Image(uiImage: avatar)
                    .resizable()
                    .scaledToFill()
                    .frame(width: 36, height: 36)
                    .clipShape(Circle())
            } else {
                Circle()
                    .fill(Color.appSandyBrown.opacity(0.5))
                    .frame(width: 36, height: 36)
                    .overlay(
                        Image(systemName: "person.fill")
                            .foregroundColor(Color.white)
                    )
            }
            
            VStack(alignment: .leading, spacing: 4) {
                // Author and timestamp
                HStack {
                    Text(comment.author)
                        .font(.interMedium(size: 14))
                        .foregroundColor(Color.appSmokyBlack)
                    
                    Spacer()
                    
                    Text(timeAgo(from: comment.timestamp))
                        .font(.interRegular(size: 12))
                        .foregroundColor(Color.appSmokyBlack.opacity(0.5))
                }
                
                // Comment text
                Text(comment.text)
                    .font(.interRegular(size: 14))
                    .foregroundColor(Color.appSmokyBlack.opacity(0.8))
                    .fixedSize(horizontal: false, vertical: true)
                
                // Action buttons
                HStack(spacing: 16) {
                    Button(action: {}) {
                        Label("Like", systemImage: "hand.thumbsup")
                            .font(.interRegular(size: 12))
                            .foregroundColor(Color.appSmokyBlack.opacity(0.6))
                    }
                    
                    Button(action: {}) {
                        Label("Reply", systemImage: "arrowshape.turn.up.left")
                            .font(.interRegular(size: 12))
                            .foregroundColor(Color.appSmokyBlack.opacity(0.6))
                    }
                }
                .padding(.top, 4)
            }
        }
        .padding(.vertical, 8)
    }
    
    // Helper function to format the timestamp as a relative time string
    private func timeAgo(from date: Date) -> String {
        let calendar = Calendar.current
        let now = Date()
        let components = calendar.dateComponents([.minute, .hour, .day], from: date, to: now)
        
        if let day = components.day, day > 0 {
            return day == 1 ? "1 day ago" : "\(day) days ago"
        } else if let hour = components.hour, hour > 0 {
            return hour == 1 ? "1 hour ago" : "\(hour) hours ago"
        } else if let minute = components.minute, minute > 0 {
            return minute == 1 ? "1 minute ago" : "\(minute) minutes ago"
        } else {
            return "Just now"
        }
    }
}

#Preview {
    CommentSection(viewModel: CommentViewModel(resultId: "1"))
        .padding()
        .background(Color.appMintCream)
} 