"""Response utilities."""
from typing import Any, Dict, List, Optional


def success_response(
    data: Any = None,
    message: str = "Success",
) -> Dict[str, Any]:
    """Create success response."""
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(
    message: str = "Error",
    errors: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create error response."""
    return {
        "success": False,
        "message": message,
        "errors": errors or [],
    }


def paginated_response(
    items: List[Any],
    total: int,
    page: int,
    per_page: int,
) -> Dict[str, Any]:
    """Create paginated response."""
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "success": True,
        "data": items,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
        },
    }
