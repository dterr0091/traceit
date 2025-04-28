import SwiftUI
import AuthenticationServices

struct SignInWithAppleButtonView: View {
    @ObservedObject var viewModel: AuthenticationViewModel

    var body: some View {
        SignInWithAppleButton(
            .signIn,
            onRequest: { request in
                request.requestedScopes = [.fullName, .email]
            },
            onCompletion: { _ in
                viewModel.signIn()
            }
        )
        .signInWithAppleButtonStyle(.black)
        .frame(height: 45)
        .accessibilityLabel("Sign in with Apple")
    }
}

#Preview {
    SignInWithAppleButtonView(viewModel: AuthenticationViewModel())
} 