import json
import boto3
import uuid
# import requests

dynamodb = boto3.client('dynamodb')
print(dynamodb)
print('loaded dynamodb')

def lambda_handler(event, context):
  # TODO implement
  if 'body' not in event:
    return {
      'statusCode': 500,
      'headers': {"content-type": "text/json"},
      'body': json.dumps({
        'error': 'missing parameters'
      })
    }

  body = json.loads(event['body'])
  if 'weight' not in body and 'device' not in body:
    return {
      'statusCode': 500,
      'headers': {"content-type": "text/json"},
      'body': json.dumps({
        'error': 'missing weight|device'
      })
    }

  item_data = {
    'id': {'S': str(uuid.uuid4())},
    'device': {'S': f'{body["device"]}'},
    'weight': {'N': f'{float(body["weight"])}'}
  }
  r = dynamodb.put_item(TableName='weights', Item=item_data)
  print(r)
  return {
    'statusCode': 200,
    'headers': {"content-type": "text/json"},
    'body': json.dumps({
      'message': 'succesfully saved weight',
      'weight': body['weight'],
      'device': body['device'],
    })
  }

