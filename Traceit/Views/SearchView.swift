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
    @State private var selectedResult: SearchResult?
    @State private var showDetailView = false
    
    var body: some View {
        ZStack(alignment: .bottom) {
            VStack(spacing: 0) {
                // Custom header instead of navigation title
                HStack {
                    Text("Search")
                        .font(.interBold(size: 18))
                        .foregroundColor(Color.appSmokyBlack)
                    Spacer()
                    Button(action: {
                        appState.shouldShowOnboarding = true
                    }) {
                        Image(systemName: "questionmark.circle")
                            .foregroundColor(Color.appSmokyBlack)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .background(Color.white)
                
                // Main content
                VStack(spacing: 0) {
                    if viewModel.isLoading {
                        loadingView
                    } else if viewModel.hasSearched && viewModel.searchResults.isEmpty && !viewModel.searchText.isEmpty {
                        emptyResultsView
                    } else if !viewModel.searchResults.isEmpty {
                        resultsView
                    } else {
                        searchHistoryView
                    }
                }
                .background(Color.appMintCream)
            }
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
        .background(Color.appMintCream)
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
        .fullScreenCover(isPresented: $showDetailView) {
            if let result = selectedResult {
                DetailViewContainer(result: result, isPresented: $showDetailView)
            }
        }
    }
    
    // Combined view for source and results
    private var resultsView: some View {
        VStack(spacing: 0) {
            // Source header
            if let firstResult = viewModel.searchResults.first {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Original Source")
                        .font(.interBold(size: 14))
                        .foregroundColor(Color.appSmokyBlack.opacity(0.6))
                        .padding(.horizontal, 16)
                        .padding(.top, 16)
                    
                    HStack(alignment: .top, spacing: 12) {
                        // Thumbnail image
                        if let thumbnail = firstResult.thumbnailImage {
                            Image(uiImage: thumbnail)
                                .resizable()
                                .scaledToFill()
                                .frame(width: 80, height: 80)
                                .clipShape(RoundedRectangle(cornerRadius: 8))
                        } else {
                            RoundedRectangle(cornerRadius: 8)
                                .fill(Color.gray.opacity(0.2))
                                .frame(width: 80, height: 80)
                                .overlay(
                                    Image(systemName: "photo")
                                        .foregroundColor(Color.gray)
                                )
                        }
                        
                        VStack(alignment: .leading, spacing: 6) {
                            Text(firstResult.source)
                                .font(.interMedium(size: 15))
                                .foregroundColor(Color.appSmokyBlack)
                            
                            Text(firstResult.title)
                                .font(.interBold(size: 18))
                                .foregroundColor(Color.appSmokyBlack)
                                .lineLimit(2)
                            
                            Text(firstResult.description)
                                .font(.interRegular(size: 14))
                                .foregroundColor(Color.appSmokyBlack.opacity(0.7))
                                .lineLimit(3)
                            
                            HStack(spacing: 12) {
                                Text(firstResult.author)
                                    .font(.interRegular(size: 13))
                                    .foregroundColor(Color.appSmokyBlack.opacity(0.6))
                                
                                Text(dateFormatter.string(from: firstResult.publishDate))
                                    .font(.interRegular(size: 13))
                                    .foregroundColor(Color.appSmokyBlack.opacity(0.6))
                            }
                            
                            Text(firstResult.url.absoluteString)
                                .font(.interRegular(size: 13))
                                .foregroundColor(Color.blue)
                                .lineLimit(1)
                                .truncationMode(.middle)
                            
                            if let label = firstResult.label {
                                Text(label)
                                    .font(.interMedium(size: 13))
                                    .foregroundColor(.white)
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 3)
                                    .background(Color.appSandyBrown)
                                    .clipShape(Capsule())
                            }
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 16)
                }
                .background(Color.white)
                .padding(.horizontal, 16)
            }
            
            // Results list title
            HStack {
                Text("Results")
                    .font(.interBold(size: 18))
                    .foregroundColor(Color.appSmokyBlack)
                Spacer()
            }
            .padding(.horizontal, 16)
            .padding(.top, 16)
            .padding(.bottom, 8)
            
            // Results list
            ScrollView {
                LazyVStack(spacing: 0) {
                    ForEach(viewModel.searchResults) { result in
                        Button(action: {
                            selectedResult = result
                            showDetailView = true
                        }) {
                            VStack(alignment: .leading, spacing: 8) {
                                Text(result.title)
                                    .font(.interBold(size: 17))
                                    .foregroundColor(Color.appSmokyBlack)
                                Text(result.description)
                                    .font(.interRegular(size: 15))
                                    .foregroundColor(Color.appSmokyBlack.opacity(0.7))
                                    .lineLimit(2)
                            }
                            .padding(.vertical, 12)
                            .padding(.horizontal, 16)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(Color.white)
                        }
                        
                        Divider()
                            .background(Color.appSmokyBlack.opacity(0.1))
                            .padding(.horizontal, 16)
                    }
                }
            }
            .background(Color.white)
            .padding(.horizontal, 16)
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
                ScrollView {
                    VStack(spacing: 0) {
                        Text("Recent Searches")
                            .font(.interBold(size: 16))
                            .foregroundColor(Color.appSmokyBlack)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.horizontal, 16)
                            .padding(.vertical, 12)
                            .background(Color.white)
                        
                        Divider()
                            .background(Color.appSmokyBlack.opacity(0.1))
                        
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
                                .padding(.vertical, 12)
                                .padding(.horizontal, 16)
                                .background(Color.white)
                            }
                            
                            Divider()
                                .background(Color.appSmokyBlack.opacity(0.1))
                                .padding(.horizontal, 16)
                        }
                    }
                    .background(Color.white)
                    .cornerRadius(12)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
                    
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
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                    }
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
    
    private let dateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter
    }()
}

// Add this structure for the detail view
struct DetailViewContainer: View {
    let result: SearchResult
    @Binding var isPresented: Bool
    
    var body: some View {
        ZStack(alignment: .topLeading) {
            ResultDetailView(result: result)
                .environmentObject(AppState())
            
            Button(action: {
                isPresented = false
            }) {
                Image(systemName: "chevron.left")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(Color.appSmokyBlack)
                    .padding(12)
                    .background(Circle().fill(Color.white.opacity(0.8)))
                    .padding(16)
            }
        }
        .edgesIgnoringSafeArea(.bottom)
    }
}

#Preview {
    SearchView()
        .environmentObject(AppState())
} 