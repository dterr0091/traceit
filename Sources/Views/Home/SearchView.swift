import SwiftUI
import MapKit

struct SearchView: View {
    @StateObject private var viewModel = SearchViewModel()
    @FocusState private var isSearchFieldFocused: Bool
    @EnvironmentObject private var appState: AppState
    @State private var searchText = ""
    
    // Drawer states
    @State private var drawerHeight: CGFloat = 100
    @State private var drawerOffset: CGFloat = 0
    @State private var lastDragValue: CGFloat = 0
    @State private var hasResults = false
    
    // Map region
    @State private var region = MKCoordinateRegion(
        center: CLLocationCoordinate2D(latitude: 37.7749, longitude: -122.4194),
        span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
    )
    
    // Screen metrics
    private let minDrawerHeight: CGFloat = 100
    private let maxDrawerHeight: CGFloat = UIScreen.main.bounds.height * 0.9
    private let screenHeight = UIScreen.main.bounds.height
    
    var body: some View {
        ZStack(alignment: .top) {
            // Map View as the background
            Map(coordinateRegion: $region)
                .edgesIgnoringSafeArea(.all)
            
            // Search bar at the top
            VStack {
                HStack {
                    HStack {
                        Image(systemName: "magnifyingglass")
                            .foregroundColor(.gray)
                        TextField("Try \"Ranch style houses in Phoenix\"", text: $searchText)
                            .onSubmitLabel(.search)
                            .onSubmit {
                                performSearch()
                            }
                    }
                    .padding(8)
                    .background(Color.white)
                    .cornerRadius(10)
                    .shadow(radius: 2)
                    
                    Button(action: {
                        // Filters action
                    }) {
                        Image(systemName: "line.horizontal.3.decrease.circle")
                            .font(.title2)
                            .foregroundColor(.blue)
                    }
                }
                .padding()
                
                Spacer()
            }
            
            // Action buttons
            VStack {
                Spacer()
                
                HStack(spacing: 16) {
                    Button(action: {}) {
                        Image(systemName: "square.stack.3d.up")
                            .font(.title2)
                            .padding(12)
                            .background(Color.white)
                            .cornerRadius(30)
                            .shadow(radius: 2)
                    }
                    
                    Button(action: {}) {
                        Image(systemName: "timer")
                            .font(.title2)
                            .padding(12)
                            .background(Color.white)
                            .cornerRadius(30)
                            .shadow(radius: 2)
                    }
                    
                    Button(action: {}) {
                        Image(systemName: "location")
                            .font(.title2)
                            .padding(12)
                            .background(Color.white)
                            .cornerRadius(30)
                            .shadow(radius: 2)
                    }
                    
                    Spacer()
                    
                    Button(action: {
                        performSearch()
                    }) {
                        HStack {
                            Image(systemName: "magnifyingglass")
                            Text("Save Search")
                                .fontWeight(.medium)
                        }
                        .padding(.vertical, 12)
                        .padding(.horizontal, 16)
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(30)
                        .shadow(radius: 2)
                    }
                }
                .padding()
                .padding(.bottom, drawerHeight > minDrawerHeight + 100 ? drawerHeight - minDrawerHeight : 0)
            }
            
            // Results drawer
            VStack(spacing: 0) {
                Spacer()
                
                ZStack(alignment: .top) {
                    // Drawer background with rounded corners
                    RoundedCorner(radius: 16, corners: [.topLeft, .topRight])
                        .fill(Color.white)
                        .shadow(radius: 5)
                    
                    VStack(spacing: 0) {
                        // Drawer handle
                        Rectangle()
                            .fill(Color.gray.opacity(0.3))
                            .frame(width: 40, height: 5)
                            .cornerRadius(2.5)
                            .padding(.top, 8)
                        
                        // Results count
                        if hasResults {
                            HStack {
                                if let sortOption = viewModel.currentSortOption {
                                    Text("Sort: \(sortOption)")
                                        .font(.subheadline)
                                } else {
                                    Text("\(viewModel.searchResults.count) results")
                                        .font(.headline)
                                        .padding(.vertical, 8)
                                }
                                
                                Spacer()
                                
                                Button(action: {
                                    // Save search action
                                }) {
                                    HStack {
                                        Image(systemName: "magnifyingglass")
                                        Text("Save Search")
                                    }
                                    .foregroundColor(.blue)
                                }
                            }
                            .padding(.horizontal)
                            .padding(.bottom, 8)
                        }
                        
                        // Results list
                        ScrollView {
                            LazyVStack(spacing: 16) {
                                ForEach(viewModel.searchResults) { result in
                                    ResultCard(result: result)
                                }
                                
                                // Add extra padding at the bottom
                                Color.clear.frame(height: 50)
                            }
                            .padding(.horizontal)
                        }
                        .gesture(
                            DragGesture()
                                .onChanged { value in
                                    // Detect drag direction for better UX
                                    let translation = value.translation.height
                                    let dragDown = translation > 0
                                    
                                    // Calculate new height based on drag
                                    let newHeight = drawerHeight - translation + lastDragValue
                                    
                                    // Apply constraints to the drawer height
                                    if newHeight >= minDrawerHeight && newHeight <= maxDrawerHeight {
                                        drawerHeight = newHeight
                                    }
                                    
                                    // If user is at the top of the list and drags down, start collapsing
                                    if dragDown && drawerOffset == 0 {
                                        drawerOffset = translation
                                    }
                                }
                                .onEnded { value in
                                    lastDragValue = 0
                                    drawerOffset = 0
                                    
                                    // Snap to predefined positions
                                    let midPoint = (maxDrawerHeight + minDrawerHeight) / 2
                                    
                                    if drawerHeight < midPoint {
                                        // Snap to minimized
                                        withAnimation(.spring()) {
                                            drawerHeight = minDrawerHeight
                                        }
                                    } else {
                                        // Snap to expanded
                                        withAnimation(.spring()) {
                                            drawerHeight = maxDrawerHeight
                                        }
                                    }
                                }
                        )
                    }
                }
                .frame(height: drawerHeight)
                .offset(y: drawerOffset)
            }
            .ignoresSafeArea(edges: .bottom)
        }
        .navigationBarHidden(true)
        .onChange(of: viewModel.searchResults) { newResults in
            withAnimation {
                hasResults = !newResults.isEmpty
                if hasResults && drawerHeight == minDrawerHeight {
                    drawerHeight = screenHeight * 0.4 // Show partial results initially
                }
            }
        }
    }
    
    private func performSearch() {
        guard !searchText.isEmpty else { return }
        
        Task {
            await viewModel.performSearch(query: searchText)
        }
    }
}

// MARK: - Helper Views

struct ResultCard: View {
    let result: SearchResult
    @State private var isFavorite = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Image with days on market label
            ZStack(alignment: .topLeading) {
                // Property image
                ZStack(alignment: .bottomTrailing) {
                    Rectangle() // Placeholder for the property image
                        .fill(Color.gray.opacity(0.3))
                        .aspectRatio(1.6, contentMode: .fit)
                        .cornerRadius(8)
                    
                    // Image pagination dots
                    HStack(spacing: 4) {
                        ForEach(0..<5) { i in
                            Circle()
                                .fill(i == 0 ? Color.white : Color.white.opacity(0.5))
                                .frame(width: 6, height: 6)
                        }
                    }
                    .padding(8)
                }
                
                // Days on market badge
                Text("1 day on Zillow")
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.white)
                    .cornerRadius(4)
                    .padding(8)
                
                // Favorite button
                VStack {
                    HStack {
                        Spacer()
                        
                        Button(action: {
                            isFavorite.toggle()
                        }) {
                            Image(systemName: isFavorite ? "heart.fill" : "heart")
                                .foregroundColor(isFavorite ? .red : .white)
                                .padding(8)
                                .background(Color.white.opacity(0.6))
                                .clipShape(Circle())
                        }
                    }
                    .padding(8)
                    
                    Spacer()
                }
            }
            
            // Property details
            VStack(alignment: .leading, spacing: 4) {
                // Price
                Text("$\(Int(result.price).formattedWithSeparator)")
                    .font(.title2)
                    .fontWeight(.bold)
                
                // Property specs
                HStack {
                    Text("\(result.bedrooms) bds")
                    Text("•")
                    Text("\(result.bathrooms) ba")
                    Text("•")
                    Text("\(Int(result.squareFeet).formattedWithSeparator) sqft")
                    
                    if !result.propertyType.isEmpty {
                        Text("•")
                        Text(result.propertyType)
                    }
                }
                .font(.subheadline)
                .foregroundColor(.secondary)
                
                // Address
                Text(result.address)
                    .font(.subheadline)
                
                // Real estate agency
                Text(result.agency.uppercased())
                    .font(.caption)
                    .foregroundColor(.gray)
                    .padding(.top, 2)
            }
            .padding(.vertical, 8)
            
            // More options button
            HStack {
                Spacer()
                
                Button(action: {}) {
                    Image(systemName: "ellipsis")
                        .foregroundColor(.blue)
                }
            }
        }
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 3)
    }
}

struct RoundedCorner: Shape {
    var radius: CGFloat = .infinity
    var corners: UIRectCorner = .allCorners
    
    func path(in rect: CGRect) -> Path {
        let path = UIBezierPath(
            roundedRect: rect,
            byRoundingCorners: corners,
            cornerRadii: CGSize(width: radius, height: radius)
        )
        return Path(path.cgPath)
    }
}

// MARK: - Extensions

extension Int {
    var formattedWithSeparator: String {
        return Formatter.withSeparator.string(for: self) ?? ""
    }
}

extension Formatter {
    static let withSeparator: NumberFormatter = {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.groupingSeparator = ","
        return formatter
    }()
}

#Preview {
    SearchView()
} 