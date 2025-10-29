resource "aws_api_gateway_rest_api" "api" {
  name        = "PedidosREST"
  description = "API REST para criar pedidos"
}

resource "aws_api_gateway_resource" "pedidos" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "pedidos"
}

resource "aws_api_gateway_method" "post_pedidos" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.pedidos.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "post_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.pedidos.id
  http_method = aws_api_gateway_method.post_pedidos.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.criar_pedido.invoke_arn
}

resource "aws_lambda_permission" "allow_apigw_rest" {
  statement_id  = "AllowAPIGWInvokeREST"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.criar_pedido.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "deploy" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  depends_on  = [aws_api_gateway_integration.post_integration]
}

resource "aws_api_gateway_stage" "stage" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  deployment_id = aws_api_gateway_deployment.deploy.id
  stage_name    = "dev"
}
