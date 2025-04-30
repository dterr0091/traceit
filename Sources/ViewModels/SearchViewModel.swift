import SwiftUI
import MapKit

@MainActor
final class SearchViewModel: ObservableObject {
    @Published var searchText = ""
    @Published var searchResults: [SearchResult] = []
    @Published var isLoading = false
    @Published var error: Error?
    @Published var searchHistory: [String] = []
    @Published var currentSortOption: String? = nil
    
    private let maxHistoryItems = 10
    private let networkService: NetworkServiceProtocol
    
    init(networkService: NetworkServiceProtocol = NetworkService()) {
        self.networkService = networkService
        loadSearchHistory()
    }
    
    func performSearch(query: String) async {
        guard !query.isEmpty else { return }
        
        isLoading = true
        error = nil
        searchText = query
        
        do {
            // TODO: Replace with actual API call
            try await Task.sleep(nanoseconds: 1_000_000_000) // Simulated delay
            
            searchResults = [
                SearchResult(
                    id: "1",
                    price: 159900,
                    address: "381 S McMullen Booth Rd APT 72, Clearwater, FL",
                    bedrooms: 2,
                    bathrooms: 1,
                    squareFeet: 968,
                    propertyType: "Condo for sale",
                    agency: "Park Property Group",
                    daysOnMarket: 1,
                    images: [],
                    features: [],
                    location: CLLocationCoordinate2D(latitude: 27.9659, longitude: -82.7121)
                ),
                SearchResult(
                    id: "2",
                    price: 660000,
                    address: "3125 Downing St, Clearwater, FL",
                    bedrooms: 4,
                    bathrooms: 3,
                    squareFeet: 2197,
                    propertyType: "New construction",
                    agency: "LPT Realty LLC",
                    daysOnMarket: 15,
                    images: [],
                    features: ["Boat or rv parking"],
                    location: CLLocationCoordinate2D(latitude: 27.9690, longitude: -82.7251)
                ),
                SearchResult(
                    id: "3",
                    price: 450000,
                    address: "1234 Main St, Clearwater, FL",
                    bedrooms: 3,
                    bathrooms: 2,
                    squareFeet: 1850,
                    propertyType: "House for sale",
                    agency: "Coastal Realty",
                    daysOnMarket: 7,
                    images: [],
                    features: ["Kidney-shaped pool"],
                    location: CLLocationCoordinate2D(latitude: 27.9671, longitude: -82.7320)
                )
            ]
            
            addToSearchHistory(query)
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
    
    func setSortOption(_ option: String) {
        currentSortOption = option
        
        // Implement actual sorting logic here
        switch option {
        case "Price: Low to High":
            searchResults.sort { $0.price < $1.price }
        case "Price: High to Low":
            searchResults.sort { $0.price > $1.price }
        case "Newest":
            searchResults.sort { $0.daysOnMarket < $1.daysOnMarket }
        case "Bedrooms":
            searchResults.sort { $0.bedrooms > $1.bedrooms }
        case "Bathrooms":
            searchResults.sort { $0.bathrooms > $1.bathrooms }
        case "Square Feet":
            searchResults.sort { $0.squareFeet > $1.squareFeet }
        default:
            break
        }
    }
    
    private func addToSearchHistory(_ query: String) {
        // Remove if already exists to avoid duplicates
        searchHistory.removeAll { $0 == query }
        
        // Add to the beginning
        searchHistory.insert(query, at: 0)
        
        // Keep only the most recent searches
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
    let price: Double
    let address: String
    let bedrooms: Int
    let bathrooms: Int
    let squareFeet: Double
    let propertyType: String
    let agency: String
    let daysOnMarket: Int
    let images: [String] // URLs to images
    let features: [String] // Special features like "pool", "waterfront", etc.
    let location: CLLocationCoordinate2D
} 