import SwiftUI

struct ResultDetailView: View {
    let result: SearchResult
    @State private var searchText = ""
    @FocusState private var isSearchFieldFocused: Bool
    @EnvironmentObject private var appState: AppState
    
    var body: some View {
        ZStack(alignment: .bottom) {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Text(result.title)
                        .font(.interBold(size: 24))
                        .foregroundColor(Color.appSmokyBlack)
                    
                    Text(result.description)
                        .font(.interRegular(size: 17))
                        .foregroundColor(Color.appSmokyBlack.opacity(0.7))
                    
                    Link(destination: result.url) {
                        HStack {
                            Image(systemName: "link")
                            Text("Visit Website")
                                .font(.interMedium(size: 16))
                        }
                        .foregroundColor(Color.appSandyBrown)
                    }
                }
                .padding()
                .background(Color.white)
                .cornerRadius(12)
                .shadow(color: Color.appSmokyBlack.opacity(0.05), radius: 5, x: 0, y: 2)
                .padding()
            }
            .background(Color.appMintCream)
            .padding(.bottom, 70) // Make room for search bar
            
            // Bottom Search Bar
            VStack(spacing: 0) {
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(Color.appSmokyBlack.opacity(0.6))
                    
                    TextField("Search...", text: $searchText)
                        .textFieldStyle(.plain)
                        .font(.interRegular(size: 16))
                        .focused($isSearchFieldFocused)
                        .foregroundColor(Color.appSmokyBlack)
                    
                    if !searchText.isEmpty {
                        Button(action: {
                            searchText = ""
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
                .background(Color.white)
            }
        }
        .navigationTitle("Details")
        .navigationBarTitleDisplayMode(.inline)
        .background(Color.appMintCream)
    }
}

#Preview {
    NavigationView {
        ResultDetailView(result: SearchResult(
            id: "1",
            title: "Sample Result",
            description: "This is a sample search result description that provides more details about the content.",
            url: URL(string: "https://example.com")!
        ))
        .environmentObject(AppState())
    }
} 