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
            searchResults = [
                SearchResult(id: "1", title: "Sample Result 1", description: "Description 1", url: URL(string: "https://example.com")!),
                SearchResult(id: "2", title: "Sample Result 2", description: "Description 2", url: URL(string: "https://example.com")!)
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
    let title: String
    let description: String
    let url: URL
} 