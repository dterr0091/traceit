import Foundation
import Combine

final class AuthenticationViewModel: ObservableObject {
    @Published var user: User?
    @Published var isAuthenticated: Bool = false
    @Published var error: Error?

    private let authService: AuthenticationServiceProtocol
    private var cancellables = Set<AnyCancellable>()

    init(authService: AuthenticationServiceProtocol = SignInWithAppleService()) {
        self.authService = authService
        self.user = authService.currentUser
        self.isAuthenticated = user != nil
    }

    func signIn() {
        authService.signInWithApple { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let user):
                    self?.user = user
                    self?.isAuthenticated = true
                case .failure(let error):
                    self?.error = error
                    self?.isAuthenticated = false
                }
            }
        }
    }

    func signOut() {
        authService.signOut()
        user = nil
        isAuthenticated = false
    }
} 