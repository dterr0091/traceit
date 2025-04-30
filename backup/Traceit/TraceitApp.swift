//
//  TraceitApp.swift
//  Traceit
//
//  Created by Dominick Terry on 4/28/25.
//

import SwiftUI

@main
struct TraceitApp: App {
    @StateObject private var appState = AppState()
    
    init() {
        // Set global appearance
        let coloredAppearance = UINavigationBarAppearance()
        coloredAppearance.configureWithOpaqueBackground()
        coloredAppearance.backgroundColor = UIColor(Color.appMintCream)
        coloredAppearance.titleTextAttributes = [.foregroundColor: UIColor(Color.appSmokyBlack)]
        coloredAppearance.largeTitleTextAttributes = [.foregroundColor: UIColor(Color.appSmokyBlack)]
        
        UINavigationBar.appearance().standardAppearance = coloredAppearance
        UINavigationBar.appearance().compactAppearance = coloredAppearance
        UINavigationBar.appearance().scrollEdgeAppearance = coloredAppearance
        
        // Set list appearance
        UITableView.appearance().backgroundColor = UIColor(Color.appMintCream)
    }
    
    var body: some Scene {
        WindowGroup {
            NavigationView {
                Group {
                    if appState.shouldShowOnboarding {
                        OnboardingView()
                    } else {
                        SearchView()
                    }
                }
            }
            .navigationViewStyle(StackNavigationViewStyle())
            .environmentObject(appState)
            .preferredColorScheme(.light)
            .background(Color.appMintCream)
        }
    }
}

class AppState: ObservableObject {
    @Published var shouldShowOnboarding: Bool {
        didSet {
            UserDefaults.standard.set(!shouldShowOnboarding, forKey: "hasSeenOnboarding")
        }
    }
    
    init() {
        self.shouldShowOnboarding = !UserDefaults.standard.bool(forKey: "hasSeenOnboarding")
    }
}
