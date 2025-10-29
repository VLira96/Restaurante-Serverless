import os, json, uuid, logging
from datetime import datetime, timezone
import boto3
from jsonschema import validate, ValidationError

TABLE_NAME   = os.environ["TABLE_NAME"]
QUEUE_URL    = os.environ["QUEUE_URL"]
AWS_ENDPOINT = os.getenv("LOCALSTACK_URL", "http://localhost:4566")

ddb = boto3.resource("dynamodb", endpoint_url=AWS_ENDPOINT)
sqs = boto3.client("sqs", endpoint_url=AWS_ENDPOINT)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

PEDIDO_SCHEMA = {
    "type": "object",
    "required": ["cliente", "itens", "mesa"],
    "properties": {
        "cliente": {"type": "string"},
        "itens": {"type": "array", "minItems": 1},
        "mesa": {"type": "integer"},
        "observacoes": {"type": "string"}
    }
}

def parse_event_body(event):
    body = event.get("body")
    if isinstance(body, str):
        return json.loads(body or "{}")
    return body or {}

def response(status, body):
    return {"statusCode": status, "headers": {"content-type": "application/json"}, "body": json.dumps(body)}

def lambda_handler(event, context):
    try:
        payload = parse_event_body(event)
        validate(instance=payload, schema=PEDIDO_SCHEMA)

        order_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        item = {
            "id": order_id,
            "cliente": payload["cliente"],
            "itens": payload["itens"],
            "mesa": payload["mesa"],
            "status": "RECEBIDO",
            "createdAt": now
        }

        ddb.Table(TABLE_NAME).put_item(Item=item)
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps({"id": order_id}))

        logger.info(f"Pedido criado: {order_id}")
        return response(201, {"id": order_id, "status": "RECEBIDO"})

    except ValidationError as e:
        return response(400, {"error": "Payload inválido", "details": e.message})
    except Exception as e:
        logger.exception("Erro interno")
        return response(500, {"error": str(e)})
