import Foundation

/// Enum representing the app environment
public enum AppEnvironment: String {
    case development = "Development"
    case staging = "Staging"
    case production = "Production"
}

/// Singleton for managing environment configuration
public final class Environment {
    public static let shared = Environment()
    public let environment: AppEnvironment
    private var config: [String: Any] = [:]

    private init() {
        #if DEVELOPMENT
        environment = .development
        #elseif STAGING
        environment = .staging
        #else
        environment = .production
        #endif
        loadConfig()
    }

    private func loadConfig() {
        let name = environment.rawValue
        if let url = Bundle.main.url(forResource: name, withExtension: "plist"),
           let data = try? Data(contentsOf: url),
           let dict = try? PropertyListSerialization.propertyList(from: data, options: [], format: nil) as? [String: Any] {
            config = dict
        }
    }

    public func value<T>(for key: String) -> T? {
        return config[key] as? T
    }
} 