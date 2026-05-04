from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
	"""
	Get token from Header, decoded and return User information
	If ticket is fake or expired, raise exception 401
	"""

	token = credentials.credentials
	try:
		decoded_token = auth.verify_id_token(token)
		return decoded_token # dict type
	except firebase_admin.auth.InvalidIdTokenError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid Token",
		)
	except firebase_admin.auth.ExpiredIdTokenError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Expired Token",
		)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail=f"Error: {str(e)}",
		)
