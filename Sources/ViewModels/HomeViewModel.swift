import Foundation

final class HomeViewModel: ObservableObject {
    @Published var items: [HomeModel] = []
    
    /// Fetches sample data for demonstration
    func fetchItems() {
        // Replace with real network call
        items = [
            HomeModel(id: UUID(), title: "Welcome to Traceit", description: "Your semantic search journey starts here."),
            HomeModel(id: UUID(), title: "Community Insights", description: "See what others are discovering.")
        ]
    }
} 