import SwiftUI

struct ResultDetailView: View {
    let result: SearchResult
    
    var body: some View {
        VStack(spacing: 0) {
            // Custom header
            HStack {
                Text("Details")
                    .font(.title)
                    .fontWeight(.bold)
                Spacer()
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(Color.white)
            
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
        }
        .background(Color(UIColor.systemGroupedBackground))
    }
}

#Preview {
    ResultDetailView(result: SearchResult(
        id: "1",
        title: "Sample Result",
        description: "This is a sample search result description that provides more details about the content.",
        url: URL(string: "https://example.com")!
    ))
} 