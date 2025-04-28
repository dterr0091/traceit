import SwiftUI

struct ResultDetailView: View {
    let result: SearchResult
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(result.title)
                    .font(.title)
                    .fontWeight(.bold)
                
                Text(result.description)
                    .font(.body)
                    .foregroundColor(.secondary)
                
                Link(destination: result.url) {
                    HStack {
                        Image(systemName: "link")
                        Text("Visit Website")
                    }
                    .foregroundColor(.blue)
                }
            }
            .padding()
        }
        .navigationTitle("Details")
        .navigationBarTitleDisplayMode(.inline)
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
    }
} 