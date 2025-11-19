import json
import os
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Use region from environment or default to us-east-1
BEDROCK_REGION = os.environ.get("AWS_REGION", "us-east-1")

bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

# Claude 3.7 Sonnet model on Bedrock
INFERENCE_PROFILE_ARN = os.environ.get(
    "BEDROCK_INFERENCE_PROFILE_ARN",
    "arn:aws:bedrock:us-east-1:247323793332:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0"
)

def call_bedrock_claude(image_base64: str, media_type: str = "image/png") -> dict:
    """
    Send a multimodal (image + text) prompt to Claude via Bedrock
    and return parsed JSON with place, date, and payment.
    """
    prompt = (
        "You are an invoice extraction engine.\n\n"
        "You will receive an image of a single invoice.\n"
        "Extract the following fields from the invoice:\n"
        "1. place  - the business/vendor name or location of the invoice.\n"
        "2. date   - the invoice issue date in ISO format YYYY-MM-DD if possible.\n"
        "3. payment - the total amount due/paid as a number (no currency symbol).\n"
        "4. currency - the currency code if visible (e.g., USD, EUR, ILS), otherwise null.\n\n"
        "Return ONLY a valid JSON object with this exact structure:\n"
        "{\n"
        '  "place": "<string or null>",\n'
        '  "date": "<YYYY-MM-DD or null>",\n'
        '  "payment": <number or null>,\n'
        '  "currency": "<3-letter code or null>"\n'
        "}\n"
        "Do not include any explanation or text outside the JSON."
    )

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ],
        # Optional: you can tweak these
        "temperature": 0.2,
        "top_p": 0.9,
    }

    response = bedrock.invoke_model(
        modelId=INFERENCE_PROFILE_ARN,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )

    response_body = json.loads(response["body"].read())
    # Claude messages API returns text in content[0].text  [oai_citation:1‡hidekazu-konishi.com](https://hidekazu-konishi.com/entry/amazon_bedrock_claude_3-5_sonnet_vision_automate_titan_image_gen.html)
    raw_text = response_body["content"][0]["text"].strip()

    try:
        extracted = json.loads(raw_text)
    except json.JSONDecodeError:
        logger.error("Claude did not return valid JSON: %s", raw_text)
        # Fallback structure
        extracted = {
            "place": None,
            "date": None,
            "payment": None,
            "currency": None,
            "raw_response": raw_text,
        }

    return extracted


def lambda_handler(event, context):
    """
    Lambda handler for a Lambda Function URL.

    Expected request:
      POST /  with JSON body:
      {
        "image_base64": "<base64-encoded-invoice-image>",
        "media_type": "image/png"  // optional, default image/png
      }
    """

    logger.info("Received event2: %s", json.dumps(event))
    print("Received event3: %s", json.dumps(event))

    # Handle preflight CORS
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": "",
        }

     # 1. Get the raw body string
    body_str = event.get("body") or ""

    # 2. If isBase64Encoded=False, body_str is plain JSON string → parse it
    try:
        body = json.loads(body_str)
    except Exception as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON body", "details": str(e)}),
        }

    # 3. Now you can safely pull image_base64 and media_type
    image_base64 = body.get("image_base64")
    media_type = body.get("media_type", "image/png")

    logger.info("image_base64_raw (first 50 chars): %s", str(image_base64)[:50])
    logger.info("media_type: %s", media_type)


    if not image_base64:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json",
            },
            "body": json.dumps(
                {"error": "Missing required field 'image_base64' in request body"}
            ),
        }

    try:
        extracted = call_bedrock_claude(image_base64, media_type)
    except Exception as e:
        logger.exception("Error while calling Bedrock")
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": "Bedrock invocation failed", "details": str(e)}),
        }

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
        "body": json.dumps(extracted),
    }
