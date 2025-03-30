#aqui pondremos lo de supabase

from supabase import create_client

# Configuración de Supabase
SUPABASE_URL = 'https://pvbxycfrdbsxhkvdjzyl.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB2Ynh5Y2ZyZGJzeGhrdmRqenlsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk4MjI3NjksImV4cCI6MjA1NTM5ODc2OX0.L-o_wReQ-BWjH17xwiM__18dq1Un13Wf3QJPOToMQh4'

# Crear el cliente de Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Funciones para autenticación
def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response, None
    except Exception as e:
        return None, str(e)

def register_user(email, password):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return response, None
    except Exception as e:
        return None, str(e)

def logout_user():
    try:
        supabase.auth.sign_out()
        return True, None
    except Exception as e:
        return False, str(e)