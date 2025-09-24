#!/bin/bash

# 🍎 AI Learning App - iOS Build Script
# This script automates the iOS build process for TestFlight submission

set -e  # Exit on any error

echo "🍎 AI Learning App - iOS Build Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "flutter_app/pubspec.yaml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    print_error "Flutter is not installed or not in PATH"
    print_status "Please install Flutter: https://docs.flutter.dev/get-started/install"
    exit 1
fi

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    print_error "Xcode is not installed or not in PATH"
    print_status "Please install Xcode from the Mac App Store"
    exit 1
fi

print_status "Starting iOS build process..."

# Navigate to Flutter app directory
cd flutter_app

# Clean previous builds
print_status "Cleaning previous builds..."
flutter clean

# Get dependencies
print_status "Getting Flutter dependencies..."
flutter pub get

# Check Flutter doctor
print_status "Checking Flutter environment..."
flutter doctor

# Build iOS app
print_status "Building iOS app for release..."
flutter build ios --release

# Check if build was successful
if [ $? -eq 0 ]; then
    print_success "iOS build completed successfully!"
    print_status "Build output location: flutter_app/build/ios/Release-iphoneos/Runner.app"
else
    print_error "iOS build failed!"
    exit 1
fi

# Navigate to iOS directory
cd ios

# Check if workspace exists
if [ ! -f "Runner.xcworkspace" ]; then
    print_error "Runner.xcworkspace not found!"
    exit 1
fi

print_status "iOS workspace found. You can now:"
print_status "1. Open Runner.xcworkspace in Xcode"
print_status "2. Select 'Any iOS Device' as target"
print_status "3. Product → Archive"
print_status "4. Upload to App Store Connect"

print_success "Build process completed!"
print_status "Next steps:"
print_status "- Open flutter_app/ios/Runner.xcworkspace in Xcode"
print_status "- Archive and upload to App Store Connect"
print_status "- Follow the TestFlight submission guide"

echo ""
echo "📱 App Information:"
echo "   Name: AI Learning"
echo "   Bundle ID: com.example.ai_learning_app"
echo "   Version: 1.0.0+2"
echo "   Platform: iOS"
echo ""
echo "🔗 Useful Links:"
echo "   - App Store Connect: https://appstoreconnect.apple.com"
echo "   - TestFlight: https://developer.apple.com/testflight/"
echo "   - Flutter iOS Guide: https://docs.flutter.dev/deployment/ios"


