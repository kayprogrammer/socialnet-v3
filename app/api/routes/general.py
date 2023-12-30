from fastapi import APIRouter
from app.api.schemas.general import (
    SiteDetailResponseSchema,
)
from app.models.general.managers import sitedetail_manager

router = APIRouter()


@router.get(
    "/site-detail",
    summary="Retrieve site details",
    description="This endpoint retrieves few details of the site/application",
)
async def retrieve_site_details() -> SiteDetailResponseSchema:
    sitedetail, created = await sitedetail_manager.get_or_create()
    return {"message": "Site Details fetched", "data": sitedetail}
