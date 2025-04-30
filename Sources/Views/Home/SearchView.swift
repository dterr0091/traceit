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
            VStack {
                if viewModel.isLoading {
                    loadingView
                } else if viewModel.searchResults.isEmpty && !viewModel.searchText.isEmpty {
                    emptyResultsView
                } else if viewModel.searchResults.isEmpty {
                    searchHistoryView
                } else {
                    resultsList
                }
                
                // Spacer to push content up when drawer expands
                Spacer(minLength: searchDrawerHeight)
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
        List(viewModel.searchResults) { result in
            NavigationLink(destination: ResultDetailView(result: result)) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(result.title)
                        .font(.headline)
                    Text(result.description)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .lineLimit(2)
                }
                .padding(.vertical, 4)
            }
        }
    }
}

#Preview {
    SearchView()
} 