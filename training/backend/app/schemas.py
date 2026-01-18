from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BSKMaster(BaseModel):
    bsk_id: int
    bsk_center: str
    district: str
    sub_division: str
    block_mun: str
    gp_ward: str
    district_name_from_gp: str
    bsk_type: str
    bsk_subtype: str
    bsk_code: str
    no_of_deos: int
    is_aadhaar: bool
    bsk_address: str
    lat_lng: str
    bsk_account_no: str
    landline_no: str
    saturday_open: bool
    status: str

    class Config:
        orm_mode = True

class ServiceMaster(BaseModel):
    service_id: int
    service_name: str
    common_name: str
    action_name: str
    service_link: str
    department_id: int
    department_name: str
    is_new: bool
    service_type: str
    status: str
    api_response: Optional[str] = None

    class Config:
        orm_mode = True

class DepartmentMaster(BaseModel):
    department_id: int
    department_name: str

    class Config:
        orm_mode = True

class DEOMaster(BaseModel):
    agent_id: int
    user_id: str
    group: str
    name: str
    code: str
    email: str
    phone: str
    date_of_engagement: datetime
    employee_no: str
    bsk_center: str
    bsk_code: str
    district: str
    sub_division: str
    block_mu: str
    gp_ward_name: str
    status: str

    class Config:
        orm_mode = True

class CitizenMaster(BaseModel):
    citizen_id: int
    citizen_phone_no: str
    citizen_name: str
    alternative_phone_no: Optional[str] = None
    email: Optional[str] = None
    father_guardian_name: str
    district: str
    block_municipality: str
    post_office: str
    police_station: str
    house_no: str
    gender: str
    date_of_birth: datetime
    age: int
    caste: str
    religion: str

    class Config:
        orm_mode = True

class DistrictMaster(BaseModel):
    district_id: int
    district_name: str
    slave_db: str
    district_code: str

    class Config:
        orm_mode = True

class BSKTransaction(BaseModel):
    transaction_id: int
    transaction_date: datetime
    bsk_code: str
    transaction_amount: float
    transaction_time: datetime
    deo_code: str
    deo_name: str
    customer_id: int
    customer_name: str
    customer_phone: str
    service_id: int
    service_name: str

    class Config:
        orm_mode = True 
        
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ServiceVideoBase(BaseModel):
    service_id: int
    service_name: str
    video_version: int
    source_type: str
    is_new: bool = False

class ServiceVideoCreate(ServiceVideoBase):
    pass

class ServiceVideoUpdate(BaseModel):
    is_new: Optional[bool] = None
    updated_at: Optional[datetime] = None

class ServiceVideo(ServiceVideoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # For Pydantic v2 (or use orm_mode = True for v1)