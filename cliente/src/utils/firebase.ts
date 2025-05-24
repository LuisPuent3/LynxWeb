// Firebase configuration temporarily disabled for Docker build
// This file provides empty exports to prevent build failures

// Mock exports for firebase functions
export const signInWithEmail = async (email: string, password: string) => {
  console.warn('Firebase not configured - signInWithEmail mock');
  return { user: null, error: 'Firebase not configured' };
};

export const signUpWithEmail = async (email: string, password: string) => {
  console.warn('Firebase not configured - signUpWithEmail mock');
  return { user: null, error: 'Firebase not configured' };
};

export const signInWithGoogle = async () => {
  console.warn('Firebase not configured - signInWithGoogle mock');
  return { user: null, error: 'Firebase not configured' };
};

export const getGoogleRedirectResult = async () => {
  console.warn('Firebase not configured - getGoogleRedirectResult mock');
  return { user: null, error: 'Firebase not configured' };
};

export const logOut = async () => {
  console.warn('Firebase not configured - logOut mock');
  return { success: false, error: 'Firebase not configured' };
};

// Mock auth object
export const auth = {
  currentUser: null
};