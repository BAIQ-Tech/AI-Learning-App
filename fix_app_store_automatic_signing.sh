#!/bin/bash

echo "🔧 Fixing App Store Automatic Signing with Sign in with Apple..."

# Navigate to the iOS project directory
cd /Users/apple/BAIQApp/CascadeProjects/AI-Learning/flutter_app/ios

echo "📝 Updating project.pbxproj for automatic App Store signing..."

# Update the project to use automatic signing with development certificate for now
sed -i '' 's/CODE_SIGN_IDENTITY = "Apple Distribution: SHIQIANG QIN (92NUAQ6A5K)"/CODE_SIGN_IDENTITY = "Apple Development"/g' Runner.xcodeproj/project.pbxproj

# Update SDK-specific code signing identity
sed -i '' 's/"CODE_SIGN_IDENTITY\[sdk=iphoneos\*\]" = "Apple Distribution: SHIQIANG QIN (92NUAQ6A5K)";/"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "Apple Development";/g' Runner.xcodeproj/project.pbxproj

# Ensure automatic signing is enabled
sed -i '' 's/CODE_SIGN_STYLE = Manual/CODE_SIGN_STYLE = Automatic/g' Runner.xcodeproj/project.pbxproj

# Set provisioning profile to automatic
sed -i '' 's/PROVISIONING_PROFILE_SPECIFIER = .*/PROVISIONING_PROFILE_SPECIFIER = ""/g' Runner.xcodeproj/project.pbxproj

echo "✅ Automatic signing configuration updated!"

# Verify the changes
echo "🔍 Verifying changes..."
xcodebuild -project Runner.xcodeproj -target Runner -configuration Release -showBuildSettings | grep -E "(CODE_SIGN_IDENTITY|DEVELOPMENT_TEAM|PROVISIONING_PROFILE)"

echo "🎉 Automatic signing configuration complete!"


