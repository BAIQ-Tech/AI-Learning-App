#!/bin/bash

echo "🔧 Fixing Xcode Project for Manual Signing..."

# Navigate to the iOS project directory
cd /Users/apple/BAIQApp/CascadeProjects/AI-Learning/flutter_app/ios

# Update the project.pbxproj file for manual signing
echo "📝 Updating project.pbxproj for manual signing..."

# Replace automatic signing with manual signing
sed -i '' 's/CODE_SIGN_STYLE = Automatic/CODE_SIGN_STYLE = Manual/g' Runner.xcodeproj/project.pbxproj

# Set the correct distribution certificate
sed -i '' 's/CODE_SIGN_IDENTITY = "iPhone Distribution"/CODE_SIGN_IDENTITY = "Apple Distribution: SHIQIANG QIN (92NUAQ6A5K)"/g' Runner.xcodeproj/project.pbxproj

# Set provisioning profile to automatic (will use the correct one)
sed -i '' 's/PROVISIONING_PROFILE_SPECIFIER = .*/PROVISIONING_PROFILE_SPECIFIER = ""/g' Runner.xcodeproj/project.pbxproj

echo "✅ Manual signing configuration updated!"

# Verify the changes
echo "🔍 Verifying changes..."
xcodebuild -project Runner.xcodeproj -target Runner -configuration Release -showBuildSettings | grep -E "(CODE_SIGN_IDENTITY|CODE_SIGN_STYLE|DEVELOPMENT_TEAM|PROVISIONING_PROFILE)"

echo "🎉 Manual signing fix completed!"


