"""
BSK Training Optimization API

A comprehensive FastAPI application for managing and optimizing training programs
for Bank Sathi Kendra (BSK) agents. This API provides endpoints for managing BSK
master data, service catalogs, DEO (Data Entry Operator) information, and provisions.
It also includes AI-powered analytics for identifying underperforming BSKs and
generating training recommendations.

Author: Your Team
Version: 1.0.0
"""

# Standard library imports
import logging
import os
import sys
from typing import List
from contextlib import asynccontextmanager

# Third-party imports
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Local application imports
from app.models import models
from app.models.schemas import (
    BSKMaster,
    ServiceMaster,
    DEOMaster,
    Provision,
    ServiceVideo,  # ✅ Add this - Pydantic schema
    ServiceVideoCreate,
    ServiceVideoUpdate,  # ✅ Add this too
)
from app.models.database import engine, get_db
from typing import Optional
from datetime import datetime

# Configure module paths for AI service and training modules
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../ai_service"))
)
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../deos_training"))
)

# Import AI and analytics functions
from bsk_analytics import find_underperforming_bsks
from training_recommendation import (
    training_recommendation,
)

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

# Configure logging with standardized format
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize database tables (idempotent operation for existing databases)
logger.info("Initializing database tables...")
models.Base.metadata.create_all(bind=engine)
logger.info("Database initialization complete")

# ============================================================================
# APPLICATION LIFECYCLE MANAGEMENT
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events.

    This context manager handles startup and shutdown tasks for the FastAPI
    application using the modern lifespan approach (recommended over deprecated
    on_event decorators).

    Startup tasks:
    - Log application initialization
    - Verify database connection
    - Display configuration info

    Shutdown tasks:
    - Log shutdown process
    - Cleanup resources

    Args:
        app: FastAPI application instance

    Yields:
        None: Control during application runtime
    """
    # Startup logic
    logger.info("=" * 80)
    logger.info("BSK Training Optimization API - Starting Up")
    logger.info("=" * 80)
    logger.info(f"Application Version: 1.0.0")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info("Database tables initialized successfully")
    logger.info("All systems ready - API is operational")
    logger.info("=" * 80)

    yield  # Application runs here

    # Shutdown logic
    logger.info("=" * 80)
    logger.info("BSK Training Optimization API - Shutting Down")
    logger.info("Performing cleanup tasks...")
    logger.info("Shutdown complete - Goodbye!")
    logger.info("=" * 80)


# ============================================================================
# FASTAPI APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title="BSK Training Optimization API",
    description="API for AI-Assisted Training Optimization System for Bank Sathi Kendra",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,  # Modern lifespan event handler
)

# Configure CORS middleware to allow cross-origin requests
# TODO: In production, replace allow_origins=["*"] with specific domain list
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # SECURITY: Update this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def convert_models_to_dataframe(model_list: List) -> pd.DataFrame:
    """
    Convert a list of SQLAlchemy model instances to a pandas DataFrame.

    This utility function handles the conversion of ORM objects to a DataFrame
    and removes SQLAlchemy's internal state tracking column.

    Args:
        model_list: List of SQLAlchemy model instances

    Returns:
        pd.DataFrame: DataFrame with model data, excluding internal state
    """
    df = pd.DataFrame([item.__dict__ for item in model_list])

    # Remove SQLAlchemy internal state column if present
    if "_sa_instance_state" in df.columns:
        df.drop("_sa_instance_state", axis=1, inplace=True)

    return df


def fetch_all_master_data(db: Session) -> tuple:
    """
    Fetch all master data from database and convert to DataFrames.

    This function retrieves all records from the four main tables:
    BSK Master, Provisions, DEO Master, and Service Master, and converts
    them to pandas DataFrames for analytics processing.

    Args:
        db: SQLAlchemy database session

    Returns:
        tuple: (bsks_df, provisions_df, deos_df, services_df)
    """
    logger.info("Fetching all master data from database...")

    # Retrieve all records from each table
    bsks = db.query(models.BSKMaster).all()
    provisions = db.query(models.Provision).all()
    deos = db.query(models.DEOMaster).all()
    services = db.query(models.ServiceMaster).all()

    logger.info(
        f"Retrieved {len(bsks)} BSKs, {len(provisions)} provisions, "
        f"{len(deos)} DEOs, {len(services)} services"
    )

    # Convert to DataFrames and clean up
    bsks_df = convert_models_to_dataframe(bsks)
    provisions_df = convert_models_to_dataframe(provisions)
    deos_df = convert_models_to_dataframe(deos)
    services_df = convert_models_to_dataframe(services)

    return bsks_df, provisions_df, deos_df, services_df


# ============================================================================
# ROOT ENDPOINT
# ============================================================================


@app.get("/", tags=["Health"])
def read_root():
    """
    Root endpoint - API health check.

    Returns basic API information to confirm the service is running.

    Returns:
        dict: Welcome message with API name
    """
    logger.info("Root endpoint accessed - health check")
    return {
        "message": "Welcome to BSK Training Optimization API",
        "version": "1.0.0",
        "status": "operational",
    }


# ============================================================================
# BSK MASTER ENDPOINTS
# ============================================================================


@app.get("/bsk/", response_model=List[BSKMaster], tags=["BSK Master"])
def get_bsk_list(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(None, ge=1, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated list of Bank Sathi Kendra (BSK) records.

    This endpoint supports pagination through skip and limit parameters,
    allowing efficient retrieval of large datasets.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return (None = all records)
        db: Database session dependency

    Returns:
        List[BSKMaster]: List of BSK master records
    """
    logger.info(f"GET /bsk/ - Fetching BSK list with skip={skip}, limit={limit}")

    # Build query with offset
    query = db.query(models.BSKMaster).offset(skip)

    # Apply limit if specified
    if limit is not None:
        query = query.limit(limit)

    bsk_list = query.all()
    logger.info(f"Successfully retrieved {len(bsk_list)} BSK records")

    return bsk_list


@app.get("/bsk/{bsk_code}", response_model=BSKMaster, tags=["BSK Master"])
def get_bsk(bsk_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific BSK record by its ID.

    Args:
        bsk_id: The unique identifier for the BSK
        db: Database session dependency

    Returns:
        BSKMaster: The requested BSK record

    Raises:
        HTTPException: 404 if BSK not found
    """
    logger.info(f"GET /bsk/{bsk_id} - Fetching BSK with ID: {bsk_id}")

    bsk = db.query(models.BSKMaster).filter(models.BSKMaster.bsk_id == bsk_id).first()

    if bsk is None:
        logger.warning(f"BSK not found with ID: {bsk_id}")
        raise HTTPException(status_code=404, detail=f"BSK not found with ID: {bsk_id}")

    logger.info(f"Successfully retrieved BSK: {bsk_id}")
    return bsk


# ============================================================================
# SERVICE MASTER ENDPOINTS
# ============================================================================


@app.get("/services/", response_model=List[ServiceMaster], tags=["Service Master"])
def get_services(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(None, ge=1, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated list of service records.

    Services represent the different banking services that can be provided
    by BSK agents (e.g., account opening, loan applications, etc.).

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return (None = all records)
        db: Database session dependency

    Returns:
        List[ServiceMaster]: List of service master records
    """
    logger.info(f"GET /services/ - Fetching services with skip={skip}, limit={limit}")

    # Build query with offset
    query = db.query(models.ServiceMaster).offset(skip)

    # Apply limit if specified
    if limit is not None:
        query = query.limit(limit)

    services = query.all()
    logger.info(f"Successfully retrieved {len(services)} service records")

    return services


@app.get(
    "/services/{service_id}", response_model=ServiceMaster, tags=["Service Master"]
)
def get_service(service_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific service record by its ID.

    Args:
        service_id: The unique identifier for the service
        db: Database session dependency

    Returns:
        ServiceMaster: The requested service record

    Raises:
        HTTPException: 404 if service not found
    """
    logger.info(f"GET /services/{service_id} - Fetching service with ID: {service_id}")

    service = (
        db.query(models.ServiceMaster)
        .filter(models.ServiceMaster.service_id == service_id)
        .first()
    )

    if service is None:
        logger.warning(f"Service not found with ID: {service_id}")
        raise HTTPException(
            status_code=404, detail=f"Service not found with ID: {service_id}"
        )

    logger.info(f"Successfully retrieved service: {service_id}")
    return service


# ============================================================================
# DEO MASTER ENDPOINTS
# ============================================================================


@app.get("/deo/", response_model=List[DEOMaster], tags=["DEO Master"])
def get_deo_list(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(None, ge=1, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated list of Data Entry Operator (DEO) records.

    DEOs are responsible for managing and overseeing BSK agents in their
    assigned territories.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return (None = all records)
        db: Database session dependency

    Returns:
        List[DEOMaster]: List of DEO master records
    """
    logger.info(f"GET /deo/ - Fetching DEO list with skip={skip}, limit={limit}")

    # Build query with offset
    query = db.query(models.DEOMaster).offset(skip)

    # Apply limit if specified
    if limit is not None:
        query = query.limit(limit)

    deo_list = query.all()
    logger.info(f"Successfully retrieved {len(deo_list)} DEO records")

    return deo_list


@app.get("/deo/{agent_id}", response_model=DEOMaster, tags=["DEO Master"])
def get_deo(agent_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific DEO record by agent ID.

    Args:
        agent_id: The unique identifier for the DEO agent
        db: Database session dependency

    Returns:
        DEOMaster: The requested DEO record

    Raises:
        HTTPException: 404 if DEO not found
    """
    logger.info(f"GET /deo/{agent_id} - Fetching DEO with agent ID: {agent_id}")

    deo = (
        db.query(models.DEOMaster).filter(models.DEOMaster.agent_id == agent_id).first()
    )

    if deo is None:
        logger.warning(f"DEO not found with agent ID: {agent_id}")
        raise HTTPException(
            status_code=404, detail=f"DEO not found with agent ID: {agent_id}"
        )

    logger.info(f"Successfully retrieved DEO: {agent_id}")
    return deo


# ============================================================================
# PROVISION ENDPOINTS
# ============================================================================


@app.get("/provisions/", response_model=List[Provision], tags=["Provisions"])
def get_provisions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(None, ge=1, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated list of provision records.

    Provisions represent service transactions or activations performed by
    BSK agents for customers.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return (None = all records)
        db: Database session dependency

    Returns:
        List[Provision]: List of provision records
    """
    logger.info(
        f"GET /provisions/ - Fetching provisions with skip={skip}, limit={limit}"
    )

    # Build query with offset
    query = db.query(models.Provision).offset(skip)

    # Apply limit if specified
    if limit is not None:
        query = query.limit(limit)

    provisions = query.all()
    logger.info(f"Successfully retrieved {len(provisions)} provision records")

    return provisions


@app.get("/provisions/{customer_id}", response_model=Provision, tags=["Provisions"])
def get_provision(customer_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific provision record by customer ID.

    Args:
        customer_id: The unique identifier for the customer
        db: Database session dependency

    Returns:
        Provision: The requested provision record

    Raises:
        HTTPException: 404 if provision not found
    """
    logger.info(
        f"GET /provisions/{customer_id} - Fetching provision for customer: {customer_id}"
    )

    provision = (
        db.query(models.Provision)
        .filter(models.Provision.customer_id == customer_id)
        .first()
    )

    if provision is None:
        logger.warning(f"Provision not found for customer ID: {customer_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Provision not found for customer ID: {customer_id}",
        )

    logger.info(f"Successfully retrieved provision for customer: {customer_id}")
    return provision


# ============================================================================
# AI ANALYTICS ENDPOINTS
# ============================================================================


@app.get("/underperforming_bsks/", tags=["Analytics"])
def get_underperforming_bsks(
    num_bsks: int = Query(50, ge=1, le=1000, description="Number of BSKs to return"),
    sort_order: str = Query(
        "asc", regex="^(asc|desc)$", description="Sort order: 'asc' or 'desc'"
    ),
    db: Session = Depends(get_db),
):
    """
    Identify and retrieve underperforming BSKs based on AI analytics.

    This endpoint uses machine learning algorithms to analyze BSK performance
    across multiple dimensions (provision volume, service diversity, efficiency, etc.)
    and returns a ranked list of underperforming BSKs that require attention.

    Args:
        num_bsks: Number of BSKs to return (1-1000)
        sort_order: Sort order for results - 'asc' (lowest performing first) or 'desc'
        db: Database session dependency

    Returns:
        List[dict]: Ranked list of underperforming BSKs with performance scores

    Example Response:
        [
            {
                "bsk_id": 123,
                "bsk_name": "BSK Branch Name",
                "score": 45.2,
                "metrics": {...}
            },
            ...
        ]
    """
    logger.info(
        f"GET /underperforming_bsks/ - Analyzing with num_bsks={num_bsks}, "
        f"sort_order={sort_order}"
    )

    # Fetch all master data from database
    bsks_df, provisions_df, deos_df, services_df = fetch_all_master_data(db)

    # Execute AI analytics to identify underperforming BSKs
    logger.info("Running underperformance analysis...")
    result_df = find_underperforming_bsks(bsks_df, provisions_df, deos_df, services_df)

    # Sort results by performance score
    ascending = sort_order == "asc"
    result_df = result_df.sort_values(by="score", ascending=ascending).head(num_bsks)

    logger.info(f"Analysis complete. Returning {len(result_df)} underperforming BSKs")

    # Convert DataFrame to list of dictionaries for JSON response
    return result_df.to_dict(orient="records")


@app.get("/service_training_recomendation/", tags=["Analytics"])
def service_training_recommendation(
    limit: int = Query(
        20, ge=1, le=500, description="Maximum recommendations to return"
    ),
    summary_only: bool = Query(
        False, description="Return summary instead of detailed recommendations"
    ),
    db: Session = Depends(get_db),
):
    """
    Generate AI-powered training recommendations for BSKs.

    This endpoint analyzes BSK performance data and generates personalized
    training recommendations for each BSK, identifying specific services
    where additional training would have the most impact.

    The algorithm considers:
    - Service provision volume and trends
    - Performance gaps compared to peers
    - Service complexity and importance
    - Historical training effectiveness

    Args:
        limit: Maximum number of recommendations to return (1-500)
        summary_only: If True, returns only high-level summary statistics
        db: Database session dependency

    Returns:
        Union[dict, List[dict]]: Training recommendations or summary

    Summary Response (when summary_only=True):
        {
            "total_bsks_needing_training": 150,
            "top_10_bsks": [
                {
                    "bsk_id": 123,
                    "bsk_name": "BSK Name",
                    "priority_score": 87.5,
                    "total_training_services": 5
                },
                ...
            ]
        }

    Detailed Response (when summary_only=False):
        [
            {
                "bsk_id": 123,
                "bsk_name": "BSK Name",
                "priority_score": 87.5,
                "recommended_services": [
                    {
                        "service_id": 5,
                        "service_name": "Loan Application",
                        "urgency": "high",
                        "expected_impact": "medium"
                    },
                    ...
                ],
                "total_training_services": 5
            },
            ...
        ]
    """
    logger.info(
        f"GET /service_training_recomendation/ - Generating recommendations "
        f"with limit={limit}, summary_only={summary_only}"
    )

    # Fetch all master data from database
    bsks_df, provisions_df, deos_df, services_df = fetch_all_master_data(db)

    # Generate AI-powered training recommendations
    logger.info("Generating training recommendations...")
    recommendations = training_recommendation(
        bsks_df=bsks_df,
        provisions_df=provisions_df,
        deos_df=deos_df,
        services_df=services_df,
        top_n_services=10,  # Consider top 10 services for each BSK
        min_provision_threshold=10,  # Minimum provisions to be included in analysis
    )

    logger.info(f"Generated {len(recommendations)} training recommendations")

    # Return summary if requested
    if summary_only:
        summary = {
            "total_bsks_needing_training": len(recommendations),
            "top_10_bsks": [
                {
                    "bsk_id": rec["bsk_id"],
                    "bsk_name": rec["bsk_name"],
                    "priority_score": rec["priority_score"],
                    "total_training_services": rec["total_training_services"],
                }
                for rec in recommendations[:10]
            ],
        }
        logger.info("Returning summary of recommendations")
        return summary

    # Return detailed recommendations up to limit
    logger.info(
        f"Returning {min(limit, len(recommendations))} detailed recommendations"
    )
    return recommendations[:limit]


# Replace your existing service_videos endpoints with these:

from app.models.schemas import ServiceVideo, ServiceVideoCreate, ServiceVideoUpdate


# POST endpoint - Creates NEW record or UPDATES existing
@app.post("/service_videos/", response_model=ServiceVideo, tags=["Service Videos"])
def create_or_update_service_video(
    video: ServiceVideoCreate, db: Session = Depends(get_db)
):
    """Create or update video record for a service"""

    # Check if record already exists
    existing_video = (
        db.query(models.ServiceVideo)
        .filter(models.ServiceVideo.service_id == video.service_id)
        .first()
    )

    if existing_video:
        # ✅ UPDATE existing record - increment version
        existing_video.video_version = video.video_version
        existing_video.source_type = video.source_type
        existing_video.is_new = True
        existing_video.is_done = False
        existing_video.updated_at = datetime.now()

        db.commit()
        db.refresh(existing_video)
        return existing_video
    else:
        # ✅ CREATE new record
        db_video = models.ServiceVideo(**video.dict())
        db.add(db_video)
        db.commit()
        db.refresh(db_video)
        return db_video


# GET endpoint - Get video info for a service
@app.get(
    "/service_videos/{service_id}",
    response_model=ServiceVideo,
    tags=["Service Videos"],
)
def get_service_video(service_id: int, db: Session = Depends(get_db)):
    """Get video record for a specific service"""
    video = (
        db.query(models.ServiceVideo)
        .filter(models.ServiceVideo.service_id == service_id)
        .first()
    )

    if not video:
        raise HTTPException(status_code=404, detail="No video found for this service")

    return video


# PUT endpoint - Update video record
@app.put(
    "/service_videos/{service_id}",
    response_model=ServiceVideo,
    tags=["Service Videos"],
)
def update_service_video(
    service_id: int,
    video_update: ServiceVideoUpdate,
    db: Session = Depends(get_db),
):
    """Update existing video record"""
    video = (
        db.query(models.ServiceVideo)
        .filter(models.ServiceVideo.service_id == service_id)
        .first()
    )

    if not video:
        raise HTTPException(status_code=404, detail="Video record not found")

    # Update fields
    for key, value in video_update.dict(exclude_unset=True).items():
        setattr(video, key, value)

    video.updated_at = datetime.now()
    db.commit()
    db.refresh(video)
    return video


# PATCH endpoint - Mark video as old/done
@app.patch("/service_videos/{service_id}/mark_old", tags=["Service Videos"])
def mark_video_as_old(service_id: int, db: Session = Depends(get_db)):
    """Mark video as no longer new"""
    video = (
        db.query(models.ServiceVideo)
        .filter(models.ServiceVideo.service_id == service_id)
        .first()
    )

    if not video:
        raise HTTPException(status_code=404, detail="Video record not found")

    video.is_new = False
    video.updated_at = datetime.now()
    db.commit()

    return {"status": "success", "service_id": service_id}


# DELETE old endpoint that's no longer needed
# Remove the mark_videos_as_old with exclude_version parameter
