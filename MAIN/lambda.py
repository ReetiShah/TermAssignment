import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')

def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            print(new_image)
            email = new_image['email']['S']
            print(email)
            
    # Create an SNS client
    sns = boto3.client('sns')

    # Set up the email message
    subject = 'New Account Created'
    message = f'An account was created with the email address {email}.'


    response = sns.subscribe(
        TopicArn='arn:aws:sns:us-east-1:239052681284:email_noti',
        Protocol='email',
        Endpoint=email
    )
    
    # Publish the message to the SNS topic
    response = sns.publish(
        TopicArn='arn:aws:sns:us-east-1:239052681284:email_noti',
        Subject=subject,
        Message=message
    )

    # Print the response for logging purposes
    print(response)

  
