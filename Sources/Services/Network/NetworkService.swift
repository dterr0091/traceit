import Foundation
import Alamofire

/// Protocol for network service (for DI and testing)
protocol NetworkServiceProtocol {
    func request<T: Decodable>(endpoint: String, method: HTTPMethod, parameters: Parameters?, completion: @escaping (Result<T, Error>) -> Void)
}

/// Base network service using Alamofire
final class NetworkService: NetworkServiceProtocol {
    private let baseURL: String
    private let session: Session

    init(baseURL: String = Environment.shared.value(for: "APIBaseURL") ?? "", session: Session = .default) {
        self.baseURL = baseURL
        self.session = session
    }

    func request<T: Decodable>(endpoint: String, method: HTTPMethod = .get, parameters: Parameters? = nil, completion: @escaping (Result<T, Error>) -> Void) {
        let url = baseURL + endpoint
        session.request(url, method: method, parameters: parameters)
            .validate()
            .responseDecodable(of: T.self) { response in
                switch response.result {
                case .success(let value):
                    completion(.success(value))
                case .failure(let error):
                    completion(.failure(error))
                }
            }
    }
}

// Usage Example:
// let networkService = NetworkService()
// networkService.request(endpoint: "/users", method: .get, parameters: nil) { (result: Result<User, Error>) in ... } 