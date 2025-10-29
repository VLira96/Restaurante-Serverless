resource "aws_sqs_queue" "pedidos_dlq" {
  name = "PedidosDLQ"
}

resource "aws_sqs_queue" "pedidos" {
  name = "PedidosQueue"
  visibility_timeout_seconds = 30
  message_retention_seconds  = 345600 # 4 dias
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.pedidos_dlq.arn
    maxReceiveCount     = 5
  })
}