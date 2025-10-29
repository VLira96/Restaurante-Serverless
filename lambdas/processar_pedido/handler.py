import os, io, json, logging
from datetime import datetime, timezone
import boto3
from botocore.exceptions import ClientError

TABLE_NAME   = os.environ["TABLE_NAME"]
BUCKET       = os.environ["BUCKET"]
AWS_ENDPOINT = os.getenv("LOCALSTACK_URL", "http://localhost:4566")

ddb = boto3.resource("dynamodb", endpoint_url=AWS_ENDPOINT)
s3  = boto3.client("s3", endpoint_url=AWS_ENDPOINT)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def gerar_pdf_simples(pedido):
    text = f"""
    Comprovante do Pedido #{pedido['id']}
    Cliente: {pedido['cliente']}
    Mesa: {pedido['mesa']}
    Itens: {pedido['itens']}
    Status: {pedido['status']}
    Gerado em: {datetime.now(timezone.utc).isoformat()}
    """
    # Gera bytes de texto para simular PDF
    pdf_bytes = f"%PDF-1.1\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R/Contents 4 0 R>>endobj\n4 0 obj<</Length {len(text)}>>stream\n{text}\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \ntrailer<</Size 5/Root 1 0 R>>\nstartxref\n0\n%%EOF".encode("latin-1")
    return pdf_bytes

def objeto_existe(bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        return False

def lambda_handler(event, context):
    for record in event.get("Records", []):
        msg = json.loads(record["body"])
        id_ = msg["id"]

        table = ddb.Table(TABLE_NAME)
        pedido = table.get_item(Key={"id": id_}).get("Item")
        if not pedido:
            logger.warning(f"Pedido {id_} não encontrado.")
            raise Exception("Pedido não encontrado")

        key = f"receipts/{id_}.pdf"
        if not objeto_existe(BUCKET, key):
            pdf = gerar_pdf_simples(pedido)
            s3.put_object(Bucket=BUCKET, Key=key, Body=pdf, ContentType="application/pdf")
            logger.info(f"PDF salvo em {key}")

        table.update_item(
            Key={"id": id_},
            UpdateExpression="set #s = :s",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":s": "COMPROVANTE_GERADO"}
        )

    return {"ok": True}
