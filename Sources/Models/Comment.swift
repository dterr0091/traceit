import Foundation

struct Comment: Identifiable, Codable {
    let id: String
    let resultId: String
    let title: String
    let comment: String
    let isHelpful: Bool
    let timestamp: Date = Date()
} 