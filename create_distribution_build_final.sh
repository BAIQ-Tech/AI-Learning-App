#!/bin/bash

echo "🔧 Creating Distribution Build for App Store Connect..."

# Navigate to the iOS project directory
cd /Users/apple/BAIQApp/CascadeProjects/AI-Learning/flutter_app/ios

echo "📝 Updating project.pbxproj for distribution signing..."

# Update the project to use distribution certificate
sed -i '' 's/CODE_SIGN_IDENTITY = "Apple Development"/CODE_SIGN_IDENTITY = "Apple Distribution: SHIQIANG QIN (92NUAQ6A5K)"/g' Runner.xcodeproj/project.pbxproj

# Update SDK-specific code signing identity
sed -i '' 's/"CODE_SIGN_IDENTITY\[sdk=iphoneos\*\]" = "Apple Development";/"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "Apple Distribution: SHIQIANG QIN (92NUAQ6A5K)";/g' Runner.xcodeproj/project.pbxproj

# Set to manual signing for distribution
sed -i '' 's/CODE_SIGN_STYLE = Automatic/CODE_SIGN_STYLE = Manual/g' Runner.xcodeproj/project.pbxproj

# Set provisioning profile to automatic (will use the correct one)
sed -i '' 's/PROVISIONING_PROFILE_SPECIFIER = .*/PROVISIONING_PROFILE_SPECIFIER = ""/g' Runner.xcodeproj/project.pbxproj

echo "✅ Distribution configuration updated!"

# Verify the changes
echo "🔍 Verifying changes..."
xcodebuild -project Runner.xcodeproj -target Runner -configuration Release -showBuildSettings | grep -E "(CODE_SIGN_IDENTITY|DEVELOPMENT_TEAM|PROVISIONING_PROFILE)"

echo "🎉 Distribution configuration complete!"


