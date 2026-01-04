"""API dependencies for authentication and authorization."""

from fastapi import Header, HTTPException, status
from app.config import settings


async def verify_api_key(x_api_key: str = Header(None)) -> str:
    """
    Verify API key for protected endpoints.
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Returns:
        The validated API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not settings.API_KEY:
        # If no API key is configured, allow access (development mode)
        return ""
    
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return x_api_key


def require_feature(feature_name: str):
    """
    Dependency factory to check if a feature flag is enabled.
    
    Args:
        feature_name: Name of the feature flag to check
        
    Returns:
        A dependency function that raises HTTPException if feature is disabled
    """
    def check_feature():
        feature_enabled = getattr(settings, feature_name, False)
        if not feature_enabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature_name}' is not enabled. Set {feature_name}=true in configuration."
            )
    return check_feature
