import XCTest
@testable import Traceit

final class AuthenticationViewModelTests: XCTestCase {
    var sut: AuthenticationViewModel!
    var mockAuthService: MockAuthenticationService!
    
    override func setUp() {
        super.setUp()
        mockAuthService = MockAuthenticationService()
        sut = AuthenticationViewModel(authenticationService: mockAuthService)
    }
    
    override func tearDown() {
        sut = nil
        mockAuthService = nil
        super.tearDown()
    }
    
    func testSignInWithApple_Success() async throws {
        // Given
        mockAuthService.signInResult = .success(User(id: "123", email: "test@example.com"))
        
        // When
        let result = try await sut.signInWithApple()
        
        // Then
        XCTAssertTrue(result)
        XCTAssertTrue(sut.isAuthenticated)
    }
    
    func testSignInWithApple_Failure() async throws {
        // Given
        mockAuthService.signInResult = .failure(AuthenticationError.invalidCredentials)
        
        // When
        let result = try await sut.signInWithApple()
        
        // Then
        XCTAssertFalse(result)
        XCTAssertFalse(sut.isAuthenticated)
    }
}

// MARK: - Mock Authentication Service
class MockAuthenticationService: AuthenticationServiceProtocol {
    var signInResult: Result<User, Error> = .failure(AuthenticationError.unknown)
    
    func signInWithApple() async throws -> User {
        switch signInResult {
        case .success(let user):
            return user
        case .failure(let error):
            throw error
        }
    }
}

// MARK: - Authentication Errors
enum AuthenticationError: Error {
    case invalidCredentials
    case networkError
    case unknown
} 