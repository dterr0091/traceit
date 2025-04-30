import SwiftUI

@MainActor
final class SearchViewModel: ObservableObject {
    @Published var searchText = ""
    @Published var searchResults: [SearchResult] = []
    @Published var isLoading = false
    @Published var error: Error?
    @Published var searchHistory: [String] = []
    
    private let maxHistoryItems = 10
    private let networkService: NetworkServiceProtocol
    
    init(networkService: NetworkServiceProtocol = NetworkService()) {
        self.networkService = networkService
        loadSearchHistory()
    }
    
    func performSearch() async {
        guard !searchText.isEmpty else { return }
        
        isLoading = true
        error = nil
        
        do {
            // TODO: Replace with actual API call
            try await Task.sleep(nanoseconds: 1_000_000_000) // Simulated delay
            
            // Current date for the timestamp
            let currentDate = Date()
            
            // Create sample comments
            let commentsForResult1 = [
                Comment(id: "1", resultId: "1", title: "Title", comment: "Comment", isHelpful: true),
                Comment(id: "2", resultId: "1", title: "Title", comment: "Comment", isHelpful: true)
            ]
            
            let commentsForResult2 = [
                Comment(id: "3", resultId: "2", title: "Title", comment: "Comment", isHelpful: true),
                Comment(id: "4", resultId: "2", title: "Title", comment: "Comment", isHelpful: true)
            ]
            
            searchResults = [
                SearchResult(
                    id: "1",
                    source: "Source 1",
                    title: "Sample Result 1",
                    description: "Description 1",
                    author: "Author 1",
                    publishedDate: currentDate,
                    url: URL(string: "https://example.com")!,
                    comments: commentsForResult1
                ),
                SearchResult(
                    id: "2",
                    source: "Source 2",
                    title: "Sample Result 2",
                    description: "Description 2",
                    author: "Author 2",
                    publishedDate: currentDate,
                    url: URL(string: "https://example.com")!,
                    comments: commentsForResult2
                )
            ]
            addToSearchHistory(searchText)
        } catch {
            self.error = error
        }
        
        isLoading = false
    }
    
    func clearSearch() {
        searchText = ""
        searchResults = []
        error = nil
    }
    
    private func addToSearchHistory(_ query: String) {
        searchHistory.insert(query, at: 0)
        if searchHistory.count > maxHistoryItems {
            searchHistory.removeLast()
        }
        saveSearchHistory()
    }
    
    private func loadSearchHistory() {
        if let history = UserDefaults.standard.stringArray(forKey: "searchHistory") {
            searchHistory = history
        }
    }
    
    private func saveSearchHistory() {
        UserDefaults.standard.set(searchHistory, forKey: "searchHistory")
    }
}

struct SearchResult: Identifiable {
    let id: String
    let source: String
    let title: String
    let description: String
    let author: String
    let publishedDate: Date
    let url: URL
    let comments: [Comment]
    
    init(id: String, source: String, title: String, description: String, author: String, publishedDate: Date, url: URL, comments: [Comment] = []) {
        self.id = id
        self.source = source
        self.title = title
        self.description = description
        self.author = author
        self.publishedDate = publishedDate
        self.url = url
        self.comments = comments
    }
} 