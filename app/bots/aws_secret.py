import base64
import os

import boto3
import json

from dotenv import load_dotenv
load_dotenv()

def get_secret(secret_name):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=os.getenv("AWS_REGION_NAME"))

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = json.loads(get_secret_value_response['SecretString'])
            return secret['tradelikebot-api-ecryption']  # Ensure this matches the JSON key stored in AWS Secrets Manager
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret
