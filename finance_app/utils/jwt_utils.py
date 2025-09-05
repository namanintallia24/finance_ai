import jwt
from django.conf import settings
from datetime import datetime, timedelta

SECRET_KEY = settings.SECRET_KEY

def generate_jwt(user):
    payload = {
        "user_id": user.id,         # ✅ DRF expects this
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(hours=5),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_jwt(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
