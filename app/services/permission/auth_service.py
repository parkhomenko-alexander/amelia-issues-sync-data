from datetime import datetime, timedelta
from venv import create
from loguru import logger
from passlib.context import CryptContext

from app.db.models.system_user import SystemUser
from app.schemas.user_permission.auth_schemas import ShortUserSchema, ShortUserWithRoleSchema
from app.schemas.user_permission.system_user_schemas import SystemUserGetSchema
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork

from config import config

from jose import JWTError, jwt

TOKEN_TYPE_KEY = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

class AuthService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.pwd_context = CryptContext(schemes=["bcrypt"])

    @with_uow
    async def authentificate_user(self, login: str, password: str) -> ShortUserWithRoleSchema:
        user = await self.uow.system_user_repo.find_one(login=login)
        if not user: 
            resp = f"User '{login}' not authentificated"
            logger.error(resp)
            raise Exception(resp)
        if not self._verify_password(password, user.password_hash):
            resp = f"Error in auth process for {login}"
            logger.error(resp)
            raise Exception(resp)
        else:
            return ShortUserWithRoleSchema.model_validate(user)

    def encode_jwt(
        self,
        payload: dict,
        expire_minutes: int = config.APPLICATION_ACCESS_TOKEN_EXPIRE_MINUTES,
        expire_timedelta: timedelta | None = None,
        secret: str = config.APPLICATION_SECRET_KEY,
        algorithm: str = config.APPLICATION_HASH_ALGORITHM
    ) -> str:
        to_encode = payload.copy()
        now = datetime.now()
        if expire_timedelta:
            expire_date = now + expire_timedelta
        else:
            expire_date = now +timedelta(minutes=expire_minutes)
        to_encode.update(
            iat=now,
            exp=expire_date
        )
        encoded_jwt = jwt.encode(to_encode, secret, algorithm=algorithm)
        return encoded_jwt

    def decode_token(
        self,
        token:str,
        secret: str = config.APPLICATION_SECRET_KEY,
        algorithm: str = config.APPLICATION_HASH_ALGORITHM
    ):
        try:
            decoded = jwt.decode(token, secret, algorithms=[algorithm])
            login = decoded.get("login")
            role = decoded.get("role")
            if login is None or role is None:
                return None
            return decoded
        except JWTError:
            return None

    def create_jwt(
        self,
        token_type: str,
        token_data: dict,
        expire_minutes: int = config.APPLICATION_ACCESS_TOKEN_EXPIRE_MINUTES,
        expire_timedelta: timedelta | None = None
    ) -> str:
        jwt_payload = {
            TOKEN_TYPE_KEY: token_type
        }
        jwt_payload.update(token_data)

        return self.encode_jwt(
            payload=jwt_payload,
            expire_minutes=expire_minutes,
            expire_timedelta=expire_timedelta
        )

    def create_access_token(self, user: ShortUserSchema, role: str) -> str:
        jwt_payload = {
            "login": user.login,
            "role": role
        }

        return self.create_jwt(
            token_type=ACCESS_TOKEN_TYPE,
            token_data=jwt_payload,
            expire_minutes=config.APPLICATION_ACCESS_TOKEN_EXPIRE_MINUTES
        )


    def create_refresh_token(self, user: ShortUserSchema) -> str:
        jwt_payload = {
            "login": user.login,
        }

        return self.create_jwt(
            token_type=REFRESH_TOKEN_TYPE,
            token_data=jwt_payload,
            expire_timedelta=timedelta(minutes=config.APPLICATION_REFRESH_TOKEN_EXPIRE)
        )


    @staticmethod
    def _gen_password_hash(password: str) -> str:
        pwd_context = CryptContext(schemes=["bcrypt"])
        return pwd_context.hash(password)

    def _verify_password(self, password: str, password_hash: str) -> bool:
        return self.pwd_context.verify(password, password_hash)