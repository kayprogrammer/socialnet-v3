from fastapi import APIRouter
from app.api.schemas.general import (
    SiteDetailResponseSchema,
)
from app.models.general.tables import SiteDetail

router = APIRouter()


@router.get(
    "/site-detail",
    summary="Retrieve site details",
    description="This endpoint retrieves few details of the site/application",
)
async def retrieve_site_details() -> SiteDetailResponseSchema:
    sitedetail = await SiteDetail.objects().first()
    if not sitedetail:
        sitedetail = await SiteDetail.objects().create()
    return {"message": "Site Details fetched", "data": sitedetail}
