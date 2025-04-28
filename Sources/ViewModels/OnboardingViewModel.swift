import SwiftUI

@MainActor
final class OnboardingViewModel: ObservableObject {
    @Published var currentPage = 0
    @Published var isOnboardingComplete = false
    
    private let pageCount = 3
    
    func nextPage() {
        if currentPage < pageCount - 1 {
            currentPage += 1
        } else {
            completeOnboarding()
        }
    }
    
    func previousPage() {
        if currentPage > 0 {
            currentPage -= 1
        }
    }
    
    func completeOnboarding() {
        UserDefaults.standard.set(true, forKey: "hasSeenOnboarding")
        isOnboardingComplete = true
    }
    
    func shouldShowOnboarding() -> Bool {
        !UserDefaults.standard.bool(forKey: "hasSeenOnboarding")
    }
} 