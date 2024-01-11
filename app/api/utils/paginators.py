import math
from app.common.handlers import ErrorCode, RequestError


class Paginator(object):
    def __init__(self, page_size: int = 50) -> None:
        self.page_size = page_size

    async def paginate_queryset(self, queryset, current_page):
        if current_page < 1:
            raise RequestError(
                err_code=ErrorCode.INVALID_PAGE, err_msg="Invalid Page", status_code=404
            )
        page_size = self.page_size
        # Doing limit and offset would probably be the best way for this, but this ORM left me no choice.
        qs = await queryset.limit(1000000)
        items = qs[(current_page - 1) * page_size : current_page * page_size]
        qs_count = len(qs)

        if qs_count > 0 and not items:
            raise RequestError(
                err_code=ErrorCode.INVALID_PAGE,
                err_msg="Page number is out of range",
                status_code=400,
            )

        last_page = math.ceil(qs_count / page_size)
        return {
            "items": items,
            "per_page": page_size,
            "current_page": current_page,
            "last_page": last_page,
        }
