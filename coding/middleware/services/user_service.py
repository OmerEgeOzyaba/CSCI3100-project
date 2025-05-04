from werkzeug.security import generate_password_hash, check_password_hash
from middleware_data_classes import User, SoftwareLicense
from database import Database
import re
from typing import Tuple, Optional
from datetime import datetime, timezone

class UserService:
    def __init__(self):
        self.db = Database()
    def create_user(self, email, password, license_key):
        if not self._validate_email(email):
            return None, "Invalid email format"
        
        if password_error := self._enforce_password_policy(password):
            return None, password_error

        session = self.db.get_session()

        try:
            if session.query(User).filter(User.email == email).first():
                return None, "Email already registered"

            soft_license = session.query(SoftwareLicense).filter(SoftwareLicense.key == license_key).with_for_update()

            if not soft_license.first():
                return None, "Invalid software license"

            if soft_license.first().used_status:
                return None, "Software license already used"

            soft_license.update({"used_status": True})

            new_user = User(email = email,
                            password = generate_password_hash(password),
                            created_at = datetime.now(timezone.utc))

            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            return new_user, "Added new user"
        except Exception as e:
            session.rollback()
            return None, f"User registration failed: {str(e)}"
        finally:
            session.close()

    def _enforce_password_policy(self, password):
        if len(password)<8 or len(password)>32 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(r"\d", password) or not re.search(r"[!@#$%^&*()_+=-]", password):
            return "Password must be between 8-32 characters and contain an uppercase letter, a lowercase letter, a number, and a special character"
    def _validate_email(self, email):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.fullmatch(pattern, email))
