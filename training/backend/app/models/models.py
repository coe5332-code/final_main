"""
SQLAlchemy ORM Models for BSK Training Optimization API

This module defines all database models (tables) using SQLAlchemy ORM.
Each class represents a table in the database.

Author: BSK Team
Version: 2.0.0
"""

from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime
from sqlalchemy.sql import func
from datetime import datetime, timezone
from .database import Base


# ============================================================================
# BSK MASTER MODEL
# ============================================================================


class BSKMaster(Base):
    """
    Bank Sathi Kendra (BSK) Master table

    Stores information about all BSK centers including location,
    contact details, and operational information.
    """

    __tablename__ = "ml_bsk_master"
    __table_args__ = {"schema": "dbo"}

    # Primary Key
    bsk_id = Column(
        Integer, primary_key=True, index=True, comment="Unique BSK identifier"
    )

    # Basic Information
    bsk_name = Column(String(200), comment="Name of the BSK center")
    bsk_code = Column(String(50), index=True, comment="Unique BSK code")
    bsk_type = Column(String, comment="Type of BSK (e.g., Urban, Rural)")
    bsk_sub_type = Column(String, comment="Sub-type classification")

    # Location Information
    district_name = Column(String(50), comment="District name")
    district_id = Column(Integer, index=True, comment="District ID reference")
    sub_division_name = Column(String, comment="Sub-division name")
    sub_div_id = Column(Integer, comment="Sub-division ID reference")
    block_municipalty_name = Column(String, comment="Block/Municipality name")
    block_mun_id = Column(Integer, comment="Block/Municipality ID reference")
    gp_ward = Column(String, comment="GP/Ward name")
    gp_id = Column(Integer, comment="GP/Ward ID reference")
    gp_ward_distance = Column(String(50), comment="Distance from GP/Ward")
    pin = Column(String(10), comment="PIN code")

    # Contact & Address
    bsk_address = Column(String(500), comment="Full address of BSK")
    bsk_lat = Column(String(50), comment="Latitude coordinate")
    bsk_long = Column(String(50), comment="Longitude coordinate")
    bsk_account_no = Column(String(30), comment="Bank account number")
    bsk_landline_no = Column(String(20), comment="Landline phone number")

    # Operational Information
    no_of_deos = Column(Integer, default=0, comment="Number of DEOs assigned")
    is_aadhar_center = Column(Integer, default=0, comment="Aadhaar center flag (0/1)")
    is_saturday_open = Column(Text, comment="Saturday operation status")
    is_active = Column(Boolean, default=True, comment="Active status flag")

    def __repr__(self):
        return f"<BSKMaster(bsk_id={self.bsk_id}, bsk_name='{self.bsk_name}', bsk_code='{self.bsk_code}')>"


# ============================================================================
# DEO MASTER MODEL
# ============================================================================


class DEOMaster(Base):
    """
    Data Entry Operator (DEO) Master table

    Stores information about DEO agents who manage BSK operations.
    """

    __tablename__ = "ml_deo_master"
    __table_args__ = {"schema": "dbo"}

    # Primary Key
    agent_id = Column(
        Integer, primary_key=True, index=True, comment="Unique agent identifier"
    )

    # User Information
    user_id = Column(Integer, index=True, comment="User ID reference")
    user_name = Column(String(200), comment="Full name of the agent")
    agent_code = Column(
        String(50), unique=True, index=True, comment="Unique agent code"
    )
    user_emp_no = Column(String, comment="Employee number")
    grp = Column(Text, comment="Group/Category")

    # Contact Information
    agent_email = Column(String(250), comment="Email address")
    agent_phone = Column(String(50), comment="Phone number")

    # BSK Assignment
    bsk_id = Column(Integer, index=True, comment="Assigned BSK ID")
    bsk_name = Column(String(200), comment="Assigned BSK name")
    bsk_code = Column(String(50), comment="Assigned BSK code")
    bsk_post = Column(String(100), comment="Post/Position at BSK")

    # Location References
    bsk_distid = Column(Integer, comment="District ID reference")
    bsk_subdivid = Column(Integer, comment="Sub-division ID reference")
    bsk_blockid = Column(Integer, comment="Block ID reference")
    bsk_gpwdid = Column(Integer, comment="GP/Ward ID reference")

    # Status & Dates
    date_of_engagement = Column(Text, comment="Date of joining/engagement")
    user_islocked = Column(Boolean, default=False, comment="Account locked status")
    is_active = Column(Boolean, default=True, comment="Active status flag")

    def __repr__(self):
        return f"<DEOMaster(agent_id={self.agent_id}, user_name='{self.user_name}', agent_code='{self.agent_code}')>"


# ============================================================================
# SERVICE MASTER MODEL
# ============================================================================


class ServiceMaster(Base):
    """
    Service Master table

    Catalog of all services that can be provided by BSK centers.
    """

    __tablename__ = "ml_service_master"
    __table_args__ = {"schema": "dbo"}

    # Primary Key
    service_id = Column(
        Integer, primary_key=True, index=True, comment="Unique service identifier"
    )

    # Service Information
    service_name = Column(String(600), comment="Official name of the service")
    common_name = Column(Text, comment="Common/popular name")
    action_name = Column(Text, comment="Action/process name")
    service_link = Column(String(600), comment="URL link to service details")
    service_desc = Column(Text, comment="Detailed description of the service")

    # Department Information
    department_id = Column(Integer, index=True, comment="Department ID reference")
    department_name = Column(Text, comment="Department name")

    # Service Classification
    service_type = Column(String(1), comment="Service type code")
    is_new = Column(Integer, default=0, comment="New service flag (0/1)")
    is_active = Column(Integer, default=1, comment="Active status (0/1)")
    is_paid_service = Column(Boolean, default=False, comment="Paid service flag")

    # Application Information
    how_to_apply = Column(Text, comment="Application process description")
    eligibility_criteria = Column(Text, comment="Eligibility requirements")
    required_doc = Column(Text, comment="Required documents list")

    def __repr__(self):
        return f"<ServiceMaster(service_id={self.service_id}, service_name='{self.service_name}')>"


# ============================================================================
# PROVISION MODEL
# ============================================================================


class Provision(Base):
    """
    Provision/Transaction table

    Records of services provided to customers at BSK centers.
    """

    __tablename__ = "ml_provision"
    __table_args__ = {"schema": "dbo"}

    # Primary Key
    customer_id = Column(Text, primary_key=True, comment="Unique customer identifier")

    # BSK Information
    bsk_id = Column(Integer, index=True, comment="BSK ID where service was provided")
    bsk_name = Column(String(200), comment="BSK name")

    # Customer Information
    customer_name = Column(String, comment="Customer name")
    customer_phone = Column(String, comment="Customer phone number")

    # Service Information
    service_id = Column(Integer, index=True, comment="Service ID reference")
    service_name = Column(String(600), comment="Service name")

    # Transaction Details
    prov_date = Column(Text, comment="Date of service provision")
    docket_no = Column(String, comment="Docket/reference number")

    def __repr__(self):
        return f"<Provision(customer_id='{self.customer_id}', service_id={self.service_id}, bsk_id={self.bsk_id})>"


# ============================================================================
# CITIZEN MASTER V2 MODEL
# ============================================================================


class CitizenMasterV2(Base):
    """
    Citizen Master table (Version 2)

    Stores demographic and contact information for citizens.
    """

    __tablename__ = "ml_citizen_master_v2"
    __table_args__ = {"schema": "dbo"}

    # Primary Key
    citizen_id = Column(
        Text, primary_key=True, index=True, comment="Unique citizen identifier"
    )

    # Contact Information
    citizen_phone = Column(String, index=True, comment="Primary phone number")
    alt_phone = Column(String, comment="Alternative phone number")
    email = Column(String, comment="Email address")

    # Personal Information
    citizen_name = Column(String, comment="Full name")
    guardian_name = Column(String(200), comment="Father/Guardian name")
    gender = Column(String(10), comment="Gender")
    dob = Column(String(30), comment="Date of birth")
    age = Column(Integer, comment="Age")

    # Location References
    district_id = Column(Integer, index=True, comment="District ID reference")
    sub_div_id = Column(Integer, comment="Sub-division ID reference")
    gp_id = Column(Integer, comment="GP/Ward ID reference")

    # Demographics
    caste = Column(String(50), comment="Caste category")
    religion = Column(String(30), comment="Religion")

    def __repr__(self):
        return f"<CitizenMasterV2(citizen_id='{self.citizen_id}', citizen_name='{self.citizen_name}')>"


# ============================================================================
# REFERENCE/LOOKUP TABLES
# ============================================================================


class DepartmentMaster(Base):
    """Department Master - Catalog of government departments"""

    __tablename__ = "ml_department_master"
    __table_args__ = {"schema": "dbo"}

    dept_id = Column(Integer, primary_key=True, index=True)
    dept_name = Column(String(600))

    def __repr__(self):
        return (
            f"<DepartmentMaster(dept_id={self.dept_id}, dept_name='{self.dept_name}')>"
        )


class District(Base):
    """District Master - List of districts"""

    __tablename__ = "ml_district"
    __table_args__ = {"schema": "dbo"}

    district_id = Column(Integer, primary_key=True, index=True)
    district_name = Column(String(50))
    district_code = Column(String(20), unique=True)
    grp = Column(String(10))

    def __repr__(self):
        return f"<District(district_id={self.district_id}, district_name='{self.district_name}')>"


class BlockMunicipality(Base):
    """Block/Municipality Master"""

    __tablename__ = "ml_block_municipality"
    __table_args__ = {"schema": "dbo"}

    block_muni_id = Column(Integer, primary_key=True, index=True)
    block_muni_name = Column(String)
    sub_div_id = Column(Integer, index=True)
    district_id = Column(Integer, index=True)
    bm_type = Column(String)

    def __repr__(self):
        return f"<BlockMunicipality(block_muni_id={self.block_muni_id}, block_muni_name='{self.block_muni_name}')>"


class GPWardMaster(Base):
    """Gram Panchayat/Ward Master"""

    __tablename__ = "ml_gp_ward_master"
    __table_args__ = {"schema": "dbo"}

    gp_id = Column(Integer, primary_key=True, index=True)
    district_id = Column(String)
    sub_div_id = Column(Integer)
    block_muni_id = Column(String)
    gp_ward_name = Column(String)

    def __repr__(self):
        return f"<GPWardMaster(gp_id={self.gp_id}, gp_ward_name='{self.gp_ward_name}')>"


class PostOfficeMaster(Base):
    """Post Office Master"""

    __tablename__ = "ml_post_office_master"
    __table_args__ = {"schema": "dbo"}

    post_office_id = Column(Integer, primary_key=True, index=True)
    post_office_name = Column(String(250))
    pin_code = Column(String(7), index=True)
    district_id = Column(Integer, index=True)

    def __repr__(self):
        return f"<PostOfficeMaster(post_office_id={self.post_office_id}, post_office_name='{self.post_office_name}')>"


# ============================================================================
# SERVICE VIDEO MODEL
# ============================================================================


class ServiceVideo(Base):
    """
    Service Video table

    Tracks video content for services (generated from PDFs, forms, or uploads).
    One row per service - uses service_id as primary key.
    """

    __tablename__ = "service_videos"
    __table_args__ = {"schema": "dbo"}

    # Primary Key (service_id - one video per service)
    service_id = Column(
        Integer, primary_key=True, index=True, comment="Service ID (primary key)"
    )

    # Core Fields
    service_name = Column(String(600), nullable=False, comment="Name of the service")
    video_version = Column(
        Integer, nullable=False, default=1, comment="Version number of video"
    )
    source_type = Column(
        String(50), nullable=False, comment="Source: 'pdf', 'form', or 'uploaded'"
    )

    # Status Flags
    is_new = Column(Boolean, default=True, comment="Flag indicating if video is new")
    is_done = Column(
        Boolean, default=False, comment="Flag indicating if processing is complete"
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when record was created",
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="Timestamp when record was last updated",
    )

    def __repr__(self):
        return f"<ServiceVideo(service_id={self.service_id}, service_name='{self.service_name}', version={self.video_version})>"
