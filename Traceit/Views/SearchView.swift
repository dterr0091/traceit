import SwiftUI

struct SearchView: View {
    @StateObject private var viewModel = SearchViewModel()
    @FocusState private var isSearchFieldFocused: Bool
    @EnvironmentObject private var appState: AppState
    
    var body: some View {
        NavigationView {
            ZStack(alignment: .bottom) {
                VStack(spacing: 0) {
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
                .background(Color.appMintCream)
                .padding(.bottom, 70) // Make room for search bar
                
                // Bottom Search Bar
                VStack(spacing: 0) {
                    Divider()
                    searchBar
                }
                .background(Color.white)
            }
            .navigationTitle("Search")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        appState.shouldShowOnboarding = true
                    }) {
                        Image(systemName: "questionmark.circle")
                            .foregroundColor(Color.appSmokyBlack)
                    }
                }
            }
        }
        .background(Color.appMintCream)
    }
    
    private var searchBar: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(Color.appSmokyBlack.opacity(0.6))
            
            TextField("Search...", text: $viewModel.searchText)
                .textFieldStyle(.plain)
                .font(.interRegular(size: 16))
                .focused($isSearchFieldFocused)
                .foregroundColor(Color.appSmokyBlack)
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
                        .foregroundColor(Color.appSmokyBlack.opacity(0.6))
                }
            }
        }
        .padding(12)
        .background(Color.appPlatinum)
        .cornerRadius(10)
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
    }
    
    private var loadingView: some View {
        VStack {
            ProgressView()
                .scaleEffect(1.5)
                .tint(Color.appSandyBrown)
            Text("Searching...")
                .font(.interRegular(size: 16))
                .foregroundColor(Color.appSmokyBlack.opacity(0.7))
                .padding(.top)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.appMintCream)
    }
    
    private var emptyResultsView: some View {
        VStack(spacing: 16) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 50))
                .foregroundColor(Color.appSandyBrown)
            Text("No results found")
                .font(.interBold(size: 18))
                .foregroundColor(Color.appSmokyBlack)
            Text("Try different keywords")
                .font(.interRegular(size: 16))
                .foregroundColor(Color.appSmokyBlack.opacity(0.7))
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.appMintCream)
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
                                .foregroundColor(Color.appSandyBrown)
                            Text(query)
                                .font(.interRegular(size: 16))
                                .foregroundColor(Color.appSmokyBlack)
                            Spacer()
                        }
                    }
                }
            }
            .listRowBackground(Color.white)
        }
        .background(Color.appMintCream)
    }
    
    private var resultsList: some View {
        List(viewModel.searchResults) { result in
            NavigationLink(destination: ResultDetailView(result: result)) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(result.title)
                        .font(.interBold(size: 17))
                        .foregroundColor(Color.appSmokyBlack)
                    Text(result.description)
                        .font(.interRegular(size: 15))
                        .foregroundColor(Color.appSmokyBlack.opacity(0.7))
                        .lineLimit(2)
                }
                .padding(.vertical, 4)
            }
            .listRowBackground(Color.white)
        }
        .background(Color.appMintCream)
    }
}

#Preview {
    SearchView()
        .environmentObject(AppState())
} 