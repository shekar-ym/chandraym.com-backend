import boto3
import pytest
import os
import json
from contextlib import contextmanager
from moto import mock_dynamodb2
from visitors_counter import app
from unittest import mock

TABLE = "visitors"


@contextmanager
def do_test_setup():
    with mock_dynamodb2():
        set_up_dynamodb()
        yield


def set_up_dynamodb():
    client = boto3.client('dynamodb', region_name='ap-southeast-2')
    client.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },
        ],
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        TableName=TABLE,
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )


@mock.patch.dict(os.environ, {"databaseName": TABLE})
def test_handler():
    with do_test_setup():
        # Run call with an event describing the file:
        response = app.lambda_handler(None, None)

        # Check that it exists in `processed/`
        assert response['statusCode'] == 200
        assert response['body'] == json.dumps({"visitorCount": 1})

        response = app.lambda_handler(None, None)

        assert response['statusCode'] == 200
        assert response['body'] == json.dumps({"visitorCount": 2})
