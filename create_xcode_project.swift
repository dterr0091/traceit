#!/usr/bin/swift

import Foundation

print("Creating new Xcode project...")

// Create project directory structure
try FileManager.default.createDirectory(atPath: "Traceit.xcodeproj", withIntermediateDirectories: true)
try FileManager.default.createDirectory(atPath: "Traceit.xcodeproj/project.xcworkspace", withIntermediateDirectories: true)
try FileManager.default.createDirectory(atPath: "Traceit.xcodeproj/xcshareddata/xcschemes", withIntermediateDirectories: true)
try FileManager.default.createDirectory(atPath: "Traceit.xcodeproj/project.xcworkspace/xcshareddata", withIntermediateDirectories: true)

// Create the xcscheme file
let schemeContent = """
<?xml version="1.0" encoding="UTF-8"?>
<Scheme
   LastUpgradeVersion = "1530"
   version = "1.7">
   <BuildAction
      parallelizeBuildables = "YES"
      buildImplicitDependencies = "YES">
      <BuildActionEntries>
         <BuildActionEntry
            buildForTesting = "YES"
            buildForRunning = "YES"
            buildForProfiling = "YES"
            buildForArchiving = "YES"
            buildForAnalyzing = "YES">
            <BuildableReference
               BuildableIdentifier = "primary"
               BlueprintIdentifier = "TraceitApp"
               BuildableName = "TraceitApp.app"
               BlueprintName = "TraceitApp"
               ReferencedContainer = "container:Traceit.xcodeproj">
            </BuildableReference>
         </BuildActionEntry>
      </BuildActionEntries>
   </BuildAction>
   <TestAction
      buildConfiguration = "Debug"
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      shouldUseLaunchSchemeArgsEnv = "YES"
      shouldAutocreateTestPlan = "YES">
   </TestAction>
   <LaunchAction
      buildConfiguration = "Debug"
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      launchStyle = "0"
      useCustomWorkingDirectory = "NO"
      ignoresPersistentStateOnLaunch = "NO"
      debugDocumentVersioning = "YES"
      debugServiceExtension = "internal"
      allowLocationSimulation = "YES">
      <BuildableProductRunnable
         runnableDebuggingMode = "0">
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "TraceitApp"
            BuildableName = "TraceitApp.app"
            BlueprintName = "TraceitApp"
            ReferencedContainer = "container:Traceit.xcodeproj">
         </BuildableReference>
      </BuildableProductRunnable>
   </LaunchAction>
   <ProfileAction
      buildConfiguration = "Release"
      shouldUseLaunchSchemeArgsEnv = "YES"
      savedToolIdentifier = ""
      useCustomWorkingDirectory = "NO"
      debugDocumentVersioning = "YES">
      <BuildableProductRunnable
         runnableDebuggingMode = "0">
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "TraceitApp"
            BuildableName = "TraceitApp.app"
            BlueprintName = "TraceitApp"
            ReferencedContainer = "container:Traceit.xcodeproj">
         </BuildableReference>
      </BuildableProductRunnable>
   </ProfileAction>
   <AnalyzeAction
      buildConfiguration = "Debug">
   </AnalyzeAction>
   <ArchiveAction
      buildConfiguration = "Release"
      revealArchiveInOrganizer = "YES">
   </ArchiveAction>
</Scheme>
"""

try schemeContent.write(toFile: "Traceit.xcodeproj/xcshareddata/xcschemes/TraceitApp.xcscheme", atomically: true, encoding: .utf8)

// Create a workspace contents file
let workspaceContent = """
<?xml version="1.0" encoding="UTF-8"?>
<Workspace
   version = "1.0">
   <FileRef
      location = "self:">
   </FileRef>
</Workspace>
"""

try workspaceContent.write(toFile: "Traceit.xcodeproj/project.xcworkspace/contents.xcworkspacedata", atomically: true, encoding: .utf8)

// Create an xcodeproj xcworkspace data
let xcsharedDataContent = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>IDEWorkspaceSharedSettings_AutocreateContextsIfNeeded</key>
	<true/>
</dict>
</plist>
"""

try xcsharedDataContent.write(toFile: "Traceit.xcodeproj/project.xcworkspace/xcshareddata/WorkspaceSettings.xcsettings", atomically: true, encoding: .utf8)

print("✅ Xcode project structure created")
print("Now open the project in Xcode and create a proper iOS App target") 