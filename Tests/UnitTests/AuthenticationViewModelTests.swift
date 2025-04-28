import XCTest
@testable import Traceit

final class MockAuthService: AuthenticationServiceProtocol {
    var currentUser: User? = nil
    var shouldSucceed = true

    func signInWithApple(completion: @escaping (Result<User, Error>) -> Void) {
        if shouldSucceed {
            let user = User(id: "123", email: "test@example.com", fullName: "Test User")
            currentUser = user
            completion(.success(user))
        } else {
            completion(.failure(NSError(domain: "Test", code: 1)))
        }
    }

    func signOut() {
        currentUser = nil
    }
}

final class AuthenticationViewModelTests: XCTestCase {
    func testSignInSuccess() {
        let mockService = MockAuthService()
        let viewModel = AuthenticationViewModel(authService: mockService)

        let expectation = self.expectation(description: "Sign in completes")
        viewModel.signIn()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            XCTAssertTrue(viewModel.isAuthenticated)
            XCTAssertNotNil(viewModel.user)
            expectation.fulfill()
        }
        waitForExpectations(timeout: 1)
    }

    func testSignInFailure() {
        let mockService = MockAuthService()
        mockService.shouldSucceed = false
        let viewModel = AuthenticationViewModel(authService: mockService)

        let expectation = self.expectation(description: "Sign in fails")
        viewModel.signIn()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            XCTAssertFalse(viewModel.isAuthenticated)
            XCTAssertNotNil(viewModel.error)
            expectation.fulfill()
        }
        waitForExpectations(timeout: 1)
    }
} 