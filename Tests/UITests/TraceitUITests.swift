import XCTest

final class TraceitUITests: XCTestCase {
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = ["UITesting"]
        app.launch()
    }
    
    func testSignInFlow() throws {
        // Given
        let signInButton = app.buttons["Sign in with Apple"]
        
        // When
        signInButton.tap()
        
        // Then
        let homeView = app.navigationBars["Home"]
        XCTAssertTrue(homeView.waitForExistence(timeout: TestConstants.testTimeout))
    }
    
    func testSearchFlow() throws {
        // Given
        let searchField = app.searchFields["Search"]
        
        // When
        searchField.tap()
        searchField.typeText("test query")
        
        // Then
        let resultsList = app.tables["Search Results"]
        XCTAssertTrue(resultsList.waitForExistence(timeout: TestConstants.testTimeout))
    }
} 