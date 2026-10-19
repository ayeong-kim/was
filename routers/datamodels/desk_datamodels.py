from decimal import Decimal
from pydantic import BaseModel, Field


# 주인, 애완동물(단일, 다중) 등록 기능 요청 

class PetRequest(BaseModel):
    pname: str
    gender: str | None = None
    age: int | None = None
    weight: Decimal | None = None
    type: str
    breed: str | None = None
    notes: str | None = None

class OwnerRequest(BaseModel):
    oname: str
    pnum: str
    address: str | None = None
    pets: list[PetRequest] = Field(min_length=1)   # 최소 1마리

# 주인, 애완동물(단일, 다중) 등록 기능 응답 

class PetResponse(BaseModel):
    pid: int
    pname: str
    gender: str | None = None
    age: int | None = None
    weight: Decimal | None = None
    type: str
    breed: str | None = None
    notes: str | None = None

class OwnerResponse(BaseModel):
    oid: int
    oname: str
    pnum: str
    address: str | None = None
    pets: list[PetResponse]

# 주인 정보 수정 기능 요청 (str = None: 생략은 가능, null은 422)

class OwnerUpdate(BaseModel):
    oname: str = None
    pnum: str = None
    address: str | None = None

# 애완동물 정보 수정 기능 요청 (str = None: 생략은 가능, null은 422)

class PetUpdate(BaseModel):
    pname: str = None
    gender: str | None = None
    age: int | None = None
    weight: Decimal | None = None
    type: str = None
    breed: str | None = None
    notes: str | None = None

# 애완동물(단일, 다중) 추가 기능 요청

class PetAddRequest(BaseModel):
    oid: int
    pets: list[PetRequest] = Field(min_length=1)   # 최소 1마리

# 방문 등록 기능 요청

class ConsultationRequest(BaseModel):
    vet_uid: int
    purpose: str
