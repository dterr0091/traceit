// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "traceit",
    platforms: [
        .iOS(.v16)
    ],
    products: [
        .executable(
            name: "Traceit",
            targets: ["Traceit"])
    ],
    dependencies: [
        .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.8.0"),
        .package(url: "https://github.com/onevcat/Kingfisher.git", from: "7.0.0"),
        .package(url: "https://github.com/firebase/firebase-ios-sdk.git", from: "10.0.0"),
        .package(url: "https://github.com/siteline/swiftui-introspect.git", from: "1.0.0")
    ],
    targets: [
        .executableTarget(
            name: "Traceit",
            dependencies: [
                "Alamofire",
                "Kingfisher",
                .product(name: "FirebaseAnalytics", package: "firebase-ios-sdk"),
                .product(name: "FirebaseAuth", package: "firebase-ios-sdk"),
                .product(name: "FirebaseDatabase", package: "firebase-ios-sdk"),
                .product(name: "SwiftUIIntrospect", package: "swiftui-introspect")
            ],
            path: "Sources",
            resources: [
                .process("../Resources")
            ]
        ),
        .testTarget(
            name: "traceitTests",
            dependencies: ["Traceit"]
        ),
    ]
)
