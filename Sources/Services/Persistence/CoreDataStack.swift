import CoreData

/// Core Data stack with encryption-ready setup
final class CoreDataStack {
    static let shared = CoreDataStack()
    let container: NSPersistentContainer

    private init() {
        container = NSPersistentContainer(name: "Traceit")
        // TODO: Add encryption options here if using SQLCipher or NSPersistentCloudKitContainer
        container.loadPersistentStores { _, error in
            if let error = error {
                fatalError("Unresolved error: \(error)")
            }
        }
    }

    var context: NSManagedObjectContext {
        container.viewContext
    }
} 