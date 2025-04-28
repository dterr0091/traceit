import Foundation

/// Protocol for DI container
protocol DIContainerProtocol {
    func register<Service>(_ serviceType: Service.Type, factory: @escaping () -> Service)
    func resolve<Service>(_ serviceType: Service.Type) -> Service?
}

/// Simple DI container for app-wide dependency management
final class DIContainer: DIContainerProtocol {
    static let shared = DIContainer()
    private var factories: [String: () -> Any] = [:]
    private init() {}

    func register<Service>(_ serviceType: Service.Type, factory: @escaping () -> Service) {
        let key = String(describing: serviceType)
        factories[key] = factory
    }

    func resolve<Service>(_ serviceType: Service.Type) -> Service? {
        let key = String(describing: serviceType)
        return factories[key]?() as? Service
    }
}

// Usage Example:
// DIContainer.shared.register(NetworkServiceProtocol.self) { NetworkService() }
// let service = DIContainer.shared.resolve(NetworkServiceProtocol.self) 