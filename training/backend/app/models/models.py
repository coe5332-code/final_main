from sqlalchemy import Column, Integer, String, Boolean, Float, Text
from datetime import datetime, timezone
from .database import Base


class BSKMaster(Base):
    __tablename__ = "ml_bsk_master"
    __table_args__ = {"schema": "dbo"}

    bsk_id = Column(Integer, primary_key=True, index=True)
    bsk_name = Column(String(200))
    district_name = Column(String(50))
    sub_division_name = Column(String)
    block_municipalty_name = Column(String)
    gp_ward = Column(String)
    gp_ward_distance = Column(String(50))
    bsk_type = Column(String)
    bsk_sub_type = Column(String)
    bsk_code = Column(String(50))
    no_of_deos = Column(Integer)
    is_aadhar_center = Column(Integer)
    bsk_address = Column(String(500))
    bsk_lat = Column(String(50))
    bsk_long = Column(String(50))
    bsk_account_no = Column(String(30))
    bsk_landline_no = Column(String(20))
    is_saturday_open = Column(Text)
    is_active = Column(Boolean)
    district_id = Column(Integer)
    block_mun_id = Column(Integer)
    gp_id = Column(Integer)
    sub_div_id = Column(Integer)
    pin = Column(String(10))


class DEOMaster(Base):
    __tablename__ = "ml_deo_master"
    __table_args__ = {"schema": "dbo"}

    agent_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    grp = Column(Text)
    user_name = Column(String(200))
    agent_code = Column(String(50))
    agent_email = Column(String(250))
    agent_phone = Column(String(50))
    date_of_engagement = Column(Text)
    user_emp_no = Column(String)
    bsk_id = Column(Integer)
    bsk_name = Column(String(200))
    bsk_code = Column(String(50))
    bsk_distid = Column(Integer)
    bsk_subdivid = Column(Integer)
    bsk_blockid = Column(Integer)
    bsk_gpwdid = Column(Integer)
    user_islocked = Column(Boolean)
    is_active = Column(Boolean)
    bsk_post = Column(String(100))


class ServiceMaster(Base):
    __tablename__ = "ml_service_master"
    __table_args__ = {"schema": "dbo"}

    service_id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(600))
    common_name = Column(Text)
    action_name = Column(Text)
    service_link = Column(String(600))
    department_id = Column(Integer)
    department_name = Column(Text)
    is_new = Column(Integer)
    service_type = Column(String(1))
    is_active = Column(Integer)
    is_paid_service = Column(Boolean)
    service_desc = Column(Text)
    how_to_apply = Column(Text)
    eligibility_criteria = Column(Text)
    required_doc = Column(Text)


class Provision(Base):
    __tablename__ = "ml_provision"
    __table_args__ = {"schema": "dbo"}

    bsk_id = Column(Integer)
    bsk_name = Column(String(200))
    customer_id = Column(Text, primary_key=True)
    customer_name = Column(String)
    customer_phone = Column(String)
    service_id = Column(Integer)
    service_name = Column(String(600))
    prov_date = Column(Text)
    docket_no = Column(String)


class BlockMunicipality(Base):
    __tablename__ = "ml_block_municipality"
    __table_args__ = {"schema": "dbo"}
    block_muni_id = Column(Integer, primary_key=True, index=True)
    block_muni_name = Column(String)
    sub_div_id = Column(Integer)
    district_id = Column(Integer)
    bm_type = Column(String)


class CitizenMasterV2(Base):
    __tablename__ = "ml_citizen_master_v2"
    __table_args__ = {"schema": "dbo"}
    citizen_id = Column(Text, primary_key=True, index=True)
    citizen_phone = Column(String)
    citizen_name = Column(String)
    alt_phone = Column(String)
    email = Column(String)
    guardian_name = Column(String(200))
    district_id = Column(Integer)
    sub_div_id = Column(Integer)
    gp_id = Column(Integer)
    gender = Column(String(10))
    dob = Column(String(30))
    age = Column(Integer)
    caste = Column(String(50))
    religion = Column(String(30))


class DepartmentMaster(Base):
    __tablename__ = "ml_department_master"
    __table_args__ = {"schema": "dbo"}
    dept_id = Column(Integer, primary_key=True, index=True)
    dept_name = Column(String(600))


class District(Base):
    __tablename__ = "ml_district"
    __table_args__ = {"schema": "dbo"}
    district_id = Column(Integer, primary_key=True, index=True)
    district_name = Column(String(50))
    district_code = Column(String(20))
    grp = Column(String(10))


class GPWardMaster(Base):
    __tablename__ = "ml_gp_ward_master"
    __table_args__ = {"schema": "dbo"}
    gp_id = Column(Integer, primary_key=True, index=True)
    district_id = Column(String)
    sub_div_id = Column(Integer)
    block_muni_id = Column(String)
    gp_ward_name = Column(String)


class PostOfficeMaster(Base):
    __tablename__ = "ml_post_office_master"
    __table_args__ = {"schema": "dbo"}
    post_office_id = Column(Integer, primary_key=True, index=True)
    post_office_name = Column(String(250))
    pin_code = Column(String(7))
    district_id = Column(Integer)


# At the top of your models.py file, update the imports:

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime

# Then in your ServiceVideo model, update the DateTime columns:

class ServiceVideo(Base):
    __tablename__ = "service_videos"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, nullable=False, index=True)
    service_name = Column(Text)
    video_version = Column(Integer, nullable=False)
    source_type = Column(Text)
    is_new = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

