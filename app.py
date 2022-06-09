from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import numpy as np
from flask import Flask, request, make_response
import json
import pandas as pd
import pickle
from flask_cors import cross_origin
import logging
import os
from flask import session, redirect, url_for, flash, g
from flask_session import Session
import os
import redis
app = Flask(__name__)
# app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_REDIS'] = redis.from_url('redis://127.0.0.1:6379')
# # Configure session to use filesystem
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# app.config['top_company_changed']=False
#Session(app)
logging.basicConfig(level=logging.INFO)
companies={'twitter','infosys limited','amex','citi','goldman sachs','deloitte','jpmorgan','capgemini','mu sigma','fractal','tiger analytics','exl','walmart','microsoft','google','amazon','ibm','pwc','infosys','tata consultancy services','hsbc','standard chartered','accenture','ey','kpmg'}
top_companies=set()
# session['top_company_changed']=False
model = pickle.load(open('rf.pkl', 'rb'))
z=True
df=pd.DataFrame() 
@app.route('/')
def upload_file():
  # global z
  # z=False
  # return "ok boss"+str(z)
  return render_template('upload.html')
# @app.route('/sog')
# def fog():
#   global z
#   z=True
#   return str(z)
# @app.route('/dog')
# def cat():
#   return str(z)
# @app.route('/', methods = ['GET', 'POST'])
# def upload_files():
#     global df
#     if request.method == 'POST':
#       f = request.files['file']
#       f.save(secure_filename(f.filename))
#       df=pd.read_csv(f.filename)

#       return 'file uploaded successfully'
@app.route("/", methods=['GET', 'POST'])
def streambyte():
    global df
    global top_companies
    global top_company_changed
    global z
    # your file processing code is here...
    f = request.files['file']
    your_script_result = 'File Uploaded!'
    df=pd.read_csv(f.filename)
    top_company_changed=True
    top_companies=df['0']
    z=False
    print(top_companies)
    # your file processing code is here...
    return render_template('upload.html', file_path = f, result = your_script_result)            
# @app.route('/')
# def hello():
#     global z
#     if z:
#         z=False
#         return "ok"+str(df.shape)
#         #return df.shape()    
#     else:
#         z=True
#         return "sure bro{}".format(z)


# geting and sending response to dialogflow
@app.route('/webhook', methods=['GET','POST'])                                                #GET
@cross_origin()
def webhook():
    global top_company_changed
    global top_companies
    global z
    req = request.get_json(silent=True, force=True)
    #print("Request:")
    #print(json.dumps(req, indent=4))
    res= processRequest(req)
    res = json.dumps(res, indent=4)
    #print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


# processing the request from dialogflow
def processRequest(req):
    global top_company_changed
    global top_companies
    global z
    #sessionID=req.get('responseId')
    result = req.get("queryResult")
    #user_says=result.get("queryText")
    #log.write_log(sessionID, "User Says: "+user_says)
    parameters = result.get("parameters")
    Petal_length=parameters.get("number")
    Petal_width = parameters.get("number1")
    Sepal_length=parameters.get("number2")
    Sepal_width=parameters.get("number3")
    int_features = [Petal_length,Petal_width,Sepal_length,Sepal_width]
    
    final_features = [np.array(int_features)]
     
    intent = result.get("intent").get('displayName')
    
    if (intent=='IrisData'):
        prediction = model.predict(final_features)
    
        output = round(prediction[0], 2)
    
        
        if(output==0):
            flowr = 'Setosa'
    
        if(output==1):
            flowr = 'Versicolour'
        
        if(output==2):
            flowr = 'Virginica'
       
        fulfillmentText= "The Iris type seems to be..  {} !".format(flowr)
        #log.write_log(sessionID, "Bot Says: "+fulfillmentText)
        return {
            "fulfillmentText": fulfillmentText
        }
    elif (intent=="SeeOurTopCompanyList"):
        if top_company_changed:
            return {
            "fulfillmentText":"{}+{}".format(top_companies,z),
             "fulfillmentMessages": [
      {
        "platform": "ACTIONS_ON_GOOGLE",
        "simpleResponses": {
          "simpleResponses": [
            {
              "textToSpeech":"{}+{}".format(top_companies,z)
            }
          ]
        }
      },
      {
      "platform": "ACTIONS_ON_GOOGLE",
        "suggestions": {
          "suggestions": [
            {
              "title": "ok"
            }
          ]
        }
      },
      {
        "text": {
          "text": [
          "{}+{}".format(top_companies,z)
            
            ]
        }
      }
    ]}
        else:
            return {
            "fulfillmentText":"{}+{}".format(companies,z),
             "fulfillmentMessages": [
      {
        "platform": "ACTIONS_ON_GOOGLE",
        "simpleResponses": {
          "simpleResponses": [
            {
              "textToSpeech":"{}+{}".format(companies,z)
            }
          ]
        }
      },
      {
      "platform": "ACTIONS_ON_GOOGLE",
        "suggestions": {
          "suggestions": [
            {
              "title": "ok"
            }
          ]
        }
      },
      {
        "text": {
          "text": [
          "{}+{}".format(companies,z)
            
            ]
        }
      }
    ]}
    elif(intent=="NoNeedOfTopCompanies"):
        top_company_changed=True
        #top_companies={}
        z=False
    elif(intent=="TimeToLeave"):
        z=True
        top_company_changed=False   
        return 
        {
        "fulfillmentText":"bye"
        } 
    elif (intent=="AddOwnCompanies"):
          z=False
          # sesssion['top_company_changed']=True
          # top_companies=df['0'].values()
 
    else:
          return {
            "fulfillmentText":"nope something is wrong  {}".format(intent)
        }
        #log.write_log(sessionID, "Bot Says: " + result.fulfillmentText)

if __name__ == '__main__':
    # z=True
    # top_companies=set()
    # top_company_changed=False
    # z=True
    app.run(debug=True)
#if __name__ == '__main__':
#    port = int(os.getenv('PORT', 5000))
#    print("Starting app on port %d" % port)
#    app.run(debug=False, port=port, host='0.0.0.0')