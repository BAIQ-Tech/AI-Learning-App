# 🍎 iOS Distribution Certificate Fix Guide

## ❌ **Current Problem**
- **Error**: "Invalid Provisioning Profile. Missing code-signing certificate"
- **Root Cause**: App is signed with Apple Development certificate instead of Apple Distribution certificate
- **Required**: Apple Distribution certificate for App Store Connect submission

## ✅ **Solution Steps**

### **Step 1: Create Apple Distribution Certificate**
1. **Open Xcode** → **Preferences** → **Accounts**
2. **Select your Apple ID** → **Manage Certificates**
3. **Click "+"** → **Apple Distribution**
4. **Download and install** the certificate

### **Step 2: Create App Store Provisioning Profile**
1. **Go to** [Apple Developer Portal](https://developer.apple.com/account/)
2. **Certificates, Identifiers & Profiles** → **Profiles**
3. **Click "+"** → **App Store** → **Continue**
4. **Select App ID**: `com.ailearning.app`
5. **Select Distribution Certificate** (the one you just created)
6. **Name it**: "AI Learning App Store"
7. **Download and install** the profile

### **Step 3: Update Xcode Project Settings**
1. **Open** `flutter_app/ios/Runner.xcworkspace` in Xcode
2. **Select Runner** → **Signing & Capabilities**
3. **Team**: Select your team
4. **Provisioning Profile**: Select "AI Learning App Store"
5. **Signing Certificate**: Apple Distribution

### **Step 4: Build for Distribution**
```bash
cd flutter_app
flutter clean
flutter pub get
flutter build ios --release --no-codesign
```

### **Step 5: Archive in Xcode**
1. **Open** `flutter_app/ios/Runner.xcworkspace` in Xcode
2. **Select** "Any iOS Device (arm64)" as target
3. **Product** → **Archive**
4. **Distribute App** → **App Store Connect** → **Upload**

## 🔧 **Alternative: Manual IPA Creation**

If Xcode archive fails, create IPA manually:

```bash
# Build the app
cd flutter_app
flutter build ios --release

# Create Payload directory
mkdir -p build/ios/ipa_payload/Payload
cp -r build/ios/iphoneos/Runner.app build/ios/ipa_payload/Payload/

# Create IPA
cd build/ios/ipa_payload
zip -r ../ai_learning_app_distribution.ipa Payload/
```

## 📋 **Required Files**
- ✅ Apple Distribution Certificate
- ✅ App Store Provisioning Profile
- ✅ Updated Xcode project settings
- ✅ Distribution-signed IPA

## 🚨 **Important Notes**
- **Development certificates** cannot be used for App Store submission
- **Distribution certificates** are required for TestFlight and App Store
- **Provisioning profiles** must match the certificate type
- **Bundle ID** must be registered in Apple Developer Portal

## 📞 **Next Steps**
1. Create Apple Distribution certificate
2. Create App Store provisioning profile
3. Update Xcode project settings
4. Build and archive in Xcode
5. Upload to App Store Connect

## 🔍 **Verification**
After fixing, verify with:
```bash
# Check certificate type
security find-identity -v -p codesigning

# Should show "Apple Distribution" not "Apple Development"
```


