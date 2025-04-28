import SwiftUI
import PhotosUI
import UIKit

struct SearchView: View {
    @StateObject private var viewModel = SearchViewModel()
    @FocusState private var isSearchFieldFocused: Bool
    @EnvironmentObject private var appState: AppState
    @State private var showUploadOptions = false
    @State private var showImagePicker = false
    @State private var showDocumentPicker = false
    @State private var showCamera = false
    @State private var selectedImage: UIImage?
    @State private var selectedFileURL: URL?
    
    var body: some View {
        NavigationView {
            ZStack(alignment: .bottom) {
                VStack(spacing: 0) {
                    if viewModel.isLoading {
                        loadingView
                    } else if viewModel.hasSearched && viewModel.searchResults.isEmpty && !viewModel.searchText.isEmpty {
                        emptyResultsView
                    } else if !viewModel.searchResults.isEmpty {
                        resultsList
                    } else {
                        searchHistoryView
                    }
                }
                .background(Color.appMintCream)
                .padding(.bottom, 120) // Make room for search bar and upload button
                
                // Bottom Search Bar and Upload Button
                VStack(spacing: 0) {
                    searchBar
                    
                    HStack {
                        Spacer()
                        
                        Button(action: {
                            showUploadOptions.toggle()
                        }) {
                            HStack(spacing: 8) {
                                Image(systemName: "arrow.up.doc.fill")
                                Text("Upload")
                                    .font(.interMedium(size: 14))
                            }
                            .foregroundColor(Color.appSmokyBlack)
                            .padding(.vertical, 8)
                            .padding(.horizontal, 16)
                            .overlay(
                                RoundedRectangle(cornerRadius: 20)
                                    .stroke(Color.appSmokyBlack, lineWidth: 1)
                            )
                        }
                        .padding(.top, 8)
                        .padding(.horizontal, 16)
                        .confirmationDialog("Choose upload option", isPresented: $showUploadOptions, titleVisibility: .visible) {
                            Button("Take Photo") {
                                showCamera = true
                            }
                            
                            Button("Choose from Photos") {
                                showImagePicker = true
                            }
                            
                            Button("Browse Files") {
                                showDocumentPicker = true
                            }
                            
                            Button("Cancel", role: .cancel) {}
                        }
                    }
                    .padding(.bottom, 8)
                }
                .background(Color.white)
            }
            .navigationTitle("Search")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        appState.shouldShowOnboarding = true
                    }) {
                        Image(systemName: "questionmark.circle")
                            .foregroundColor(Color.appSmokyBlack)
                    }
                }
            }
            .sheet(isPresented: $showImagePicker) {
                PhotosPicker(selection: $viewModel.photoSelection, matching: .images) {
                    Text("Select Photo")
                }
            }
            .sheet(isPresented: $showDocumentPicker) {
                DocumentPicker { url in
                    selectedFileURL = url
                    // Handle the selected file
                    print("Selected file: \(url.lastPathComponent)")
                }
            }
            .sheet(isPresented: $showCamera) {
                CameraView { image in
                    if let image = image {
                        selectedImage = image
                        // Handle the captured image
                        print("Captured image")
                    }
                }
            }
        }
        .background(Color.appMintCream)
    }
    
    private var searchBar: some View {
        HStack {
            TextField("Search...", text: $viewModel.searchText)
                .textFieldStyle(.plain)
                .font(.interRegular(size: 16))
                .focused($isSearchFieldFocused)
                .foregroundColor(Color.appSmokyBlack)
                .onSubmit {
                    Task {
                        await viewModel.performSearch()
                    }
                }
            
            if !viewModel.searchText.isEmpty {
                Button(action: {
                    viewModel.clearSearch()
                    isSearchFieldFocused = false
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(Color.appSmokyBlack.opacity(0.6))
                }
            }
        }
        .padding(12)
        .background(Color.white)
        .cornerRadius(10)
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
    }
    
    private var loadingView: some View {
        VStack {
            ProgressView()
                .scaleEffect(1.5)
                .tint(Color.appSandyBrown)
            Text("Searching...")
                .font(.interRegular(size: 16))
                .foregroundColor(Color.appSmokyBlack.opacity(0.7))
                .padding(.top)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.appMintCream)
    }
    
    private var emptyResultsView: some View {
        VStack(spacing: 16) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 50))
                .foregroundColor(Color.appSandyBrown)
            Text("No results found")
                .font(.interBold(size: 18))
                .foregroundColor(Color.appSmokyBlack)
            Text("Try different keywords")
                .font(.interRegular(size: 16))
                .foregroundColor(Color.appSmokyBlack.opacity(0.7))
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.appMintCream)
    }
    
    private var searchHistoryView: some View {
        VStack {
            if !viewModel.searchHistory.isEmpty {
                List {
                    Section("Recent Searches") {
                        ForEach(viewModel.searchHistory, id: \.self) { query in
                            Button(action: {
                                viewModel.searchText = query
                                isSearchFieldFocused = true
                            }) {
                                HStack {
                                    Image(systemName: "clock")
                                        .foregroundColor(Color.appSandyBrown)
                                    Text(query)
                                        .font(.interRegular(size: 16))
                                        .foregroundColor(Color.appSmokyBlack)
                                    Spacer()
                                }
                            }
                            .swipeActions(edge: .trailing) {
                                Button(role: .destructive) {
                                    viewModel.removeSearchHistory(query: query)
                                } label: {
                                    Label("Delete", systemImage: "trash")
                                }
                            }
                        }
                    }
                    .listRowBackground(Color.white)
                }
                .listStyle(.plain)
                .environment(\.defaultMinListRowHeight, 0)
                
                Button(action: {
                    viewModel.clearAllSearchHistory()
                }) {
                    Text("Clear All Searches")
                        .font(.interMedium(size: 16))
                        .foregroundColor(Color.red)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.white)
                        .cornerRadius(10)
                        .padding(.horizontal)
                        .padding(.bottom)
                }
            } else {
                VStack(spacing: 20) {
                    Image(systemName: "magnifyingglass")
                        .font(.system(size: 50))
                        .foregroundColor(Color.appSmokyBlack.opacity(0.3))
                    Text("No Search History")
                        .font(.interBold(size: 18))
                        .foregroundColor(Color.appSmokyBlack)
                    Text("Your recent searches will appear here")
                        .font(.interRegular(size: 16))
                        .foregroundColor(Color.appSmokyBlack.opacity(0.7))
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
        .background(Color.appMintCream)
    }
    
    private var resultsList: some View {
        List(viewModel.searchResults) { result in
            NavigationLink(destination: ResultDetailView(result: result)) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(result.title)
                        .font(.interBold(size: 17))
                        .foregroundColor(Color.appSmokyBlack)
                    Text(result.description)
                        .font(.interRegular(size: 15))
                        .foregroundColor(Color.appSmokyBlack.opacity(0.7))
                        .lineLimit(2)
                }
                .padding(.vertical, 4)
            }
            .listRowBackground(Color.white)
        }
        .listStyle(.plain)
        .background(Color.appMintCream)
    }
}

#Preview {
    SearchView()
        .environmentObject(AppState())
} 