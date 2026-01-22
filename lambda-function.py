import os
import json
import urllib.request
import urllib.error

VAULT_ADDR = os.environ["VAULT_ADDR"]
VAULT_TOKEN = os.environ["VAULT_TOKEN"]
SECRET_PATH = "secret/data/openai"

def lambda_handler(event, context):
    try:
        req = urllib.request.Request(
            f"{VAULT_ADDR}/v1/{SECRET_PATH}",
            headers={
                "X-Vault-Token": VAULT_TOKEN
            }
        )

        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())

        api_key = data["data"]["data"]["api_key"]

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Secret fetched successfully",
                "key_length": len(api_key)
            })
        }

    except urllib.error.HTTPError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": f"Vault HTTP error: {e.code}"
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }
