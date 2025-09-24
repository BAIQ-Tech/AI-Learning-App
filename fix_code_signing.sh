#!/bin/bash

echo "🔧 Fixing Code Signing for Distribution..."

# Navigate to the iOS project directory
cd /Users/apple/BAIQApp/CascadeProjects/AI-Learning/flutter_app/ios

# Update the project.pbxproj file to use distribution certificate
echo "📝 Updating project.pbxproj file..."

# Replace iPhone Developer with iPhone Distribution
sed -i '' 's/iPhone Developer/iPhone Distribution/g' Runner.xcodeproj/project.pbxproj

# Replace development provisioning profile with distribution
sed -i '' 's/CODE_SIGN_STYLE = Automatic/CODE_SIGN_STYLE = Automatic\n\t\t\tCODE_SIGN_IDENTITY = "iPhone Distribution"/g' Runner.xcodeproj/project.pbxproj

echo "✅ Code signing settings updated!"

# Verify the changes
echo "🔍 Verifying changes..."
xcodebuild -project Runner.xcodeproj -target Runner -configuration Release -showBuildSettings | grep -E "(CODE_SIGN_IDENTITY|DEVELOPMENT_TEAM|PROVISIONING_PROFILE)"

echo "🎉 Code signing fix completed!"


