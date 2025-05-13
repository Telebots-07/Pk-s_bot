import os
import requests
from utils.logger import log_error

def redeploy():
    """Trigger redeployment on Render."""
    try:
        render_api_token = os.getenv("RENDER_API_TOKEN")
        service_id = os.getenv("RENDER_SERVICE_ID")
        headers = {"Authorization": f"Bearer {render_api_token}"}
        response = requests.post(
            f"https://api.render.com/v1/services/{service_id}/deploys",
            headers=headers
        )
        response.raise_for_status()
        print("Redeployment triggered!")
    except Exception as e:
        log_error(f"Redeploy error: {str(e)}")

if __name__ == "__main__":
    redeploy()
