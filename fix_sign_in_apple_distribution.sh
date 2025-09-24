#!/bin/bash

echo "🔧 Fixing Sign in with Apple Distribution Provisioning Profile..."

# Navigate to the iOS project directory
cd /Users/apple/BAIQApp/CascadeProjects/AI-Learning/flutter_app/ios

echo "📝 Updating project.pbxproj for automatic distribution signing..."

# Set automatic signing with distribution certificate
sed -i '' 's/CODE_SIGN_STYLE = Manual/CODE_SIGN_STYLE = Automatic/g' Runner.xcodeproj/project.pbxproj

# Set the correct distribution certificate
sed -i '' 's/CODE_SIGN_IDENTITY = "Apple Distribution: SHIQIANG QIN (92NUAQ6A5K)"/CODE_SIGN_IDENTITY = "Apple Distribution: SHIQIANG QIN (92NUAQ6A5K)"/g' Runner.xcodeproj/project.pbxproj

# Set provisioning profile to automatic
sed -i '' 's/PROVISIONING_PROFILE_SPECIFIER = .*/PROVISIONING_PROFILE_SPECIFIER = ""/g' Runner.xcodeproj/project.pbxproj

# Ensure provisioning profile is required
if ! grep -q "PROVISIONING_PROFILE_REQUIRED = YES" Runner.xcodeproj/project.pbxproj; then
  sed -i '' '/DEVELOPMENT_TEAM = 92NUAQ6A5K/a\t\t\t\tPROVISIONING_PROFILE_REQUIRED = YES;' Runner.xcodeproj/project.pbxproj
fi

echo "✅ Sign in with Apple distribution configuration updated!"

# Verify the changes
echo "🔍 Verifying changes..."
xcodebuild -project Runner.xcodeproj -target Runner -configuration Release -showBuildSettings | grep -E "(CODE_SIGN_IDENTITY|DEVELOPMENT_TEAM|PROVISIONING_PROFILE_REQUIRED)"

echo "🎉 Sign in with Apple distribution configuration complete!"


