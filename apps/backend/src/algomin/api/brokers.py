from fastapi import APIRouter
import yaml
import os

router = APIRouter()

@router.get("/brokers")
async def get_brokers():
    yaml_path = os.path.join("data", "brokers.yaml")
    try:
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
            return {"brokers": data.get("brokers", [])}
    except Exception as e:
        return {"error": f"Could not read brokers.yaml: {str(e)}"}
