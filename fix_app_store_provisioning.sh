#!/bin/bash

echo "🔧 Fixing App Store Provisioning Profile..."

# Navigate to the iOS project directory
cd /Users/apple/BAIQApp/CascadeProjects/AI-Learning/flutter_app/ios

echo "📝 Updating project.pbxproj for App Store distribution..."

# Update the project to use automatic signing with distribution certificate
sed -i '' 's/CODE_SIGN_STYLE = Manual/CODE_SIGN_STYLE = Automatic/g' Runner.xcodeproj/project.pbxproj

# Set the correct distribution certificate
sed -i '' 's/CODE_SIGN_IDENTITY = "Apple Distribution: SHIQIANG QIN (92NUAQ6A5K)"/CODE_SIGN_IDENTITY = "iPhone Distribution"/g' Runner.xcodeproj/project.pbxproj

# Set provisioning profile to automatic
sed -i '' 's/PROVISIONING_PROFILE_SPECIFIER = .*/PROVISIONING_PROFILE_SPECIFIER = ""/g' Runner.xcodeproj/project.pbxproj

echo "✅ App Store provisioning configuration updated!"

# Verify the changes
echo "🔍 Verifying changes..."
xcodebuild -project Runner.xcodeproj -target Runner -configuration Release -showBuildSettings | grep -E "(CODE_SIGN_IDENTITY|CODE_SIGN_STYLE|DEVELOPMENT_TEAM|PROVISIONING_PROFILE)"

echo "🎉 App Store provisioning fix completed!"


