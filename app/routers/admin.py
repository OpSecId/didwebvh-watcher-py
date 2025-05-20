"""Admin endpoints."""

from fastapi import APIRouter, HTTPException, Security, status
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from app.plugins import AskarStorage, WebVhProcessor
from app.models.records import DidLogRecord, DidWitnessRecord
from config import settings

router = APIRouter(tags=["Admin"])
askar = AskarStorage()
webvh = WebVhProcessor()

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def get_api_key(
    api_key_header: str = Security(api_key_header),
) -> str:
    if api_key_header == settings.SECRET_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )


@router.post("/scid")
async def register_scid(did: str, api_key: str = Security(get_api_key)):
    """Register new scid to watch."""

    if not await webvh.resolve(did):
        return JSONResponse(status_code=404, content={})

    scid = did.split(":")[2]
    # askar = AskarStorage(scid)
    # await askar.provision()

    log_record = DidLogRecord(
        scid=scid, log_history=webvh.get_log_file(did)
    ).model_dump()
    await askar.store("logRecord", scid, log_record, {"scid": scid})

    witness_record = DidWitnessRecord(
        scid=scid, witness_file=webvh.get_witness_file(did)
    ).model_dump()
    await askar.store("witnessRecord", scid, witness_record, {"scid": scid})

    return JSONResponse(status_code=202, content={})


@router.delete("/log")
async def delete_scid(scid: str, api_key: str = Security(get_api_key)):
    """Remove scid from watchlist and remove all associated resources."""
    
    askar = AskarStorage(scid)

    await askar.remove("logRecord", scid)
    await askar.remove("witnessRecord", scid)
    # TODO, remove all resources

    return JSONResponse(status_code=202, content={})


@router.post("/resource/delete")
async def delete_cached_resource(
    scid: str, resourcePath: str, api_key: str = Security(get_api_key)
):
    """Remove cached resource."""
    
    askar = AskarStorage(scid)

    resource_id = f"{scid}{resourcePath}"
    await askar.remove("resourceRecord", resource_id)

    return JSONResponse(status_code=202, content={})
