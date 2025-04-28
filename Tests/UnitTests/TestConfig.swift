import Foundation
import XCTest

// MARK: - Test Helpers
extension XCTestCase {
    func waitForAsyncOperation(timeout: TimeInterval = 1.0) async {
        try? await Task.sleep(nanoseconds: UInt64(timeout * 1_000_000_000))
    }
    
    func verifyOnMainThread() {
        XCTAssertTrue(Thread.isMainThread, "This test must be run on the main thread")
    }
}

// MARK: - Test Constants
enum TestConstants {
    static let testTimeout: TimeInterval = 5.0
    static let mockUserId = "test_user_123"
    static let mockUserEmail = "test@example.com"
}

// MARK: - Test Environment
enum TestEnvironment {
    static var isSimulator: Bool {
        #if targetEnvironment(simulator)
        return true
        #else
        return false
        #endif
    }
} 