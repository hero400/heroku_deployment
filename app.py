from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import numpy as np
from flask import Flask, request, make_response,redirect,url_for
import json
import pandas as pd
import pickle
from flask_cors import cross_origin
import logging
import os
import requests
import docx2txt
import boto3,botocore
import io
import docx
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
top_company_changed=False
# session['top_company_changed']=False
model = pickle.load(open('rf.pkl', 'rb'))
z=True
# app.config['S3_BUCKET'] = "storage-bucket-for-resume"
# app.config['S3_KEY'] = "AKIATY6DFONKGVKGUJS2"
# app.config['S3_SECRET'] = "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"
# app.config['S3_LOCATION'] = 'http://{}.s3.amazonaws.com/'.format(app.config['S3_BUCKET'])
#print(app.config['S3_BUCKET'])
# s3 = boto3.client(
#    "s3",
#    aws_access_key_id=app.config['S3_KEY'],
#    aws_secret_access_key=app.config['S3_SECRET']
# )
# @app.route('/')
# def upload_file():
#   # global z
#   # z=False
#   # return "ok boss"+str(z)
#   return render_template('upload.html')
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
def watch():
  print("ok bro")
  return url_for('giff')
@app.route("/")
def account():
    return render_template('upload.html')
@cross_origin()    
@app.route('/sign-s3/')
def sign_s3():
  # Load necessary information into the application
  S3_BUCKET = os.environ.get('S3_BUCKET')

  # Load required data from the request
  file_name = request.args.get('file-name')
  file_type = request.args.get('file-type')

  # Initialise the S3 client
  s3 = boto3.client('s3',region_name='ap-south-1')
  # Generate and return the presigned URL
  presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = file_name,
    Fields = {"acl": "public-read", "Content-Type": file_type},
    Conditions = [
      {"acl": "public-read"},
      {"Content-Type": file_type}
    ],
    ExpiresIn = 3600
  )
  return json.dumps({
    'data': presigned_post,
    'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
  })

@app.route("/companies")       
def company_list():
    global top_companies
    global top_company_changed
    contents = show_image(os.environ.get('S3_BUCKET'))
    print(len(contents))
    if len(contents)>0:
      f =requests.get(contents[0], allow_redirects=True)
      #print(f.text)
      temp=f.text.split("\n")
      for x in temp:
        top_companies.add(x)
    #print(top_companies)          
    # import json
    # data = json.loads(f.text)
    top_company_changed=True
    return render_template("upload.html",result="file submitted successfully")
def show_image(bucket):
    s3_client = boto3.client('s3',region_name='ap-south-1')
    public_urls = []
    try:
        for item in s3_client.list_objects(Bucket=bucket)['Contents']:
            text=item['Key']
            index=text.find(".")
            #print(text[index+1:])
            if text[index+1:]=="csv":
                presigned_url = s3_client.generate_presigned_url('get_object', Params = {'Bucket': bucket, 'Key': item['Key']}, ExpiresIn = 100)
                public_urls.append(presigned_url) 

    except Exception as e:
        print("expection:"+str(e))
    # for item in s3_client.list_objects(Bucket=bucket)['Contents']:
    #     print(item['Key'])    
    # print("[INFO] : The contents inside show_image = ", public_urls)
    return public_urls
@app.route("/resumes")
def resume_list():
     contents = show_image2(os.environ.get('S3_BUCKET'))
       #print(f.text)
       #print(resume_text)
     return render_template("upload.html",result2=contents)  
def show_image2(bucket):
    # fs = obj.get()['Body'].read()
    # pdfFile = PdfFileReader(BytesIO(fs))
    s3_client = boto3.client('s3',region_name='ap-south-1')
    resumes= []
    count=0
    try:
        for item in s3_client.list_objects(Bucket=bucket)['Contents']:
            s3 = boto3.resource('s3')
            text=item['Key']
            index=text.find(".")
            if text[index+1:]=="docx" or text[index+1:]=="doc":
              count+=1
              obj = s3.Object(bucket,item['Key'])
              bytes_data= obj.get()['Body'].read()
              file_object=io.BytesIO(bytes_data)
              document=doc_to_text(file_object)
              #print(document)
              #document+="**********************"
              resumes.append(document)
              # document = docx.Document(docx=file_object)
              # doc=""
              # for p in document.paragraphs:
              #     doc+=p.text
              #     print(p.text)
              # doc+="*************************************\n"  
    except Exception as e:
        print("expection:"+str(e))
    # for item in s3_client.list_objects(Bucket=bucket)['Contents']:
    #     print(item['Key'])    
    # print("[INFO] : The contents inside show_image = ", public_urls)
    print(count)
    return resumes
def doc_to_text(path):
    text=docx2txt.process(path)
    text2=[line.replace('\t'," ") for line in text.split('\n') if line]
    return " ".join(text)           
@app.route("/gif")
def giff():
  return str(top_companies)

# @app.route("/submit_form/", methods = ["POST"])
# def submit_form():

#   username = request.form["username"]
#   full_name = request.form["full-name"]
#   avatar_url = request.form["avatar-url"]
#   return "dog"
# @app.route("/", methods=['GET', 'POST'])
# def streambyte():
#     global df
#     global top_companies
#     global top_company_changed
#     global z
#     # your file processing code is here...
#     f = request.files['file']
#     filename = secure_filename(f.filename)
#     client = boto3.client('s3',
#     aws_access_key_id=app.config['S3_KEY'],
#     aws_secret_access_key=app.config['S3_SECRET'])
#     client.put_object(Body=f,
#                       Bucket=app.config['S3_BUCKET'],
#                       Key=filename)
#     your_script_result = 'File Uploaded!'
#     df=pd.read_csv(f.filename)
#     top_company_changed=True
#     top_companies=df['0']
#     z=False
#     print(top_companies)
#     # your file processing code is here...
#     return render_template('upload.html', file_path = f, result = your_script_result)        
@app.route('/dog')
def cat():
  return str(top_company_changed)+str(top_companies)        
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
            "fulfillmentText":"{}".format(top_companies),
             "fulfillmentMessages": [
      {
        "platform": "ACTIONS_ON_GOOGLE",
        "simpleResponses": {
          "simpleResponses": [
            {
              "textToSpeech":"{}".format(top_companies)
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
          "{}".format(top_companies)
            
            ]
        }
      }
    ]}
        else:
            return {
            "fulfillmentText":"{}".format(companies),
             "fulfillmentMessages": [
      {
        "platform": "ACTIONS_ON_GOOGLE",
        "simpleResponses": {
          "simpleResponses": [
            {
              "textToSpeech":"{}".format(companies)
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
          "{}".format(companies)
            
            ]
        }
      }
    ]}
    elif(intent=="NoNeedOfTopCompanies"):
        print("cat")
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
          #return redirect(url_for('account'))
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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port = port,debug=True)
    #app.run(debug=True)
#if __name__ == '__main__':
#    port = int(os.getenv('PORT', 5000))
#    print("Starting app on port %d" % port)
#    app.run(debug=False, port=port, host='0.0.0.0')