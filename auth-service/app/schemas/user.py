from pydantic import BaseModel, EmailStr, field_validator

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr  # Uses email-validator
    business_name: str

    @field_validator("email")
    def email_must_contain_domain(cls, v):
        # if "example.com" in v:  # Replace with your allowed domain
        #     raise ValueError("Disposable emails not allowed")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    username: str
    email: EmailStr
    business_name: str