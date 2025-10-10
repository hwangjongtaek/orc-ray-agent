"""
Plugin management API endpoints for Plugin Registry service
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.plugin import Plugin as PluginModel
from app.schemas.plugin import Plugin, PluginCreate, PluginList, PluginUpdate

router = APIRouter()


@router.post("", response_model=Plugin, status_code=status.HTTP_201_CREATED)
async def create_plugin(
    plugin_in: PluginCreate,
    db: Session = Depends(get_db),
):
    """
    Create new plugin.

    Register a new plugin in the registry.
    """
    # Check if plugin with this name already exists
    existing = db.query(PluginModel).filter(PluginModel.name == plugin_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plugin with this name already exists",
        )

    # Create plugin
    db_plugin = PluginModel(
        name=plugin_in.name,
        version=plugin_in.version,
        description=plugin_in.description,
        docker_image_url=plugin_in.docker_image_url,
        input_schema=plugin_in.input_schema,
        output_schema=plugin_in.output_schema,
    )
    db.add(db_plugin)
    db.commit()
    db.refresh(db_plugin)

    return db_plugin


@router.get("", response_model=PluginList)
async def list_plugins(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List plugins.

    Retrieve paginated list of all registered plugins.
    """
    query = db.query(PluginModel)

    # Filter by name if provided
    if name:
        query = query.filter(PluginModel.name.contains(name))

    # Get total count
    total = query.count()

    # Get paginated plugins
    plugins = (
        query.order_by(PluginModel.created_at.desc()).offset(skip).limit(limit).all()
    )

    return {
        "total": total,
        "items": plugins,
    }


@router.get("/{name}", response_model=Plugin)
async def get_plugin(
    name: str,
    db: Session = Depends(get_db),
):
    """
    Get plugin by name.

    Retrieve detailed information about a specific plugin.
    """
    plugin = db.query(PluginModel).filter(PluginModel.name == name).first()

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found",
        )

    return plugin


@router.put("/{name}", response_model=Plugin)
async def update_plugin(
    name: str,
    plugin_in: PluginUpdate,
    db: Session = Depends(get_db),
):
    """
    Update plugin.

    Update plugin information by name.
    """
    plugin = db.query(PluginModel).filter(PluginModel.name == name).first()

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found",
        )

    # Update fields
    update_data = plugin_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plugin, field, value)

    db.commit()
    db.refresh(plugin)

    return plugin


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plugin(
    name: str,
    db: Session = Depends(get_db),
):
    """
    Delete plugin.

    Remove a plugin from the registry.
    """
    plugin = db.query(PluginModel).filter(PluginModel.name == name).first()

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found",
        )

    db.delete(plugin)
    db.commit()

    return None
