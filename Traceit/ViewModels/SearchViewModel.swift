import SwiftUI
import PhotosUI

@MainActor
final class SearchViewModel: ObservableObject {
    @Published var searchText = ""
    @Published var searchResults: [SearchResult] = []
    @Published var isLoading = false
    @Published var error: Error?
    @Published var searchHistory: [String] = []
    @Published var hasSearched = false
    @Published var photoSelection: PhotosPickerItem? {
        didSet {
            processPhotoSelection()
        }
    }
    @Published var selectedImage: UIImage?
    
    private let maxHistoryItems = 10
    
    init() {
        loadSearchHistory()
    }
    
    private func processPhotoSelection() {
        Task {
            if let photoSelection = photoSelection,
               let data = try? await photoSelection.loadTransferable(type: Data.self),
               let image = UIImage(data: data) {
                await MainActor.run {
                    self.selectedImage = image
                    print("Photo selected")
                    // Here you would process the image for search
                }
            }
        }
    }
    
    func performSearch() async {
        guard !searchText.isEmpty else { return }
        
        isLoading = true
        error = nil
        
        do {
            // Simulated search delay
            try await Task.sleep(nanoseconds: 1_000_000_000)
            
            // Simulated results
            searchResults = [
                SearchResult(
                    id: "1", 
                    title: "Sample Result 1", 
                    description: "Description 1", 
                    url: URL(string: "https://example.com")!,
                    source: "Source 1",
                    publishDate: Date(),
                    author: "Author 1"
                ),
                SearchResult(
                    id: "2", 
                    title: "Sample Result 2", 
                    description: "Description 2", 
                    url: URL(string: "https://example.com")!,
                    source: "Source 2",
                    publishDate: Date(),
                    author: "Author 2"
                )
            ]
            
            addToSearchHistory(searchText)
            hasSearched = true
        } catch {
            self.error = error
        }
        
        isLoading = false
    }
    
    func clearSearch() {
        searchText = ""
        searchResults = []
        error = nil
        hasSearched = false
    }
    
    func removeSearchHistoryItem(at index: Int) {
        guard index >= 0, index < searchHistory.count else { return }
        searchHistory.remove(at: index)
        saveSearchHistory()
    }
    
    func removeSearchHistory(query: String) {
        searchHistory.removeAll { $0 == query }
        saveSearchHistory()
    }
    
    func clearAllSearchHistory() {
        searchHistory.removeAll()
        saveSearchHistory()
    }
    
    private func addToSearchHistory(_ query: String) {
        // Remove the query if it already exists to avoid duplicates
        searchHistory.removeAll { $0 == query }
        
        // Add the query at the beginning of the array
        searchHistory.insert(query, at: 0)
        
        // Keep only the maximum number of history items
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
    var source: String = ""
    var thumbnailImage: UIImage? = nil
    var publishDate: Date = Date()
    var author: String = ""
    var label: String? = nil
}

struct Comment: Identifiable {
    let id: String
    let author: String
    let text: String
    let timestamp: Date
    let avatarImage: UIImage?
}

@MainActor
class CommentViewModel: ObservableObject {
    @Published var comments: [Comment] = []
    @Published var newCommentText: String = ""
    
    // In a real app, this would be associated with the current search result
    private let resultId: String
    
    init(resultId: String) {
        self.resultId = resultId
        // Load sample comments for demonstration
        loadSampleComments()
    }
    
    private func loadSampleComments() {
        comments = [
            Comment(
                id: UUID().uuidString,
                author: "John Doe",
                text: "This is a very interesting result. I found it really helpful for my research.",
                timestamp: Date().addingTimeInterval(-3600 * 24), // 1 day ago
                avatarImage: nil
            ),
            Comment(
                id: UUID().uuidString,
                author: "Jane Smith",
                text: "Great resource! Thanks for sharing this information.",
                timestamp: Date().addingTimeInterval(-3600 * 12), // 12 hours ago
                avatarImage: nil
            )
        ]
    }
    
    func addComment() {
        guard !newCommentText.isEmpty else { return }
        
        let newComment = Comment(
            id: UUID().uuidString,
            author: "Current User", // In a real app, this would be the current user's name
            text: newCommentText,
            timestamp: Date(),
            avatarImage: nil
        )
        
        comments.append(newComment)
        newCommentText = ""
        
        // In a real app, you would save the comment to a database
    }
} 