#Followed the following tutorials while building this app
#https://www.youtube.com/watch?v=NR9QkgsEjck
#https://www.youtube.com/watch?v=7RcqfuKBnfM
#https://www.youtube.com/watch?v=dam0GPOAvVI

from flask import Flask, redirect, render_template, request, url_for, session
import key_config as keys
import boto3 
import secrets
import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

dynamodb = boto3.client('dynamodb',
                    aws_access_key_id=keys.ACCESS_KEY_ID,
                    aws_secret_access_key=keys.ACCESS_SECRET_KEY,
                    aws_session_token=keys.AWS_SESSION_TOKEN,
                    region_name=keys.REGION)

secretsManagerClient = boto3.client('secretsmanager',
                    aws_access_key_id=keys.ACCESS_KEY_ID,
                    aws_secret_access_key=keys.ACCESS_SECRET_KEY,
                    aws_session_token=keys.AWS_SESSION_TOKEN,
                    region_name=keys.REGION)

from boto3.dynamodb.conditions import Key, Attr

@app.route('/')
def index():
    if 'userData' in session:
        return redirect(url_for('home'))
    return redirect(url_for('check'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstName = request.form['firstName']
        email = request.form['email']
        password = request.form['password']
        
        table = 'users'

        user = {
            'firstName': {'S': firstName},
            'email': {'S': email},
            'password': {'S': password},
        }

        response = dynamodb.put_item(
             TableName=table,
            Item=user
        )
        msg = "Registration Complete. Please Login to your account !"
    
        return render_template('login.html',msg = msg)
    return render_template('sign_up.html')


@app.route('/login', methods=['GET', 'POST'])
def check():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']

        table_name = 'users'
        key = {
            'email': {'S': email}
        }
        response = dynamodb.get_item(TableName=table_name, Key=key)
        items = response['Item']
        print(items)
        if password == items['password']['S']:
            passwordReceived = items['password']['S']
            email = items['email']['S']
            firstName = items['firstName']['S']
            dataReceived = {
                'firstName' : firstName,
                'email' : email,
                'passwordReceived' : passwordReceived
            }
            session['UserData'] = dataReceived
            return redirect(url_for('home'))
            # return render_template("home.html", userData = dataReceived)
    return render_template("login.html")


@app.route('/home', methods=['GET', 'POST'])
def home():
    userData = session.get('UserData')

    if request.method == 'POST':
        note = request.form['note']
        table2 = 'notes'

        noteData = {
            'id' : {'S': datetime.datetime.now().strftime('%Y%m%d%H%M%S') },
            'firstName': {'S': userData['firstName']},
            'email': {'S': userData['email']},
            'notes': {'S': note},
        }

        response = dynamodb.put_item(
             TableName=table2,
            Item=noteData
        )
        return redirect(url_for('home'))
        # return render_template('home.html', userData= userData)

    if request.method == 'GET':

        non_partition_key = 'email'
        non_partition_key_value = userData['email']
        table_name = 'notes'
        key = {
            'email': {'S': userData['email']}
        }

        response = dynamodb.scan(
            TableName=table_name,
            FilterExpression=f'{non_partition_key} = :val',
            ExpressionAttributeValues={
                ':val': {'S': non_partition_key_value}
            }
        )
        # response = dynamodb.get_item(TableName=table_name, Key=key)
        items = response['Items']
        print(response)
        return render_template('home.html', userData= userData, items = items)
    

@app.route('/notes', methods=['GET'])
def notes():
    if request.method == 'GET':

        response = secretsManagerClient.get_secret_value(
            SecretId = 'notes'
        )
        secret = response['SecretString']
        return render_template('home.html')
    
@app.route('/logout')
def logout():
    # Clear session data
    session.clear()

    # Redirect to the home page or any other page after logout
    return redirect(url_for('check'))
        
if __name__ == "__main__":
    
    app.run(debug=True)