import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  GoogleAuthProvider,
  signInWithPopup,
  signInWithRedirect,
  getRedirectResult,
  signOut
} from 'firebase/auth';

// Configuración de Firebase
const firebaseConfig = {
  apiKey: "AIzaSyA5VdhVKg1N-Y5o4mYXJurydyXz4ia6fTw",
  authDomain: "lynxshop-auth.firebaseapp.com",
  projectId: "lynxshop-auth",
  storageBucket: "lynxshop-auth.appspot.com",
  messagingSenderId: "583214567890",
  appId: "1:583214567890:web:c1d2e3f4g5h6i7j8k9l0m1"
};

// Inicializar Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

// Funciones de autenticación
export const signInWithEmail = async (email: string, password: string) => {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    return { user: userCredential.user, error: null };
  } catch (error: any) {
    return { user: null, error: error.message };
  }
};

export const signUpWithEmail = async (email: string, password: string) => {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    return { user: userCredential.user, error: null };
  } catch (error: any) {
    return { user: null, error: error.message };
  }
};

// Función actualizada para usar redirección en lugar de popup
export const signInWithGoogle = async () => {
  try {
    // Esta función solo inicia el proceso de redirección
    await signInWithRedirect(auth, googleProvider);
    // La función no devuelve nada ya que la redirección ocurre
    return { user: null, error: null };
  } catch (error: any) {
    return { user: null, error: error.message };
  }
};

// Nueva función para obtener el resultado después de la redirección
export const getGoogleRedirectResult = async () => {
  try {
    const result = await getRedirectResult(auth);
    if (result) {
      return { user: result.user, error: null };
    }
    return { user: null, error: null };
  } catch (error: any) {
    return { user: null, error: error.message };
  }
};

export const logOut = async () => {
  try {
    await signOut(auth);
    return { success: true, error: null };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
};

export { auth }; 