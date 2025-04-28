import SwiftUI

@main
struct TraceitApp: App {
    @StateObject private var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            Group {
                if appState.shouldShowOnboarding {
                    OnboardingView()
                } else {
                    SearchView()
                }
            }
            .environmentObject(appState)
        }
    }
}

class AppState: ObservableObject {
    @Published var shouldShowOnboarding: Bool {
        didSet {
            UserDefaults.standard.set(!shouldShowOnboarding, forKey: "hasSeenOnboarding")
        }
    }
    
    init() {
        self.shouldShowOnboarding = !UserDefaults.standard.bool(forKey: "hasSeenOnboarding")
    }
} 