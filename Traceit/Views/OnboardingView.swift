import SwiftUI

struct OnboardingView: View {
    @EnvironmentObject private var appState: AppState
    @State private var currentPage = 0
    
    private let pages = [
        OnboardingPage(
            title: "Welcome to Traceit",
            description: "Your intelligent search companion for connected information",
            imageName: "magnifyingglass.circle.fill"
        ),
        OnboardingPage(
            title: "Smart Search",
            description: "Find related information with semantic search technology",
            imageName: "brain.head.profile"
        ),
        OnboardingPage(
            title: "Community Insights",
            description: "Discover and contribute to shared knowledge",
            imageName: "person.3.fill"
        )
    ]
    
    var body: some View {
        VStack {
            TabView(selection: $currentPage) {
                ForEach(0..<pages.count, id: \.self) { index in
                    OnboardingPageView(page: pages[index])
                        .tag(index)
                }
            }
            .tabViewStyle(.page)
            .indexViewStyle(.page(backgroundDisplayMode: .always))
            
            HStack {
                if currentPage > 0 {
                    Button("Back") {
                        withAnimation {
                            currentPage -= 1
                        }
                    }
                }
                
                Spacer()
                
                if currentPage == pages.count - 1 {
                    Button("Get Started") {
                        appState.shouldShowOnboarding = false
                    }
                    .buttonStyle(.borderedProminent)
                } else {
                    Button("Next") {
                        withAnimation {
                            currentPage += 1
                        }
                    }
                }
            }
            .padding()
        }
    }
}

struct OnboardingPage: Identifiable {
    let id = UUID()
    let title: String
    let description: String
    let imageName: String
}

struct OnboardingPageView: View {
    let page: OnboardingPage
    
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: page.imageName)
                .font(.system(size: 100))
                .foregroundColor(.blue)
                .padding()
            
            Text(page.title)
                .font(.title)
                .fontWeight(.bold)
            
            Text(page.description)
                .font(.body)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
        }
    }
}

#Preview {
    OnboardingView()
        .environmentObject(AppState())
} 