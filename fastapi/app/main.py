from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError

app = FastAPI(title="AWS Explorer UI")

# Mount static and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Helper to create boto3 clients — reads AWS creds from env or uses IAM role
def aws_client(service_name, region_name=None):
    session_kwargs = {}
    # If user provided profile name
    profile = os.environ.get("AWS_PROFILE")
    if profile:
        session_kwargs["profile_name"] = profile
    session = boto3.Session(**session_kwargs) if session_kwargs else boto3.Session()
    return session.client(service_name, region_name=region_name) if region_name else session.client(service_name)

@app.get("/", response_class=None)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/buckets")
async def list_buckets():
    try:
        s3 = aws_client("s3")
        resp = s3.list_buckets()
        buckets = [{"Name": b.get("Name"), "CreationDate": b.get("CreationDate", "")} for b in resp.get("Buckets", [])]
        return JSONResponse({"ok": True, "buckets": buckets})
    except (BotoCoreError, ClientError) as e:
        return JSONResponse({"ok": False, "error": str(e)})

@app.get("/api/ec2")
async def list_ec2(region: str = "us-east-1"):
    try:
        ec2 = aws_client("ec2", region_name=region)
        resp = ec2.describe_instances()
        instances = []
        for res in resp.get("Reservations", []):
            for inst in res.get("Instances", []):
                instances.append({
                    "InstanceId": inst.get("InstanceId"),
                    "State": inst.get("State", {}).get("Name"),
                    "InstanceType": inst.get("InstanceType"),
                    "PublicIpAddress": inst.get("PublicIpAddress"),
                    "PrivateIpAddress": inst.get("PrivateIpAddress"),
                    "LaunchTime": str(inst.get("LaunchTime")),
                })
        return JSONResponse({"ok": True, "instances": instances})
    except (BotoCoreError, ClientError) as e:
        return JSONResponse({"ok": False, "error": str(e)})