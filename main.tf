resource "aws_s3_bucket" "files-bucket" {
  bucket = "files-data"
}

resource "aws_s3_bucket" "make-datalake" {
  bucket = "datalake"
}

resource "aws_s3_bucket" "make-lambda-code" {
  bucket = "lambda-code"
}



data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_s3_object" "object" {
  bucket = "lambda-code"
  key    = "lambdas.zip"
  source = "lambdas/lambdas.zip"

  # The filemd5() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the md5() function and the file() function:
  # etag = "${md5(file("path/to/file"))}"
  etag = filemd5("lambdas/lambdas.zip")
}

data "aws_s3_object" "lambda" {
  bucket = "lambda-code"
  key    = "lambdas.zip"

  depends_on = [aws_s3_object.object]
}

resource "aws_lambda_function" "test_lambda" {
  # If the file is not in the current working directory you will need to include a
  # path.module in the filename.
  s3_bucket         = data.aws_s3_object.lambda.bucket
  s3_key            = data.aws_s3_object.lambda.key
  s3_object_version = data.aws_s3_object.lambda.version_id
  function_name     = "read_s3"
  role              = aws_iam_role.iam_for_lambda.arn # (not shown)
  handler           = "read_s3.main"
  depends_on = [aws_iam_role.iam_for_lambda]

  runtime = "python3.10"
}