from typing import Optional
from app.models.base.managers import BaseManager
from .tables import SiteDetail


class SiteDetailManager(BaseManager[SiteDetail]):
    pass

sitedetail_manager = SiteDetailManager(SiteDetail)