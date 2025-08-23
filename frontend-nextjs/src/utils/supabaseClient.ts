import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});

// Types for our database schema
export interface User {
  id: string;
  email: string;
  user_metadata?: {
    role?: string;
    name?: string;
  };
}

export interface AuthState {
  user: User | null;
  session: any | null;
  loading: boolean;
}

export interface Profile {
  id: string;
  user_id: string;
  full_name?: string;
  avatar_url?: string;
  role: string;
  tenant_id?: string;
  created_at: string;
  updated_at: string;
}
