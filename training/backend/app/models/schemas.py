from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BSKMaster(BaseModel):
    bsk_id: int
    bsk_name: Optional[str]
    district_name: Optional[str]
    sub_division_name: Optional[str]
    block_municipalty_name: Optional[str]
    gp_ward: Optional[str]
    gp_ward_distance: Optional[str]
    bsk_type: Optional[str]
    bsk_sub_type: Optional[str]
    bsk_code: Optional[str]
    no_of_deos: Optional[int]
    is_aadhar_center: Optional[int]
    bsk_address: Optional[str]
    bsk_lat: Optional[str]
    bsk_long: Optional[str]
    bsk_account_no: Optional[str]
    bsk_landline_no: Optional[str]
    is_saturday_open: Optional[str]
    is_active: Optional[bool]
    district_id: Optional[int]
    block_mun_id: Optional[int]
    gp_id: Optional[int]
    sub_div_id: Optional[int]
    pin: Optional[str]

    class Config:
        from_attributes = True

class ServiceMaster(BaseModel):
    service_id: int
    service_name: Optional[str]
    common_name: Optional[str]
    action_name: Optional[str]
    service_link: Optional[str]
    department_id: Optional[int]
    department_name: Optional[str]
    is_new: Optional[int]
    service_type: Optional[str]
    is_active: Optional[int]
    is_paid_service: Optional[bool]
    service_desc: Optional[str]
    how_to_apply: Optional[str]
    eligibility_criteria: Optional[str]
    required_doc: Optional[str]

    class Config:
        from_attributes = True

class DepartmentMaster(BaseModel):
    department_id: int
    department_name: str

    class Config:
        from_attributes = True

class DEOMaster(BaseModel):
    agent_id: int
    user_id: Optional[int]
    grp: Optional[str]
    user_name: Optional[str]
    agent_code: Optional[str]
    agent_email: Optional[str]
    agent_phone: Optional[str]
    date_of_engagement: Optional[str]
    user_emp_no: Optional[str]
    bsk_id: Optional[int]
    bsk_name: Optional[str]
    bsk_code: Optional[str]
    bsk_distid: Optional[int]
    bsk_subdivid: Optional[int]
    bsk_blockid: Optional[int]
    bsk_gpwdid: Optional[int]
    user_islocked: Optional[bool]
    is_active: Optional[bool]
    bsk_post: Optional[str]

    class Config:
        from_attributes = True

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
        from_attributes = True

class DistrictMaster(BaseModel):
    district_id: int
    district_name: str
    slave_db: str
    district_code: str

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional

class Provision(BaseModel):
    bsk_id: Optional[int]
    bsk_name: Optional[str]
    customer_id: str
    customer_name: Optional[str]
    customer_phone: Optional[str]
    service_id: Optional[int]
    service_name: Optional[str]
    prov_date: Optional[str]
    docket_no: Optional[str]

    class Config:
        from_attributes = True

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
        from_attributes = True

class BlockMunicipality(BaseModel):
    block_muni_id: int
    block_muni_name: Optional[str]
    sub_div_id: Optional[int]
    district_id: Optional[int]
    bm_type: Optional[str]
    class Config:
        from_attributes = True

class CitizenMasterV2(BaseModel):
    citizen_id: str
    citizen_phone: Optional[str]
    citizen_name: Optional[str]
    alt_phone: Optional[str]
    email: Optional[str]
    guardian_name: Optional[str]
    district_id: Optional[int]
    sub_div_id: Optional[int]
    gp_id: Optional[int]
    gender: Optional[str]
    dob: Optional[str]
    age: Optional[int]
    caste: Optional[str]
    religion: Optional[str]
    class Config:
        from_attributes = True

class DepartmentMaster(BaseModel):
    dept_id: int
    dept_name: Optional[str]
    class Config:
        from_attributes = True

class District(BaseModel):
    district_id: int
    district_name: Optional[str]
    district_code: Optional[str]
    grp: Optional[str]
    class Config:
        from_attributes = True

class GPWardMaster(BaseModel):
    gp_id: int
    district_id: Optional[str]
    sub_div_id: Optional[int]
    block_muni_id: Optional[str]
    gp_ward_name: Optional[str]
    class Config:
        from_attributes = True

class PostOfficeMaster(BaseModel):
    post_office_id: int
    post_office_name: Optional[str]
    pin_code: Optional[str]
    district_id: Optional[int]
    class Config:
        from_attributes = True 