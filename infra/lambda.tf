resource "aws_lambda_function" "criar_pedido" {
  function_name = "LambdaCriarPedido"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  filename      = "${path.module}/../lambdas/criar_pedido/build/lambda.zip"
  environment {
    variables = {
      TABLE_NAME   = aws_dynamodb_table.pedidos.name
      QUEUE_URL    = aws_sqs_queue.pedidos.id
      LOCALSTACK_URL = "http://localhost:4566"
    }
  }
}

resource "aws_lambda_function" "processar_pedido" {
  function_name = "LambdaProcessarPedido"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  filename      = "${path.module}/../lambdas/processar_pedido/build/lambda.zip"
  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.pedidos.name
      BUCKET     = aws_s3_bucket.receipts.bucket
      LOCALSTACK_URL = "http://localhost:4566"
    }
  }
}

resource "aws_lambda_event_source_mapping" "sqs_to_lambda" {
  event_source_arn  = aws_sqs_queue.pedidos.arn
  function_name     = aws_lambda_function.processar_pedido.arn
  batch_size        = 1
  enabled           = true
}
