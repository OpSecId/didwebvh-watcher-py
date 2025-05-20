"""WebVH Log endpoints."""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse

from app.plugins import AskarStorage, WebVhProcessor
from app.models.records import DidLogRecord, DidWitnessRecord

router = APIRouter(tags=["Dids"])
askar = AskarStorage()
webvh = WebVhProcessor()


@router.post("/log")
async def update_cached_scid(did: str):
    """Update cached log/witness file."""

    if not await webvh.resolve(did):
        raise HTTPException(status_code=422, detail="Unresolveable DID.")

    scid = did.split(":")[2]
    log_record = await askar.fetch("logRecord", scid)

    if not log_record:
        raise HTTPException(status_code=404, detail="Unknown scid value.")

    log_record = DidLogRecord(
        scid=scid, log_history=webvh.get_log_file(did)
    ).model_dump()
    await askar.update("logRecord", scid, log_record)

    witness_record = DidWitnessRecord(
        scid=scid, witness_file=webvh.get_witness_file(did)
    ).model_dump()
    await askar.update("witnessRecord", scid, witness_record)

    return JSONResponse(status_code=202, content={})


@router.get("/log")
async def return_cached_log_file(scid: str):
    """Get cached log file."""
    
    # askar = AskarStorage(scid)
    log_record = await askar.fetch("logRecord", scid)
    if not log_record:
        raise HTTPException(status_code=404, detail="Unknown scid value.")

    return Response(log_record.get("log_history"), media_type="text/jsonl")


@router.get("/witness")
async def return_cached_witness_file(scid: str):
    """Get cached witness file."""

    log_record = await askar.fetch("logRecord", scid)
    if not log_record:
        raise HTTPException(status_code=404, detail="Unknown scid value.")

    witness_record = await askar.fetch("witnessRecord", scid)

    return JSONResponse(status_code=200, content=witness_record.get("witness_file"))
