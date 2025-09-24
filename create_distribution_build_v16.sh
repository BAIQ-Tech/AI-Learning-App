#!/bin/bash

echo "🔧 Creating Distribution Build for Version 16..."

# Navigate to the iOS project directory
cd /Users/apple/BAIQApp/CascadeProjects/AI-Learning/flutter_app/ios

echo "📝 Updating project.pbxproj for distribution signing..."

# Set the correct distribution certificate
sed -i '' 's/CODE_SIGN_IDENTITY = "Apple Development"/CODE_SIGN_IDENTITY = "Apple Distribution: SHIQIANG QIN (92NUAQ6A5K)"/g' Runner.xcodeproj/project.pbxproj
sed -i '' 's/CODE_SIGN_IDENTITY = "iPhone Distribution"/CODE_SIGN_IDENTITY = "Apple Distribution: SHIQIANG QIN (92NUAQ6A5K)"/g' Runner.xcodeproj/project.pbxproj

# Ensure provisioning profile is required
if ! grep -q "PROVISIONING_PROFILE_REQUIRED = YES" Runner.xcodeproj/project.pbxproj; then
  sed -i '' '/DEVELOPMENT_TEAM = 92NUAQ6A5K/a\t\t\t\tPROVISIONING_PROFILE_REQUIRED = YES;' Runner.xcodeproj/project.pbxproj
fi

# Set manual signing for distribution
sed -i '' 's/CODE_SIGN_STYLE = Automatic/CODE_SIGN_STYLE = Manual/g' Runner.xcodeproj/project.pbxproj

echo "✅ Distribution configuration updated!"

# Verify the changes
echo "🔍 Verifying changes..."
xcodebuild -project Runner.xcodeproj -target Runner -configuration Release -showBuildSettings | grep -E "(CODE_SIGN_IDENTITY|DEVELOPMENT_TEAM|PROVISIONING_PROFILE_REQUIRED)"

echo "🎉 Distribution configuration complete!"


