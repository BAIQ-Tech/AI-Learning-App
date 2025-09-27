import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface User {
  id: string;
  email?: string;
  name: string;
  avatar?: string;
  authMethod: 'email' | 'google' | 'apple' | 'metamask' | 'coinbase' | 'phantom';
  walletAddress?: string;
}

interface AuthContextType {
  user: User | null;
  login: (emailOrMethod: string, password?: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on app load
    const checkAuthStatus = async () => {
      const savedUser = localStorage.getItem('ai-learning-user');
      const token = localStorage.getItem('authToken');
      
      if (savedUser && token) {
        try {
          // Verify token is still valid by calling backend
          const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
          const response = await fetch(`${apiUrl}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });
          
          if (response.ok) {
            // Token is valid, restore user session
            setUser(JSON.parse(savedUser));
          } else {
            // Token is invalid/expired, clear session
            console.log('Token expired or invalid, clearing session');
            localStorage.removeItem('ai-learning-user');
            localStorage.removeItem('authToken');
            setUser(null);
          }
        } catch (error) {
          console.error('Error verifying token:', error);
          // Clear session on error
          localStorage.removeItem('ai-learning-user');
          localStorage.removeItem('authToken');
          setUser(null);
        }
      }
      setIsLoading(false);
    };
    
    checkAuthStatus();
  }, []);

  const login = async (method: string, credentials?: any) => {
    setIsLoading(true);
    try {
      let userData: User;

      switch (method) {
        case 'email':
          userData = await loginWithEmail(credentials);
          break;
        case 'google':
          userData = await loginWithGoogle();
          break;
        case 'apple':
          userData = await loginWithApple();
          break;
        case 'metamask':
          userData = await loginWithMetaMask();
          break;
        case 'coinbase':
          userData = await loginWithCoinbase();
          break;
        case 'phantom':
          userData = await loginWithPhantom();
          break;
        default:
          throw new Error('Unsupported authentication method');
      }

      // Set user in context
      setUser(userData);
      
      // The individual login methods should have already stored the token
      // Let's verify it exists
      const token = localStorage.getItem('authToken');
      console.log('Login completed - Token stored:', token ? 'Yes' : 'No');
      console.log('Login completed - User:', userData);
      
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('ai-learning-user');
    localStorage.removeItem('authToken');
  };

  const loginWithEmail = async (credentials: { email: string; password: string }): Promise<User> => {
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/auth/email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      throw new Error('Email login failed');
    }

    const data = await response.json();
    
    // Store JWT token
    localStorage.setItem('authToken', data.token);
    
    return {
      id: data.user.id.toString(),
      email: data.user.email,
      name: data.user.name,
      avatar: data.user.avatar,
      authMethod: 'email',
    };
  };

  const loginWithGoogle = async (): Promise<User> => {
    return new Promise((resolve, reject) => {
      // Wait for Google SDK to load
      const checkGoogleSDK = () => {
        if (typeof window !== 'undefined' && window.google && window.google.accounts) {
          // Initialize Google Sign-In
          window.google.accounts.id.initialize({
            client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID || 'your-google-client-id.googleusercontent.com',
            callback: async (response: any) => {
              try {
                // Decode JWT token to get user info
                const payload = JSON.parse(atob(response.credential.split('.')[1]));
                
                // Send to backend for verification
                const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
                const backendResponse = await fetch(`${apiUrl}/api/auth/social`, {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({
                    provider: 'google',
                    token: response.credential,
                    user_info: {
                      id: payload.sub,
                      email: payload.email,
                      name: payload.name,
                      picture: payload.picture,
                    },
                  }),
                });

                if (!backendResponse.ok) {
                  throw new Error('Google authentication failed');
                }

                const data = await backendResponse.json();
                localStorage.setItem('authToken', data.token);

                resolve({
                  id: data.user.id.toString(),
                  email: data.user.email,
                  name: data.user.name,
                  avatar: data.user.avatar,
                  authMethod: 'google',
                });
              } catch (error) {
                reject(error);
              }
            },
          });

          // Trigger the sign-in popup
          window.google.accounts.id.prompt();
        } else {
          // Retry after a short delay
          setTimeout(checkGoogleSDK, 100);
        }
      };

      checkGoogleSDK();
      
      // Timeout after 10 seconds
      setTimeout(() => {
        reject(new Error('Google Sign-In not available. Please check your internet connection.'));
      }, 10000);
    });
  };

  const loginWithApple = async (): Promise<User> => {
    return new Promise((resolve, reject) => {
      // Wait for Apple SDK to load
      const checkAppleSDK = () => {
        if (typeof window !== 'undefined' && window.AppleID) {
          // Initialize Apple Sign-In
          window.AppleID.auth.init({
            clientId: process.env.REACT_APP_APPLE_CLIENT_ID || 'com.ailearning.service',
            scope: 'name email',
            redirectURI: window.location.origin,
            state: 'apple-signin',
            usePopup: true,
          });

          window.AppleID.auth.signIn().then(async (response: any) => {
            try {
              // Send to backend for verification
              const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
              const backendResponse = await fetch(`${apiUrl}/api/auth/social`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  provider: 'apple',
                  token: response.authorization.id_token,
                  user_info: {
                    id: response.user,
                    email: response.email,
                    name: response.name ? `${response.name.firstName} ${response.name.lastName}` : 'Apple User',
                  },
                }),
              });

              if (!backendResponse.ok) {
                throw new Error('Apple authentication failed');
              }

              const data = await backendResponse.json();
              localStorage.setItem('authToken', data.token);

              resolve({
                id: data.user.id.toString(),
                email: data.user.email,
                name: data.user.name,
                authMethod: 'apple',
              });
            } catch (error) {
              reject(error);
            }
          }).catch(reject);
        } else {
          // Retry after a short delay
          setTimeout(checkAppleSDK, 100);
        }
      };

      checkAppleSDK();
      
      // Timeout after 10 seconds
      setTimeout(() => {
        reject(new Error('Apple Sign-In not available. Please check your internet connection.'));
      }, 10000);
    });
  };

  const loginWithMetaMask = async (): Promise<User> => {
    if (typeof window === 'undefined' || !window.ethereum) {
      throw new Error('MetaMask not installed');
    }

    try {
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts',
      });

      const account = accounts[0];
      const message = `Sign in to AI-Learning with your wallet: ${Date.now()}`;

      const signature = await window.ethereum.request({
        method: 'personal_sign',
        params: [message, account],
      });

      // Call backend wallet login endpoint
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/auth/wallet`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          wallet_address: account,
          signature,
          message,
          wallet_type: 'metamask'
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'MetaMask authentication failed');
      }

      const data = await response.json();
      const userData: User = {
        id: data.user.id.toString(),
        name: data.user.name,
        authMethod: 'metamask',
        walletAddress: account,
      };

      console.log('MetaMask authentication successful:', userData);
      setUser(userData);
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('ai-learning-user', JSON.stringify(userData));

      return userData;

    } catch (error) {
      throw new Error('MetaMask connection failed');
    }
  };

  const loginWithCoinbase = async (): Promise<User> => {
    try {
      // Advanced Coinbase Wallet detection with comprehensive error handling
      let coinbaseProvider = null;
      
      console.log('🔍 Starting Coinbase Wallet detection...');
      
      // Wait for provider injection (some extensions need time)
      await new Promise(resolve => setTimeout(resolve, 100));
      
      console.log('📊 Available providers:', {
        ethereum: !!window.ethereum,
        ethereumProviders: window.ethereum?.providers?.length || 0,
        isCoinbaseWallet: window.ethereum?.isCoinbaseWallet,
        isCoinbaseBrowser: window.ethereum?.isCoinbaseBrowser,
        isMetaMask: window.ethereum?.isMetaMask,
        coinbaseWalletExtension: !!(window as any).coinbaseWalletExtension,
        coinbase: !!(window as any).coinbase,
        ethereum_coinbase: !!(window as any).ethereum?.coinbase
      });
      
      // Check if window.ethereum exists
      if (typeof window === 'undefined' || typeof window.ethereum === 'undefined') {
        // Check for alternative Coinbase injection points
        if ((window as any).coinbase) {
          console.log('🔄 Found window.coinbase, attempting to use it');
          coinbaseProvider = (window as any).coinbase;
        } else {
          throw new Error('Web3 wallet not detected. Please install Coinbase Wallet extension from https://wallet.coinbase.com/ and refresh the page.');
        }
      }
      
      if (!coinbaseProvider) {
        // Method 1: Direct Coinbase Wallet detection
        if (window.ethereum?.isCoinbaseWallet) {
          coinbaseProvider = window.ethereum;
          console.log('✅ Method 1: Coinbase Wallet detected via isCoinbaseWallet flag');
        }
        // Method 2: Multi-wallet environment - comprehensive search
        else if (window.ethereum?.providers && Array.isArray(window.ethereum.providers)) {
          console.log('🔍 Method 2: Searching through providers array...');
          for (let i = 0; i < window.ethereum.providers.length; i++) {
            const provider = window.ethereum.providers[i];
            console.log(`Provider ${i}:`, {
              isCoinbaseWallet: provider.isCoinbaseWallet,
              isCoinbaseBrowser: provider.isCoinbaseBrowser,
              isMetaMask: provider.isMetaMask,
              selectedAddress: provider.selectedAddress,
              _metamask: provider._metamask,
              isCoinbase: provider.isCoinbase
            });
            
            if (provider.isCoinbaseWallet || provider.isCoinbaseBrowser || provider.isCoinbase) {
              coinbaseProvider = provider;
              console.log(`✅ Coinbase Wallet found at provider index ${i}`);
              break;
            }
          }
        }
        // Method 3: Check for Coinbase Browser extension
        else if (window.ethereum?.isCoinbaseBrowser) {
          coinbaseProvider = window.ethereum;
          console.log('✅ Method 3: Coinbase Browser detected');
        }
        // Method 4: Check window.coinbaseWalletExtension
        else if ((window as any).coinbaseWalletExtension) {
          coinbaseProvider = (window as any).coinbaseWalletExtension;
          console.log('✅ Method 4: Coinbase Wallet detected via coinbaseWalletExtension');
        }
        // Method 5: Check for Coinbase SDK injection
        else if ((window as any).CoinbaseWalletSDK) {
          console.log('🔍 Method 5: Found CoinbaseWalletSDK, attempting initialization...');
          try {
            const CoinbaseWalletSDK = (window as any).CoinbaseWalletSDK;
            const coinbaseWallet = new CoinbaseWalletSDK({
              appName: 'AI-Learning',
              appLogoUrl: window.location.origin + '/favicon.ico',
              darkMode: false
            });
            coinbaseProvider = coinbaseWallet.makeWeb3Provider();
            console.log('✅ Coinbase Wallet SDK initialized');
          } catch (sdkError) {
            console.log('❌ SDK initialization failed:', sdkError);
          }
        }
        // Method 6: Force enable Coinbase by requesting accounts first
        else if (window.ethereum) {
          console.log('🔍 Method 6: Attempting to force Coinbase detection...');
          try {
            // First, try to get accounts to see if Coinbase responds
            const testAccounts = await window.ethereum.request({
              method: 'eth_accounts'
            });
            
            // Try to get the wallet name/version
            const walletInfo = await window.ethereum.request({
              method: 'web3_clientVersion'
            }).catch(() => null);
            
            console.log('Wallet info:', { testAccounts, walletInfo });
            
            // If we have accounts or wallet responds, assume it might be Coinbase
            if (testAccounts?.length > 0 || walletInfo) {
              // Try to switch to mainnet to trigger proper wallet identification
              try {
                await window.ethereum.request({
                  method: 'wallet_switchEthereumChain',
                  params: [{ chainId: '0x1' }], // Ethereum mainnet
                });
              } catch (switchError) {
                console.log('Network switch not needed or failed');
              }
              
              // Check again after network operations
              if (window.ethereum.isCoinbaseWallet) {
                coinbaseProvider = window.ethereum;
                console.log('✅ Coinbase Wallet detected after network operations');
              } else {
                // Use as fallback but warn user
                coinbaseProvider = window.ethereum;
                console.log('⚠️ Using ethereum provider as Coinbase fallback');
              }
            }
          } catch (forceError) {
            console.log('❌ Force detection failed:', forceError);
          }
        }
      }
      
      if (!coinbaseProvider) {
        throw new Error('Coinbase Wallet not found. Please install the extension from https://wallet.coinbase.com/ and refresh the page.');
      }
      
      // Request account access with enhanced error handling and retry logic
      console.log('🔐 Requesting account access from Coinbase Wallet...');
      let accounts;
      let retryCount = 0;
      const maxRetries = 5;
      
      // First, check if we already have accounts
      try {
        const existingAccounts = await coinbaseProvider.request({ method: 'eth_accounts' });
        if (existingAccounts && existingAccounts.length > 0) {
          console.log('✅ Found existing connected accounts:', existingAccounts);
          accounts = existingAccounts;
        }
      } catch (existingError) {
        console.log('No existing accounts found, will request new connection');
      }
      
      // If no existing accounts, request new connection
      if (!accounts || accounts.length === 0) {
        while (retryCount < maxRetries) {
          try {
            console.log(`🔄 Connection attempt ${retryCount + 1}/${maxRetries}`);
            
            // Add a small delay before each attempt to allow wallet to be ready
            if (retryCount > 0) {
              await new Promise(resolve => setTimeout(resolve, 1500));
            }
            
            accounts = await coinbaseProvider.request({ 
              method: 'eth_requestAccounts' 
            });
            
            if (accounts && accounts.length > 0) {
              console.log('✅ Successfully connected to accounts:', accounts);
              break;
            } else {
              throw new Error('No accounts returned from wallet');
            }
          } catch (requestError: any) {
            retryCount++;
            console.log(`❌ Attempt ${retryCount} failed:`, {
              code: requestError.code,
              message: requestError.message,
              data: requestError.data
            });
            
            if (retryCount >= maxRetries) {
              if (requestError.code === 4001) {
                throw new Error('Connection rejected by user. Please click "Connect" in your Coinbase Wallet when prompted.');
              } else if (requestError.code === -32002) {
                throw new Error('Connection request already pending. Please check your Coinbase Wallet and approve the connection.');
              } else if (requestError.code === -32603) {
                throw new Error('Internal wallet error. Please restart Coinbase Wallet and try again.');
              } else if (requestError.message?.includes('User rejected')) {
                throw new Error('Connection rejected. Please approve the connection request in Coinbase Wallet.');
              } else {
                throw new Error(`Connection failed after ${maxRetries} attempts: ${requestError.message || 'Unknown error'}. Please ensure Coinbase Wallet is installed, unlocked, and try refreshing the page.`);
              }
            }
          }
        }
      }
      
      if (!accounts || accounts.length === 0) {
        throw new Error('No accounts found. Please unlock your Coinbase Wallet and try again.');
      }
      
      const address = accounts[0];
      console.log('✅ Connected to Coinbase Wallet address:', address);
      
      // Verify the connection by checking if we can get the current account
      try {
        const currentAccounts = await coinbaseProvider.request({
          method: 'eth_accounts'
        });
        console.log('🔍 Current accounts verification:', currentAccounts);
        
        // Also try to get chain ID to ensure wallet is responsive
        const chainId = await coinbaseProvider.request({
          method: 'eth_chainId'
        });
        console.log('🌐 Current chain ID:', chainId);
      } catch (verifyError) {
        console.warn('⚠️ Could not verify connection:', verifyError);
      }
      
      // Create message to sign with timestamp for uniqueness
      const timestamp = Date.now();
      const message = `Sign in to AI-Learning\nTimestamp: ${timestamp}\nAddress: ${address}`;
      
      // Request signature with enhanced error handling and retry logic
      console.log('✍️ Requesting signature...');
      let signature;
      let signRetryCount = 0;
      const maxSignRetries = 3;
      
      while (signRetryCount < maxSignRetries) {
        try {
          console.log(`🔄 Signature attempt ${signRetryCount + 1}/${maxSignRetries}`);
          
          signature = await coinbaseProvider.request({
            method: 'personal_sign',
            params: [message, address],
          });
          
          if (!signature) {
            throw new Error('No signature returned from wallet');
          }
          
          console.log('✅ Signature received successfully');
          break;
        } catch (signError: any) {
          signRetryCount++;
          console.error(`❌ Signature attempt ${signRetryCount} failed:`, {
            code: signError.code,
            message: signError.message
          });
          
          if (signRetryCount >= maxSignRetries) {
            if (signError.code === 4001) {
              throw new Error('Signature rejected by user. Please approve the signature request in your Coinbase Wallet.');
            } else if (signError.code === -32603) {
              throw new Error('Wallet internal error during signing. Please restart Coinbase Wallet and try again.');
            } else if (signError.message?.includes('User rejected')) {
              throw new Error('Signature rejected. Please approve the signature request in Coinbase Wallet.');
            } else {
              throw new Error(`Signature failed after ${maxSignRetries} attempts: ${signError.message || 'Unknown error'}`);
            }
          }
          
          // Wait before retry
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }
      
      // Call backend wallet login endpoint
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/auth/wallet`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          wallet_address: address,
          signature,
          message,
          wallet_type: 'coinbase'
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Coinbase Wallet認証に失敗しました');
      }
      
      const data = await response.json();
      const userData: User = {
        id: data.user.id.toString(),
        name: data.user.name,
        authMethod: 'coinbase',
        walletAddress: address,
      };
      
      console.log('Coinbase Wallet authentication successful:', userData);
      setUser(userData);
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('ai-learning-user', JSON.stringify(userData));
      
      return userData;
      
    } catch (error: any) {
      console.error('Coinbase Wallet authentication error:', error);
      
      // Provide better error messages based on error codes
      if (error.code === 4001) {
        throw new Error('Connection rejected. Please approve the connection in Coinbase Wallet.');
      } else if (error.code === -32002) {
        throw new Error('Connection request pending. Please check your Coinbase Wallet.');
      } else if (error.code === -32603) {
        throw new Error('Internal error. Please try again or restart Coinbase Wallet.');
      } else if (error.message?.includes('User rejected') || error.message?.includes('rejected')) {
        throw new Error('Connection rejected. Please approve the connection in Coinbase Wallet.');
      } else if (error.message?.includes('not installed') || error.message?.includes('not found')) {
        throw new Error('Coinbase Wallet not found. Please install the extension and refresh the page.');
      } else if (error.message?.includes('unlock')) {
        throw new Error('Please unlock your Coinbase Wallet and try again.');
      } else {
        throw new Error(`Coinbase Wallet error: ${error.message || 'Unknown error occurred'}`);
      }
    }
  };

  const loginWithPhantom = async (): Promise<User> => {
    if (typeof window === 'undefined' || !window.solana?.isPhantom) {
      throw new Error('Phantom Wallet not installed');
    }

    try {
      const response = await window.solana.connect();
      const publicKey = response.publicKey.toString();

      // Create message to sign
      const message = `Sign in to AI-Learning with your wallet: ${Date.now()}`;

      // Sign the message with Phantom
      const encodedMessage = new TextEncoder().encode(message);
      const signature = await window.solana.signMessage(encodedMessage, 'utf8');

      // Convert signature to base64 for backend
      const signatureBase64 = btoa(String.fromCharCode(...signature.signature));

      // Call backend wallet login endpoint
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const backendResponse = await fetch(`${apiUrl}/api/auth/wallet`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          wallet_address: publicKey,
          signature: signatureBase64,
          message,
          wallet_type: 'phantom'
        }),
      });

      if (!backendResponse.ok) {
        const errorData = await backendResponse.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Phantom Wallet authentication failed');
      }

      const data = await backendResponse.json();
      const userData: User = {
        id: data.user.id.toString(),
        name: data.user.name,
        authMethod: 'phantom',
        walletAddress: publicKey,
      };

      console.log('Phantom Wallet authentication successful:', userData);
      setUser(userData);
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('ai-learning-user', JSON.stringify(userData));

      return userData;

    } catch (error) {
      throw new Error('Phantom Wallet connection failed');
    }
  };

  const register = async (email: string, password: string, name: string) => {
    setIsLoading(true);
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, name }),
      });

      if (!response.ok) {
        throw new Error('Registration failed');
      }

      const data = await response.json();
      
      // Store JWT token
      localStorage.setItem('authToken', data.token);
      
      const userData: User = {
        id: data.user.id.toString(),
        email: data.user.email,
        name: data.user.name,
        authMethod: 'email',
      };

      setUser(userData);
      localStorage.setItem('ai-learning-user', JSON.stringify(userData));
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const value = {
    user,
    isLoading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Extend window interface for wallet types
declare global {
  interface Window {
    ethereum?: any;
    solana?: any;
    google?: any;
    AppleID?: any;
  }
}
