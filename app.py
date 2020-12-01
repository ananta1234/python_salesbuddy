from flask import Flask, make_response, render_template, request
from functools import wraps

import firebase_admin
from firebase_admin import credentials, auth
import pyrebase
import json

from lead_generation import getResults
import pandas as pd

#App configuration
app = Flask(__name__)
app.config["DEBUG"] = True

#Connect to Firebase
cred = credentials.Certificate('fbAdminConfig.json')
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('fbconfig.json')))
db = pb.database()
auth = pb.auth()

#Get user
def getUser():
    try:
        user = auth.current_user
    except Exception as e:
        print(e)
        user = None
    return user

#Get token
def getToken(user):
    try:
        token = user['idToken']
    except Exception as e:
        print(e)
        token = None
    return token

@app.route('/', methods=["GET", "POST"])
def index():

  if request.method == "POST":

    if request.form['form-name'] == 'auth_form':
        email = request.form['email']
        password = request.form['password']

        if request.form['action'] == 'Login':
            #Sample account: "anantsagra@gmail.com", "samarth16"
            if email=="" or password=="":
                return {'message': 'Error missing email or password'},400

            try:
                user = auth.sign_in_with_email_and_password(email, password)
                token = user['idToken']
            except Exception as e:
                return {'message': 'Error logging user in'},400


        if request.form['action'] == 'Sign Up':
            if email=="" or password=="":
                return {'message': 'Error missing email or password'},400
            try:
                user = auth.create_user_with_email_and_password(email, password)
                token = user['idToken']
                print("Sign Up")
            except Exception as e:
                return {'message': 'Error signing user up'},400

        if request.form['action'] == 'Log Out':
            try:
                auth.current_user = None
                return {'message': 'Successfully signed out!'}
            except Exception as e:
                print(e)
                return {'message': 'Error signing out'},400



    if request.form['form-name'] == 'create_form':

        user = getUser()
        token = getToken(user)
        
        #Make sure the user is authenticated
        if token is None:
            return {'message': 'User has not successfully signed in'}

        #Get the query input
        company = request.form['company']
        keyword = request.form['keyword']

        try:
            ans = getResults(company, keyword)

            for row in ans:
                company = row[0]
                keyword = row[1]

                uid = user["localId"]


                first = row[2]
                last = row[3]
                email = row[4]

                link = row[9]

                created = row[-1]

                new_query = {"uid": uid, "company": company, "keyword": keyword, "first":first, "last": last, "email":email, "linkedin_url": link}

                db.child("queries").push(new_query, token)

            df = pd.DataFrame(ans, columns=["Company", "Keyword", "First", "Last", "Email", "Status", "Title", "Seniority", "Department", "LinkedIn Url", "Phone", "Pattern", "Time Created"])
            leads_csv = df.to_csv()
            response = make_response(leads_csv)
            response.headers["Content-Disposition"] = "attachment; filename=leads.csv"
            return response
        except Exception as e:
            print(e)
            return {'message': 'Error generating leads'}

  #Display entries currently in database
  user = getUser()
  tup_output = []

  try:
    past_queries = db.child("queries").get().val().values()

    for query in past_queries:
        uid = query["uid"]
        co = query["company"]
        key = query["keyword"]

        if user['localId']==uid:
            tup_output.append(tuple([co, key]))

    tup_output = list(set(tup_output))


  except Exception as e:
    print(e)
    past_queries = None

  return render_template('index.html', queries=tup_output)