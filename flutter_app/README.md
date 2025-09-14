# AI-Learning Flutter iOS App

A comprehensive Flutter iOS application for AI-powered language learning with multilingual support, authentication, and interactive learning features.

## Features

### 🔐 Authentication
- Email/password registration and login
- Google Sign-In integration
- Apple Sign-In support
- Web3 wallet authentication (placeholder)
- JWT token management with secure storage

### 🌍 Multilingual Support
- 9 supported languages: English, Japanese, Chinese, Spanish, Greek, Hebrew, German, French, Italian
- Complete localization with native language names
- Dynamic UI language switching
- Learning language selection

### 🎓 Core Learning Features
- **AI Chat**: Conversational practice with AI tutors
- **Voice Practice**: Speech-to-text and pronunciation feedback
- **Translation**: Real-time translation between supported languages
- **Lessons**: AI-generated lessons with vocabulary and grammar
- **Games**: Interactive vocabulary quizzes and language games

### 📱 iOS-Specific Features
- Native iOS design with Material 3
- Dark/light theme support
- Proper iOS permissions handling
- App Store ready configuration
- Firebase integration
- Social login with Apple ID

## Project Structure

```
lib/
├── core/
│   ├── config/           # App configuration and constants
│   ├── localization/     # i18n support for 9 languages
│   ├── models/          # Data models with JSON serialization
│   ├── providers/       # State management (Auth, Language, Theme)
│   ├── router/          # GoRouter navigation setup
│   ├── services/        # API services and utilities
│   ├── theme/           # Material 3 theme configuration
│   └── utils/           # Utility functions and helpers
├── features/
│   ├── auth/            # Authentication screens and widgets
│   ├── chat/            # AI chat functionality
│   ├── games/           # Language learning games
│   ├── home/            # Main dashboard and navigation
│   ├── lessons/         # Lesson generation and display
│   ├── profile/         # User profile and progress
│   ├── settings/        # App settings and preferences
│   ├── translation/     # Translation feature
│   └── voice/           # Voice practice and pronunciation
└── main.dart            # App entry point
```

## iOS Configuration

### Info.plist Permissions
- Microphone access for voice practice
- Camera access for future features
- Network access for API communication
- Localization support for 9 languages

### Bundle Configuration
- Bundle ID: `com.ailearning.app`
- Minimum iOS version: 11.0
- Supports iPhone and iPad
- URL schemes for social login

## Dependencies

### Core Flutter Packages
- `flutter`: SDK
- `provider`: State management
- `flutter_riverpod`: Advanced state management
- `go_router`: Declarative routing

### Authentication & Security
- `firebase_auth`: Firebase authentication
- `google_sign_in`: Google Sign-In
- `sign_in_with_apple`: Apple Sign-In
- `flutter_secure_storage`: Secure token storage

### API & Networking
- `dio`: HTTP client
- `retrofit`: Type-safe API client
- `json_annotation`: JSON serialization

### UI & Theming
- `google_fonts`: Typography
- `flutter_localizations`: Internationalization

### Device Features
- `speech_to_text`: Voice input
- `flutter_tts`: Text-to-speech
- `permission_handler`: iOS permissions

## Setup Instructions

### 1. Prerequisites
- Flutter SDK (latest stable)
- Xcode 12+ for iOS development
- iOS Simulator or physical iOS device
- Firebase project setup

### 2. Installation
```bash
# Clone the repository
git clone <repository-url>
cd flutter_app

# Install dependencies
flutter pub get

# Generate code (for JSON serialization)
flutter packages pub run build_runner build

# iOS setup
cd ios
pod install
cd ..
```

### 3. Firebase Configuration
1. Create a Firebase project
2. Add iOS app with bundle ID: `com.ailearning.app`
3. Download `GoogleService-Info.plist`
4. Place it in `ios/Runner/`
5. Enable Authentication providers in Firebase Console

### 4. API Configuration
Update `lib/core/config/app_config.dart`:
```dart
static const String apiBaseUrl = 'YOUR_BACKEND_URL';
static const String openaiApiKey = 'YOUR_OPENAI_KEY';
```

### 5. Run the App
```bash
# Run on iOS simulator
flutter run

# Build for release
flutter build ios --release
```

## App Store Submission

### Required Assets
- App icons (all sizes in Assets.xcassets)
- Launch screen images
- App Store screenshots
- App description and metadata

### Build Configuration
- Release build with proper signing
- Privacy policy URL
- Terms of service
- App Store Connect metadata

### Testing
- Test on multiple iOS devices
- Verify all permissions work correctly
- Test authentication flows
- Validate API integrations

## Backend Integration

The app connects to a FastAPI backend with endpoints for:
- User authentication (`/auth/`)
- AI conversation (`/conversation/`)
- Translation (`/translate/`)
- Lesson generation (`/lessons/`)
- Game content (`/games/`)
- Pronunciation checking (`/pronunciation/`)

## Contributing

1. Follow Flutter/Dart style guidelines
2. Add proper documentation for new features
3. Include unit tests for business logic
4. Test on iOS devices before submitting PRs
5. Update localization files for new strings

## License

[Add your license information here]

## Support

For technical support or questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

Built with ❤️ using Flutter for iOS
