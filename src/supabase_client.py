"""Supabase client initialization for PsychoCrowd."""
import os
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

def get_supabase_client() -> Client:
    """Initialize and return the Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
    return create_client(SUPABASE_URL, SUPABASE_KEY)
