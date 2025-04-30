import SwiftUI

struct SearchView: View {
    @StateObject private var viewModel = SearchViewModel()
    @FocusState private var isSearchFieldFocused: Bool
    @EnvironmentObject private var appState: AppState
    @State private var searchDrawerHeight: CGFloat = 60
    @State private var textEditorHeight: CGFloat = 40
    @State private var keyboardHeight: CGFloat = 0
    
    var body: some View {
        ZStack(alignment: .bottom) {
            // Main content
            VStack(spacing: 0) {
                if viewModel.isLoading {
                    loadingView
                } else if viewModel.searchResults.isEmpty && !viewModel.searchText.isEmpty {
                    emptyResultsView
                } else if viewModel.searchResults.isEmpty {
                    searchHistoryView
                } else {
                    ScrollView {
                        VStack(spacing: 16) {
                            // Original Source section
                            if let firstResult = viewModel.searchResults.first {
                                VStack(alignment: .leading, spacing: 0) {
                                    Text("Original Source")
                                        .font(.headline)
                                        .padding(.horizontal, 16)
                                        .padding(.vertical, 8)
                                    
                                    HStack(alignment: .top, spacing: 12) {
                                        // Image placeholder
                                        Rectangle()
                                            .fill(Color.gray.opacity(0.2))
                                            .frame(width: 80, height: 80)
                                            .overlay(
                                                Image(systemName: "photo")
                                                    .foregroundColor(.gray)
                                            )
                                        
                                        VStack(alignment: .leading, spacing: 6) {
                                            Text(firstResult.source)
                                                .font(.subheadline)
                                                .foregroundColor(.secondary)
                                            
                                            Text(firstResult.title)
                                                .font(.headline)
                                            
                                            Text(firstResult.description)
                                                .font(.subheadline)
                                                .foregroundColor(.secondary)
                                            
                                            HStack(spacing: 4) {
                                                Text(firstResult.author)
                                                    .font(.caption)
                                                    .foregroundColor(.secondary)
                                                
                                                Text("•")
                                                    .font(.caption)
                                                    .foregroundColor(.secondary)
                                                
                                                Text(firstResult.publishedDate, formatter: dateFormatter)
                                                    .font(.caption)
                                                    .foregroundColor(.secondary)
                                            }
                                            
                                            Text(firstResult.url.absoluteString)
                                                .font(.caption)
                                                .foregroundColor(.blue)
                                        }
                                    }
                                    .padding(16)
                                    .background(Color.white)
                                    .cornerRadius(8)
                                    .padding(.horizontal)
                                }
                            }
                            
                            // Results list
                            resultsList
                            
                            // Search field indicator at bottom
                            HStack {
                                Text("Test")
                                    .padding(.vertical, 8)
                                    .padding(.horizontal, 12)
                                
                                Spacer()
                                
                                Button(action: {}) {
                                    Image(systemName: "xmark.circle.fill")
                                        .foregroundColor(.gray)
                                }
                            }
                            .padding(.horizontal)
                            .background(Color.white)
                            .cornerRadius(20)
                            .shadow(radius: 1)
                            .padding(.horizontal)
                            
                            // Upload button
                            HStack {
                                Spacer()
                                
                                Button(action: {}) {
                                    HStack {
                                        Image(systemName: "doc.fill")
                                        Text("Upload")
                                    }
                                    .padding(.vertical, 8)
                                    .padding(.horizontal, 16)
                                    .background(
                                        RoundedRectangle(cornerRadius: 20)
                                            .stroke(Color.black, lineWidth: 1)
                                    )
                                }
                            }
                            .padding(.horizontal)
                            .padding(.bottom, 16)
                        }
                        .padding(.bottom, searchDrawerHeight)
                    }
                }
            }
            .navigationTitle("Search")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        appState.shouldShowOnboarding = true
                    }) {
                        Image(systemName: "questionmark.circle")
                    }
                }
            }
            
            // Search drawer
            searchDrawer
        }
        .onAppear {
            NotificationCenter.default.addObserver(forName: UIResponder.keyboardWillShowNotification, object: nil, queue: .main) { notification in
                if let keyboardFrame = notification.userInfo?[UIResponder.keyboardFrameEndUserInfoKey] as? CGRect {
                    keyboardHeight = keyboardFrame.height
                }
            }
            
            NotificationCenter.default.addObserver(forName: UIResponder.keyboardWillHideNotification, object: nil, queue: .main) { _ in
                keyboardHeight = 0
            }
        }
    }
    
    private var searchDrawer: some View {
        VStack(spacing: 0) {
            // Drawer handle
            RoundedRectangle(cornerRadius: 2.5)
                .fill(Color.gray.opacity(0.5))
                .frame(width: 40, height: 5)
                .padding(.top, 8)
            
            // Search content
            VStack {
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(.gray)
                    
                    TextEditor(text: $viewModel.searchText)
                        .frame(height: max(40, min(120, textEditorHeight)))
                        .focused($isSearchFieldFocused)
                        .padding(.vertical, 4)
                        .background(
                            GeometryReader { geo in
                                Color.clear.onAppear {
                                    textEditorHeight = geo.size.height
                                }
                                .onChange(of: viewModel.searchText) { _ in
                                    textEditorHeight = geo.size.height
                                    updateDrawerHeight()
                                }
                            }
                        )
                        .scrollContentBackground(.hidden)
                    
                    if !viewModel.searchText.isEmpty {
                        Button(action: {
                            viewModel.clearSearch()
                            isSearchFieldFocused = false
                        }) {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(.gray)
                        }
                    }
                }
                
                Button("Search") {
                    Task {
                        await viewModel.performSearch()
                        isSearchFieldFocused = false
                    }
                }
                .padding(.vertical, 8)
                .padding(.horizontal, 16)
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(8)
                .padding(.top, 8)
            }
            .padding()
        }
        .frame(height: searchDrawerHeight)
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color(.systemGray6))
                .shadow(radius: 3)
        )
        .gesture(
            DragGesture()
                .onChanged { value in
                    let newHeight = searchDrawerHeight - value.translation.height
                    searchDrawerHeight = min(max(60, newHeight), UIScreen.main.bounds.height / 2)
                }
        )
    }
    
    private func updateDrawerHeight() {
        withAnimation(.spring()) {
            searchDrawerHeight = max(60, min(textEditorHeight + 100, UIScreen.main.bounds.height / 2))
        }
    }
    
    private var loadingView: some View {
        VStack {
            ProgressView()
                .scaleEffect(1.5)
            Text("Searching...")
                .foregroundColor(.secondary)
                .padding(.top)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    private var emptyResultsView: some View {
        VStack(spacing: 16) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 50))
                .foregroundColor(.secondary)
            Text("No results found")
                .font(.headline)
            Text("Try different keywords")
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    private var searchHistoryView: some View {
        List {
            Section("Recent Searches") {
                ForEach(viewModel.searchHistory, id: \.self) { query in
                    Button(action: {
                        viewModel.searchText = query
                        isSearchFieldFocused = true
                    }) {
                        HStack {
                            Image(systemName: "clock")
                                .foregroundColor(.secondary)
                            Text(query)
                            Spacer()
                        }
                    }
                }
            }
        }
    }
    
    private var resultsList: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Results header
            HStack {
                Text("Results")
                    .font(.headline)
                    .fontWeight(.bold)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
                Spacer()
            }
            .background(Color(.systemGroupedBackground))
            
            VStack(alignment: .leading, spacing: 0) {
                ForEach(viewModel.searchResults) { result in
                    VStack(alignment: .leading, spacing: 0) {
                        // Result item
                        NavigationLink(destination: ResultDetailView(result: result)) {
                            VStack(alignment: .leading, spacing: 8) {
                                Text(result.title)
                                    .font(.headline)
                                    .foregroundColor(.primary)
                                
                                Text(result.description)
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                            .padding(.horizontal, 16)
                            .padding(.vertical, 12)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(Color.white)
                        }
                        .buttonStyle(PlainButtonStyle())
                        
                        Divider()
                        
                        // Comments section
                        VStack(spacing: 0) {
                            ForEach(result.comments) { comment in
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(comment.title)
                                        .font(.subheadline)
                                        .fontWeight(.medium)
                                    Text(comment.comment)
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    Text("Helpful")
                                        .font(.caption)
                                        .foregroundColor(.blue)
                                }
                                .padding(.horizontal, 16)
                                .padding(.vertical, 12)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(Color(.systemGray6))
                            }
                        }
                    }
                    .background(Color.white)
                    .cornerRadius(8)
                    .padding(.bottom, 16)
                }
            }
            .padding(.horizontal)
        }
        .background(Color(.systemGroupedBackground))
    }
    
    private struct CommentSectionView: View {
        let resultId: String
        @State private var comments: [Comment] = []
        @State private var newComment: String = ""
        
        var body: some View {
            VStack(alignment: .leading, spacing: 8) {
                Text("Comments")
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                ForEach(comments) { comment in
                    HStack(alignment: .top) {
                        Image(systemName: "person.circle.fill")
                            .foregroundColor(.gray)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(comment.authorName)
                                .font(.caption)
                                .fontWeight(.medium)
                            
                            Text(comment.text)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding(.vertical, 2)
                }
                
                HStack {
                    TextField("Add a comment...", text: $newComment)
                        .font(.caption)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                    
                    Button(action: addComment) {
                        Image(systemName: "paperplane.fill")
                            .foregroundColor(.blue)
                            .font(.caption)
                    }
                    .disabled(newComment.isEmpty)
                }
                .padding(.top, 4)
            }
            .padding(.vertical, 4)
            .onAppear(perform: loadComments)
        }
        
        private func loadComments() {
            // Mock data for now, replace with real data loading
            comments = [
                Comment(id: "1", resultId: resultId, authorId: "user1", authorName: "User 1", text: "Great result!"),
                Comment(id: "2", resultId: resultId, authorId: "user2", authorName: "User 2", text: "This is helpful.")
            ]
        }
        
        private func addComment() {
            guard !newComment.isEmpty else { return }
            
            let comment = Comment(
                id: UUID().uuidString,
                resultId: resultId,
                authorId: "currentUser",
                authorName: "You",
                text: newComment
            )
            
            comments.append(comment)
            newComment = ""
            
            // TODO: Save comment to backend
        }
    }
    
    // Date formatter for displaying published date
    private var dateFormatter: DateFormatter {
        let formatter = DateFormatter()
        formatter.dateFormat = "MMM d, yyyy 'at' h:mm a"
        return formatter
    }
}

#Preview {
    SearchView()
} 