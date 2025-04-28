import SwiftUI

struct SearchView: View {
    @StateObject private var viewModel = SearchViewModel()
    @FocusState private var isSearchFieldFocused: Bool
    @EnvironmentObject private var appState: AppState
    
    var body: some View {
        VStack(spacing: 0) {
            searchBar
            
            if viewModel.isLoading {
                loadingView
            } else if viewModel.searchResults.isEmpty && !viewModel.searchText.isEmpty {
                emptyResultsView
            } else if viewModel.searchResults.isEmpty {
                searchHistoryView
            } else {
                resultsList
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
    }
    
    private var searchBar: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.gray)
            
            TextField("Search for a source", text: $viewModel.searchText)
                .textFieldStyle(.plain)
                .focused($isSearchFieldFocused)
                .onSubmit {
                    Task {
                        await viewModel.performSearch()
                    }
                }
            
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
        .padding(8)
        .background(Color(.systemGray6))
        .cornerRadius(10)
        .padding()
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