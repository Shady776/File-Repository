from passlib.context import CryptContext

pwd_cxt = CryptContext(
    schemes=['bcrypt'],
    deprecated="auto"
)

def bcrypt(plainTextPassword: str) -> str:
    return pwd_cxt.hash(plainTextPassword)


def verify_hash(plainTextPassword: str, hashedPassword: str) -> bool:
    return pwd_cxt.verify(plainTextPassword, hashedPassword)