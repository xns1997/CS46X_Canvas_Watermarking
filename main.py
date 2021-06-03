from flask import Flask, render_template, request, flash, redirect, url_for,send_file, make_response
import os
from canvasapi import Canvas
from werkzeug.utils import secure_filename
import requests
from water import water
import asyncio

API_URL = "https://canvas.oregonstate.edu/"
# Canvas API key
API_KEY = "1002~m1ShsxLu5bZY6SbSd5KlXjN9ejluixXwRFVYDvVQhGjIMx46dLJqS81NfZtCeTRJ"

app = Flask(__name__,template_folder='templates')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.before_request
def log_request():
    # app.logger.debug("Request Headers %s", request.headers)
    return None

@app.route('/upload',methods=["GET","POST"])
def getHomework():
    form = request.form
    clientID = form['custom_clientid']
    logo_url = form['custom_logo_url']
    canvas = Canvas(API_URL, clientID)
    user_data = {"Name":form['lis_person_name_full'],
                 "Role":form['roles'],
                 "Institution":form['tool_consumer_instance_name']
                }
    import re
    regex = r"\d{7,}"
    matches = re.findall(regex, form['custom_membership_service_url'], re.MULTILINE)
    course_id = matches[0]
    print(course_id)
    course = canvas.get_course(course_id)
    assigments=course.get_assignments()
    assList=[{"name":item.name,"id":item.id} for item in assigments]
    # return str(clientID)
    course = {"Title":course.name,"Logo":logo_url}
    datas = {"ass":assList,"course":course,"user":user_data}
    return render_template("assList.html",data = datas)

@app.route('/clientID/<clientID>/course/<courseID>',methods=["GET","POST"])
def getHomeworkwiCourse(clientID=None,courseID=None):
    canvas = Canvas(API_URL, clientID)
    course = canvas.get_course(courseID)
    assigments=course.get_assignments()
    assNameList=[item.name for item in assigments]
    assIDList=[item.id for item in assigments]
    print(assNameList)
    # return str(clientID)
    return render_template("assList.html",len=len(assNameList),Ass=assNameList,AssID=assIDList,title=course.name)

@app.route('/submit', methods=['POST'])
def upload_file():
    print('received!!')
    print(request.form)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_dir = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print("Upload: ",file_dir)
            print("File Save: ",file.save(file_dir))
            f = request.form
            info = { 'name':f['name'],\
                    'title':f['title'],\
                    'inst':f['inst'],\
                    'id':f['id']}
            w = water(file_dir,'./logo.png','./config.ini',info)
            d = w.do()
            return make_response("Uploaded",200)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    file_dir = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    send_from_directory(app.config['UPLOAD_FOLDER'],filename,as_attachment=True)
    return send_file(file_dir, as_attachment=True)

@app.route("/download/<fileName>",methods=["POST","GET"])
def downloadFile(fileName):
    path = os.path.join(app.config['UPLOAD_FOLDER'], fileName)
    return send_file(path, as_attachment=True)
@app.route("/try",methods=["POST","GET"])
def test():
    print(request.form)
    url = "https://canvas.oregonstate.edu/login/oauth2/auth?client_id={0}&response_type=code&redirect_uri=https://example.com/oauth_complete".format(API_KEY)
    # headers = {"Authorization":"Bearer"+request.form['oauth_signature']}
    res = requests.get(url)
    print(res.text)
    return res.text



if __name__ == "__main__":  
    app.config['ENV'] = 'development'
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    app.config['JSON_AS_ASCII'] = False
    app.config['UPLOAD_FOLDER']="static/uploadStack/"
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='0.0.0.0', port='2333',ssl_context='adhoc')