#!/usr/bin/env python3

# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/
#
# Original code snippet from AWS reviewed and modified for current application.

import boto3
from botocore.exceptions import ClientError


def get_secret(username, aws_access_key_id, aws_secret_access_key):

    secret_name = "sensorfabric/fitbitcompliance/{}".format(username)
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        return None

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']

    return secret
