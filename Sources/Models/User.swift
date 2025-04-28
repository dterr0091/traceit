import Foundation

struct User: Identifiable, Codable {
    let id: String
    let email: String?
    let fullName: String?
} 