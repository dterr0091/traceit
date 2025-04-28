import Foundation
import AuthenticationServices

/// Protocol for authentication service (for DI and testing)
protocol AuthenticationServiceProtocol {
    func signInWithApple(completion: @escaping (Result<User, Error>) -> Void)
    func signOut()
    var currentUser: User? { get }
}

/// Sign in with Apple implementation
final class SignInWithAppleService: NSObject, AuthenticationServiceProtocol {
    private(set) var currentUser: User?
    private var completion: ((Result<User, Error>) -> Void)?

    func signInWithApple(completion: @escaping (Result<User, Error>) -> Void) {
        self.completion = completion
        let request = ASAuthorizationAppleIDProvider().createRequest()
        request.requestedScopes = [.fullName, .email]
        let controller = ASAuthorizationController(authorizationRequests: [request])
        controller.delegate = self
        controller.presentationContextProvider = self
        controller.performRequests()
    }

    func signOut() {
        currentUser = nil
        // Remove tokens from Keychain if needed
    }
}

extension SignInWithAppleService: ASAuthorizationControllerDelegate, ASAuthorizationControllerPresentationContextProviding {
    func authorizationController(controller: ASAuthorizationController, didCompleteWithAuthorization authorization: ASAuthorization) {
        if let appleIDCredential = authorization.credential as? ASAuthorizationAppleIDCredential {
            let user = User(
                id: appleIDCredential.user,
                email: appleIDCredential.email,
                fullName: [appleIDCredential.fullName?.givenName, appleIDCredential.fullName?.familyName].compactMap { $0 }.joined(separator: " ")
            )
            self.currentUser = user
            completion?(.success(user))
        }
    }

    func authorizationController(controller: ASAuthorizationController, didCompleteWithError error: Error) {
        completion?(.failure(error))
    }

    func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor {
        // Provide the main window for presentation
        UIApplication.shared.windows.first { $0.isKeyWindow } ?? ASPresentationAnchor()
    }
} 