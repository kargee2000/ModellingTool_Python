from flask import Flask, render_template, request, redirect, url_for, g, send_from_directory
from flask_wtf import Form
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from wtforms import Form, TextField, PasswordField, validators
import pandas as pd
from pandas import Series
from pandas import DataFrame
import template,categ,vardist,chisqrt,treat1,corr1,vif1,tree1,linreg1,crosstab
from werkzeug.datastructures import MultiDict
import scipy.stats
import statsmodels.stats.outliers_influence as of
from sklearn import tree
from sklearn.externals.six import StringIO  
from StringIO import StringIO
from sklearn import linear_model
import statsmodels.api as sm
import numpy as np
import os
from sklearn.cross_validation import train_test_split
import pickle

#This displays the various nodes in the tree on the HTML form. 
#It will take the Decision tree fit and return the HTML string to be printed on screen. This is still WIP
def build_tree_html(k,px_str,lpx,wpx,tpx,hpx):
    k1 = k.split(";")
    label_df = DataFrame({'label':[],'strin':[]})
    temp_conn_df = DataFrame({'parent':[],'child':[]})
    conn_df = DataFrame({'parent':[],'child':[]})
    row_count = 0
    conn_count = 0
    label_nm = ""
    label_nm1 = ""    
    string_nm = ""
    temp_str = ""
    nodes = list()
    temp_kar = 0
    #For loop that reads the list and puts the lines into separate list and Dataframe
    for i in k1:
        if(i.find("""label=""")>0):
            z = i.find("\n")
            i = i[z:]
            z = i.find("\n")
            i = i[z:]
            z = i.find("0")
            label_nm = str(i[1:3])
            string_nm = str(i[3:len(i)])
            label_df.ix[row_count,0] = label_nm.strip()
            label_df.ix[row_count,1] = string_nm
            row_count = row_count + 1
        elif(i.find("->")>0):
            temp_str = str(i)
            nodes = temp_str.split("->")
            conn_df.ix[conn_count,0] = str(nodes[1]).strip()
            temp_str = str(nodes[0]).replace("\n","")
            conn_df.ix[conn_count,1] = str(temp_str).strip()
            conn_count = conn_count + 1            
        temp_kar = temp_kar + 1    
    #Read the dataframe and list and print out into string
    conn_dict = {}
    df_counter = 0       
    string_nm1 = ""
    temp_str=""
    html_str=""
    temp_lpx = lpx
    temp_tpx = tpx
    ramp_fac = 200
    temp_list=list()
    child1=0
    child2=0
    while(df_counter < len(label_df)):
        label_nm1 = label_nm1.replace("\n","")        
        label_nm1 = label_df.iloc[df_counter,0]
        label_nm1 = label_nm1.strip()
        string_nm1 = label_df.iloc[df_counter,1]
        if(int(label_nm1) == 0):
            temp_str = px_str
            string_nm1 = string_nm1.replace("\n"," ")
            s1 = list()
            s1.append(tpx)
            s1.append(lpx)
            s1.append(ramp_fac)
            conn_dict[label_nm1]=s1
            temp_str = temp_str.replace("tree_text_here",string_nm1[0:20])
            temp_str = temp_str.replace("<top>",str(tpx))
            temp_str = temp_str.replace("<width>",str(wpx))
            temp_str = temp_str.replace("<height>",str(hpx))
            temp_str = temp_str.replace("<left>",str(lpx))
            html_str = html_str + temp_str
        else:
            temp_conn_df = DataFrame({'parent':[],'child':[]})
            temp_conn_df = conn_df[conn_df['child']==label_nm1]
            temp_ind=temp_conn_df.iloc[0,1]
            temp_conn_df1 = conn_df[conn_df['parent']==temp_ind]
            temp_list=conn_dict[temp_ind]
            temp_conn_df1_count = len(temp_conn_df1)
            ramp_fac = int(temp_list[2])
            if(temp_conn_df1_count == 2):
                child1 = temp_conn_df1.iloc[0,0]
                child2 = temp_conn_df1.iloc[1,0]
                if(child1 == label_nm1 and (int(child1) > int(child2))):
                    temp_tpx=int(temp_list[0]) + 60
                    temp_lpx=int(temp_list[1]) + ramp_fac
                elif(child1 == label_nm1 and (int(child1) < int(child2))):
                    temp_tpx=int(temp_list[0]) + 60
                    temp_lpx=int(temp_list[1]) - ramp_fac
                elif(child2 == label_nm1 and (int(child1) > int(child2))):
                    temp_tpx=int(temp_list[0]) + 60
                    temp_lpx=int(temp_list[1]) - ramp_fac
                elif(child2 == label_nm1 and (int(child1) < int(child2))):
                    temp_tpx=int(temp_list[0]) + 60
                    temp_lpx=int(temp_list[1]) + ramp_fac
            temp_list1 = list()
            temp_list1.append(temp_tpx)
            temp_list1.append(temp_lpx)
            temp_list1.append(ramp_fac-45)
            conn_dict[label_nm1]=temp_list1
            temp_str = px_str
            string_nm1 = string_nm1.replace("\n"," ")
            string_nm1 = string_nm1.replace("[label=","")
            temp_str = temp_str.replace("tree_text_here",string_nm1[0:15])
            temp_str = temp_str.replace("<top>",str(temp_tpx))
            temp_str = temp_str.replace("<width>",str(wpx))
            temp_str = temp_str.replace("<height>",str(hpx))
            temp_str = temp_str.replace("<left>",str(temp_lpx))
            html_str = html_str + temp_str
            
        df_counter = df_counter + 1
        
    return html_str

def ret_day(k4):
    return k4.day

def ret_month(k4):
    return k4.month

def ret_year(k4):
    return k4.year

app = Flask(__name__)      
filename = "E:/data_file_" 

#New login manager code
lm = LoginManager(app)
lm.login_view = "/login"
app.secret_key = 'secret'
users = {'karthikganapathy' : ['karthikganapathy_1127','admin123'],'karthickhariharan' : ['karthickhariharan','kh123'],'rameshhariharan' : ['rameshhariharan','test123'],'vivekdesikan' : ['vivekdesikan','test123'],'sandhyagopalan' : ['sandhyagopalan','test123']}
app.config['UPLOAD'] = 'UPLOAD'

## Functions for Login Manager begins
class User():
    def __init__(self,email):
        self.email = email
        self.id = users[email][0]
        self.password = users[email][1]

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

@lm.user_loader
def load_user(userid):
    for u in users.keys():
        if users[u][0] == userid:
            email = u
            break
        else:
            email = ''
    return User(email) if email else None

@app.before_request
def before_request():
    g.user = current_user

class LoginForm(Form):
    email = TextField('email')
    password = PasswordField('password')

    def validate_login(self):
        username = self.email.data
        password = self.password.data
        if username in users:
            return True if users[username] == password else False
        return 

def hashIt(val):
    return str(abs(hash(val)))
	
## Functions for Login Manager ends

df = DataFrame()
df_train = DataFrame()
df_test = DataFrame()
origin_df = DataFrame()
test_train_created = False
final_html = ""
log_predict1 = DataFrame({'results':[]})
lin_predict1 = DataFrame({'results':[]})
log_model = ()
lin_model= ()
res_log = ()
res_lin = ()
log_reg_key = list()
lin_reg_key = list()

#@app.route('/',methods=['GET','POST'])
#@login_required
#def home1():
#  return render_template('index.html')

@app.route('/',methods=['GET', 'POST'])
@app.route('/login',methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        if username in users:
            if users[username][1] == password:
                #flash("Logged in successfully.")
                user = User(username)
                login_user(user)
                #os.path.join(user)
                return redirect(url_for('upload'))
            else:
                return 'User doesn\'t Exits'
    return render_template('sign_in.html', form=form)

@app.route('/<var>',methods=['GET','POST'])
@login_required
def home(var):
  global df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  if(str(var) == 'restore' or str(var) == 'view' or str(var) == 'testrain'):
	try:
		temp_list1 = read_global(str(current_user.get_id()))
		df = temp_list1[0]
		df_train= temp_list1[1]
		df_test= temp_list1[2]
		test_train_created= temp_list1[3]
		lin_model= temp_list1[4]
		log_model= temp_list1[5]
		log_reg_key= temp_list1[6]
		res_log= temp_list1[7]
		log_predict1= temp_list1[8]
		res_lin= temp_list1[9]
		lin_predict1= temp_list1[10]
		lin_reg_key= temp_list1[11]
		final_html = temp_list1[12]
		#df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))
	except:
		s = "<br><br>" + df[1:10].to_html()
		final_html = template.s1 + """</div> <font color="tomato">Something went wrong. Please ensure you follow the proper sequence to call the functions </font>""" + s
		return final_html
  # Upload the data file
  if (var == 'upl'):
	f = request.files['myfile']
	filename1 = ""
	filename1 = filename + str(current_user.get_id()) + ".csv"
	f.save(filename1)
	filename1 = filename + str(current_user.get_id()) + ".csv"
	df = pd.read_csv(filename1)
	#Original Data frame
	origin_df = df
	#Take a subset of records to display as sample
	df1 = df[1:10]
	s = "<br><br>" + df1.to_html()
	# String in HTML form to be returned
	final_html = template.s2 +"""<div style="width:600px; height:700px; position: absolute; top: 20px; left:500px;"><b>File Uploaded Successfully !!</b></div>"""+  s
	#Code to get the key variables used across functions
	save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
	return final_html
  # This will restore the original data uploaded from CSV. All changes made in the functions will be lost
  elif (var == 'restore'):
	try:
		s = "<br><br>" + df[1:10].to_html()
		final_html = template.s1 + "</div>" + s
		return final_html
	except:
		final_html = template.s1 + """</div><font ="lightcoral">Something went wrong. Please try again</font>""" + s
		return final_html
  #Function called to view sample rows
  elif (var ==	'view'):
	try:
		#df_train.to_csv(template.save_train_data_path)
		temp_df = df[1:10]	
		s = "<br><br>" + temp_df.to_html()
		return template.s1 + "</div><br> <b> Sample Data </b><br>" + s
	except:
		return template.s1 + """</div><br><font color="lightcoral"> Something went wrong. Please try again </font><br><br>""" + df[1:15].to_html()
  # Create random Test and train data samples
  elif (var == 'testrain'):
	#df = pd.read_csv("E:/test2.csv")
	#s = "<br><br>" + df[1:15].to_html()
	s = df[1:10].to_html()
	final_html = template.s1 + template.train_per + "</div>" + s
	return final_html
  elif (var == 'lin_test'):
	#df = pd.read_csv("E:/test2.csv")
	try:
		df_test['PREDICTED_LIN'] = res_lin.predict(df_test[lin_reg_key])
		df_test.to_csv(template.save_lin_predict_path)
		s = """<div style="width:600px; height:700px; position: absolute; top: 20px; left:500px;"><br><br> ***** Predicted Values (sample) **** <br>""" + (DataFrame(df_test['PREDICTED_LIN'])[1:10]).to_html() + "</div>" + df[1:15].to_html()
		final_html = template.s1 + "</div>" + s
		#Code to get the key variables used across functions
		save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
		return final_html
	except KeyError,ValueError:
		s = """<div style="width:600px; height:700px; position: absolute; top: 20px; left:500px;"><font color="lightcoral">Error.  Please select the proper parameters and try again. </font><br><br> <br></div>""" + df[1:15].to_html()
		final_html = template.s1 + "</div>" + s
		return final_html
	except AttributeError:
		s = """<div style="width:600px; height:700px; position: absolute; top: 20px; left:500px;"><font color="lightcoral"> Error. Please select the proper parameters and try again. </font><br><br></div>""" + df[1:15].to_html()
		final_html = template.s1 + "</div>" + s
		return final_html	
	except IOError,e:
		s = """<div style="width:600px; height:700px; position: absolute; top: 20px; left:500px;"><font color="lightcoral"> IO Error.  Error with file locations. </font><br><br></div>""" +str(e) + df[1:15].to_html()
		final_html = template.s1 + "</div>" + s
		return final_html	
  elif (var == 'log_test'):
	try:
		df_test['PREDICTED_LOG'] = res_log.predict(df_test[log_reg_key])
		df_test.to_csv(template.save_log_predict_path)
		s = """<div style="width:600px; height:700px; position: absolute; top: 20px; left:500px;"><br><br> ***** Predicted Values (sample) **** <br>""" + (DataFrame(df_test['PREDICTED_LOG'])[1:10]).to_html() + "</div>"  + df[1:15].to_html()
		final_html = template.s1 + "</div>" + s
		#Code to get the key variables used across functions
		save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
		return final_html
	except KeyError,ValueError:
		s = """<div style="width:600px; height:700px; position: absolute; top: 20px; left:500px;"><font color="lightcoral"> Error.  Please select the proper parameters and try again.</font><br><br></div>""" + df[1:15].to_html()
		final_html = template.s1 + "</div>" + s
		return final_html
	except AttributeError:
		s = """<div style="width:600px; height:700px; position: absolute; top: 20px; left:500px;"><font color="lightcoral"> Error.  Please select the proper parameters and try again.</font><br><br></div>""" + df[1:15].to_html()
		final_html = template.s1 + "</div>" + s
		return final_html
	except IOError,e:
		s = """<div style="width:600px; height:700px; position: absolute; top: 20px; left:500px;"><font color="lightcoral"> IO Error.  Error with file locations. </font><br><br></div>""" +str(e) + df[1:15].to_html()
		final_html = template.s1 + "</div>" + s
		return final_html	
  elif (var == 'bin1'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"bin")
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>"
	return final_html
# Create Check-box for Dependent and Independent Variables for Decision tree
  elif (var == 'tree'):
	coln = list(df.columns.values)
	k = create_treecheckbox(coln)
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div><br>" 
	return final_html
# Removing variables from data
  elif (var == 'remove'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"remove")
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
# Outlier treatment of data
  elif (var == 'outtr'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"outliers")
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
# Create dummy variables based on conditions
  elif (var == 'cond'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"cond")
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>"
	return final_html
  #Function called after selecting variables from Check-box to be removed	
  elif (var ==	'four'):
	if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		df1 = df
		for key1 in Listkey1:
			if(key1 <> "Remove"):
				df1 = df1.drop(key1,1)
		df = df1
		temp_df = df[1:10]	
		s = "<br><br><br><br><br><br>" + temp_df.to_html()
		#Code to get the key variables used across functions
		save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
		return template.s1 + "</div>" + s
  #Function called to Export predicted Test data
  elif (var ==	'export1'):
	try:
		df_test.to_csv(template.save_lin_predict_path)
		#log_predict1.to_csv(template.save_log_predict_path)
		temp_df = df[1:10]	
		s = "<br><br>" + temp_df.to_html()
		return template.s1 + "</div><br> Data Exported to "+ template.save_lin_predict_path + " drive <br>" + s
	except:
		return template.s1 + """</div><br><font color="lightcoral"> Something went wrong. Please try again </font><br><br>""" + df[1:15].to_html()
  #Function called to Export dataset prepared
  elif (var ==	'export2'):
	try:
		df.to_csv(template.save_prep_data_path)
		temp_df = df[1:10]	
		s = "<br><br>" + temp_df.to_html()
		return template.s1 + "</div><br> Data Exported to " + template.save_prep_data_path + " drive <br>" + s
	except:
		return template.s1 + """</div><br><font color="lightcoral"> Something went wrong. Please try again </font><br><br>""" + df[1:15].to_html()
  #Function called to Export dataset prepared
  elif (var ==	'export3'):
	try:
		df_train.to_csv(template.save_train_data_path)
		temp_df = df[1:10]	
		s = "<br><br>" + temp_df.to_html()
		return template.s1 + "</div><br> Data Exported to " + template.save_train_data_path + " drive <br>" + s
	except:
		return template.s1 + """</div><br><font color="lightcoral"> Something went wrong. Please try again </font><br><br>""" + df[1:15].to_html()
  # Create Checkbox for dependent and independent variables for Linear Regression		
  elif (var == 'linreg'):
	coln = list(df.columns.values)
	k = create_reg_checkbox(coln,"linear")
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div><br><br>"
	return final_html
  # Create Checkbox for dependent and independent variables for Linear Regression		
  elif (var == 'logreg'):
	coln = list(df.columns.values)
	k = create_reg_checkbox(coln,"logistic")
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div><br><br>"
	return final_html	
  # Create checkbox to select variables to be declared as categorical	
  elif (var == 'categ'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"categorical")
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>"
	return final_html
  # Create Check-box to select variables to view distribution	
  elif (var == 'vardis'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"variable_dist")
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>"
	return final_html
  # Create Check-box to select variables to view distribution	
  elif (var == 'datedis'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"date_dist")
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>"
	return final_html
  # Create check-box to select variables to declare as dummy	
  elif (var == 'dumm'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"dummy_variables")
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>"
	return final_html
  # Create checkbox to select variables for chi-square
  elif (var == 'chisq'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"chi_square")
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>"
	return final_html
  # Create checkbox to select variables for cross tab
  elif (var == 'cross'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"crosstab")
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>"
	return final_html
  # Create checkbox to select variables for missing value treatment	
  elif (var == 'treat'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"missing_value")
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>"
	return final_html
  # Create check-box to select variables for correlation test	
  elif (var == 'corr'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"correlation")
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1  + k + "</div>"
	return final_html
  # Create checkbox to select variables to test for VIF	
  elif (var == 'vif'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"vif")
	temp_df = df[1:10]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>"
	return final_html	
  return render_template('index.html')

#Function gets called on clicking on Categorical variable creation link  
@app.route('/categ1',methods=['GET','POST'])
@login_required
def categ1():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df

  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))

  if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		df1 = df
		for key1 in Listkey1:
			if(key1 <> "Mark as Categorical"):
				df1[key1] = pd.Categorical.from_array(df1[key1]).labels
				#df1[key1] = pd.Categorical.from_array(df1[key1])
		df = df1
		temp_df = df[1:10]		
		final_html = template.s1 + "</div><br><br>" + temp_df.to_html()
		#Code to get the key variables used across functions
		save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
		return final_html
  return 'helloo'

#Function gets called on clicking on Variable Distribution link  
@app.route('/vardis1',methods=['GET','POST'])
@login_required
def vardis():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))

  count_val = ""
  if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		df1 = df
		firstkey=0
		secondkey=0
		for key1 in Listkey1:
			if(key1 == "Display Categorical Distribution"):
				firstkey=1
			elif(key1 == "Display Continuous Distribution"):
				secondkey=1
		for key1 in Listkey1:
			if(key1 <> "Display Categorical Distribution" and key1 <> "Display Continuous Distribution"):
				if(firstkey == 1):
					s = df1[key1].value_counts() 
					s = DataFrame(s)
					count_val = count_val + "<br> Variable name" + str(key1)+ "<br>" + s.to_html() + "  "
				elif(secondkey == 1):
					percent_1 = np.percentile(df1[key1],1)
					percent_5 = np.percentile(df1[key1],5)
					percent_10 = np.percentile(df1[key1],10)
					percent_90 = np.percentile(df1[key1],90)
					percent_95 = np.percentile(df1[key1],95)
					percent_99 = np.percentile(df1[key1],99)
					s1 = DataFrame(df1[key1].describe())
					total_rows = len(df1.index)
					non_zero_count = np.count_nonzero(df1[key1])
					not_a_number_count = np.count_nonzero(np.isnan(df1[key1]))
					count_val = count_val + "<br><br>"+ s1.to_html() + "<br><b> 1 %ile : </b>" + str(percent_1) +  "<br><b> 5 %ile : </b>" + str(percent_5) +   "<br><b> 10 %ile : </b>" + str(percent_10) +  "<br><b> 90 %ile : </b>" + str(percent_90) + "<br><b> 95 %ile : </b>" + str(percent_95) +"<br><b> 99 %ile : </b>" + str(percent_99) + "<br><b> Total row count : </b>"+ str(total_rows) + "<br><b> Non-zero count : </b>" + str(non_zero_count) + "<br><b> Not a number count : </b>"  + str(not_a_number_count) + "<br>"
		temp_df = df[1:10]		
		final_html = vardist.s1 + count_val + "</div><br><br>"
		  	#Code to get the key variables used across functions
		save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
		return final_html
  return 'helloo'

#Function gets called on clicking on Variable Distribution link  
@app.route('/datedis1',methods=['GET','POST'])
@login_required
def datedis1():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))

  count_val = ""
  if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		df1 = df
		for key1 in Listkey1:
			if(key1 <> "Display Date-fields distribution"):
				df1['date1'] = pd.to_datetime(df1[key1])
				z1 = df1['date1'].apply(ret_day)
				z2 = df1['date1'].apply(ret_month)
				z3 = df1['date1'].apply(ret_year)
				#s1 = z1.value_counts() 
				s2 = z2.value_counts() 
				s3 = z3.value_counts() 
				#days_count = DataFrame(s1)
				months_count = DataFrame(s2)
				years_count = DataFrame(s3)
				count_val = count_val + "<br> Variable name  <span>" + str(key1)+ "</span><br><br> Month distribution " + months_count.to_html() + "<br><br> Years distribution " + years_count.to_html() + "  "
				df1 = df1.drop('date1',1)
		temp_df = df[1:15]		
		final_html = vardist.s1 + count_val + "</div><br><br>"

		#Code to get the key variables used across functions
		save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
		return final_html
  return 'helloo'
  
#Function gets called on clicking on Chi-Square function link. For now this calls chi-square for only two variables - a DV and IDV  
@app.route('/chisq1',methods=['GET','POST'])
@login_required
def chisq1():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))

  chi_key = list()
  if request.method == 'POST':
		try:
			Listkey1 = list(MultiDict(request.form).values())
			for key1 in Listkey1:
				if(key1 <> "Display Details"):
					chi_key.append(key1)
			ctab = pd.crosstab(df[chi_key[0]],df[chi_key[1]])	
			fit =  scipy.stats.chi2_contingency(ctab)
			temp_df = df[1:15]		
			final_html = template.s1 + " <br><br><u><b> Chi-Square Test Results </b></u><br> Chi-Square statistic: "+ str(fit[0]) + "<br><br> p-value: " + str(fit[1]) + "<br><br> Cross Tabulation <br><br>" + ctab.to_html() + "<br><br></div>"
			#final_html = template.s1 + "</div> <br><br> Chi-Square Test <br> p-value : "+ str(fit) + "<br><br>" + temp_df.to_html()
			#Code to get the key variables used across functions
			save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
			return final_html
		except KeyError:
			final_html = template.s1 + """ <br><br><b> <font color="lightcoral"> Error. Select 2 categorical variables for Chi-square test </font> </b><br><br></div>"""
			return final_html
  return 'helloo'

#Function gets called on clicking on Cross Tabulation function link. This calls Cross Tabs for only two variables
@app.route('/cross1',methods=['GET','POST'])
@login_required
def cross1():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))

  cross_key = list()
  if request.method == 'POST':
		try:
			Listkey1 = list(MultiDict(request.form).values())
			for key1 in Listkey1:
				if(key1 <> "Display Cross Tabulation"):
					cross_key.append(key1)
			ctab = pd.crosstab(df[cross_key[0]],df[cross_key[1]])	
			temp_df = df[1:15]		
			final_html = template.s1 + " <br><br> Cross Tabulation result <br> : "+ ctab.to_html() + "<br><br></div>"
			#Code to get the key variables used across functions
			save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
			return final_html
		except IndexError,KeyError:
			final_html = template.s1 + """ <br><br> <font color="lightcoral">Wrong keys selected. Please select two categorical columns </font><br><br></div>""" + df[1:15].to_html()
			return final_html
  return 'helloo'
  
#Function gets called on calling Linear Regression link
@app.route('/linreg2',methods=['GET','POST'])
@login_required
def linreg2():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df,lin_model,lin_reg_key,res_lin
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))
  lin_reg_key = list()
  firstkey=0
  secondkey=0
  if request.method == 'POST':
		try:
			Listkey1 = list(MultiDict(request.form).values())
			Listkey2 = MultiDict(request.form)
			DV_lin_reg = Listkey2.get('DV')
			df1 = df
			for key1 in Listkey1:
				if(key1 == "Build Model on Train data"):
					firstkey=1
				elif(key1 == "Build Model on full data"):
					secondkey=1
			for key1 in Listkey1:
				if(key1 <> "Build Model on Train data" and key1 <> "Build Model on full data" and key1 <> DV_lin_reg):
					lin_reg_key.append(key1)
			if(firstkey==1):
				df1 = df_train.loc[:,lin_reg_key]
				Y = df_train[DV_lin_reg]
				linreg = linear_model.LinearRegression()
				lin_model = sm.OLS(Y.values,df1.values)
			elif(secondkey==1):
				df1 = df.loc[:,lin_reg_key]
				Y = df[DV_lin_reg]
				#lin_model = linear_model.LinearRegression()
				lin_model = sm.OLS(Y.values,df1.values)
			res_lin = lin_model.fit()
			s = (res_lin.summary()).as_html()
			temp_df = df[0:15]	
			t = """</div><div style="width:600px; height:700px; position: absolute; top: 20px; left:500px;"><br><b> Linear Regression Result </b><br>"""
			final_html = template.s1 + t + s + "</div><br><br><br>" + temp_df.to_html()
			#Code to get the key variables used across functions
			save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
			return final_html
		except KeyError:
			final_html = template.s1 + """<br><font color="lightcoral"> Error. Please select the proper parameters and try again. </font><br><br></div>""" + df[1:15].to_html()
			return final_html
		except ValueError:
			final_html = template.s1 + """<br><font color="lightcoral"> Error. Please select the proper parameters and try again. </font><br><br></div>""" + df[1:15].to_html()
			return final_html
		except AttributeError:
			final_html = template.s1 + """<br><font color="lightcoral"> Ensure Test and train data is created before running the predict on Train. </font><br><br></div>""" + df[1:15].to_html()
			return final_html
  return 'helloo'  

#Function gets called on calling Logistic Regression link
@app.route('/logreg2',methods=['GET','POST'])
@login_required
def logreg2():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df,log_model,log_reg_key,res_log
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))

  log_reg_key = []
  firstkey=0
  secondkey=0
  df2 = DataFrame()
  if request.method == 'POST':
		try:
			Listkey1 = list(MultiDict(request.form).values())
			Listkey2 = MultiDict(request.form)
			DV_log_reg = Listkey2.get('DV')
			df1 = df
			for key1 in Listkey1:
				if(key1 == "Build Model on Train data"):
					firstkey=1
				elif(key1 == "Build Model on Entire data"):
					secondkey=1
			for key1 in Listkey1:
				if(key1 <> "Build Model on Train data" and key1 <> "Build Model on Full data" and key1 <> DV_log_reg):
					log_reg_key.append(key1)
			if(firstkey==1):
				df2 = df_train.loc[:,log_reg_key]
				Y = df_train[DV_log_reg]
				log_model = sm.Logit(Y.values,df2.values)
				res_log = log_model.fit()
			elif(secondkey==1):
				df1 = df.loc[:,log_reg_key]
				Y = df[DV_log_reg]
				log_model = sm.Logit(Y.values,X.values)
				res_log = log_model.fit()
			s = (res_log.summary()).as_html()
			temp_df = df[0:15]	
			t = """</div><div style="width:600px; height:700px; position: absolute; top: 20px; left:500px;"><br> Logistic Regression Results <br>"""
			final_html = template.s1 + t + s + "</div><br><br><br>" + temp_df.to_html()
			#Code to get the key variables used across functions
			save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
			return final_html
		except KeyError:
			final_html = template.s1 + """<br><font color="lightcoral"> Error. Please select the proper parameters and try again.</font><br><br></div>""" + df[1:15].to_html()
			return final_html
		except ValueError:
			final_html = template.s1 + """<br><font color="lightcoral"> Error.  Please select the proper parameters and try again. </font><br><br></div>""" + df[1:15].to_html()
			return final_html
		except AttributeError:
			final_html = template.s1 + """<br><font color="lightcoral"> Error. Ensure Test and train data is created before running the predict on Train. </font><br><br></div>""" + df[1:15].to_html()
			return final_html	
  return 'helloo'  

  #Function gets called on clicking on Decision Tree creation link  
@app.route('/tree2',methods=['GET','POST'])
@login_required
def tree2():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))

  chi_key = list()
  init_style_string = template.style_string
  if request.method == 'POST':
		try:
			Listkey1 = list(MultiDict(request.form).values())
			Listkey2 = MultiDict(request.form)
			max_tree_depth = int(Listkey2.get('tree_depth'))
			min_leaf_samp = int(Listkey2.get('min_sample'))
			DV_tree = Listkey2.get('DV')
			df1 = df
			for key1 in Listkey1:
				if(key1 <> "Build Tree" and key1 <> DV_tree and key1 <> str(max_tree_depth) and key1 <> str(min_leaf_samp)):
					chi_key.append(key1)
			df1 = df.loc[:,chi_key]
			df2 = df1.values
			Y = df[DV_tree]
			clf = tree.DecisionTreeClassifier(max_depth=max_tree_depth,min_samples_leaf=min_leaf_samp)
			clf = clf.fit(df2,Y.values)
			dot_data = StringIO()
			tree.export_graphviz(clf, feature_names=list(df1.columns.values),out_file=dot_data)
			k = dot_data.getvalue()
			k = k.replace("digraph Tree","")
			k = k.replace("{","")
			k = k.replace("}","")
			k = k.replace("label=","IDV=")
			s = k.split(";")
			k = ""
			for k1 in s:
				k = k + "<br>" + str(k1)
			temp_df = df[0:15]	
			t = """</div><div style="width:700px; height:700px; position:absolute; top: 20px; left:500px;"><br> <b>Decision Tree Result</b> <br>"""
			#final_html = template.s1 + t + k + "</div><br><br><br>" + temp_df.to_html()
			final_html = template.s1 + t + k + "</div><br><br><br>"
			#Code to get the key variables used across functions
			save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
			return final_html
		except ValueError:
			final_html = template.s1 + """</div><div style="width:700px; height:700px; position:absolute; top: 20px; left:500px;"><br> <font color="lightcoral">Error. Please select the proper values and retry. </font></div><br><br>""" + df[1:15].to_html()
			return final_html
  return 'helloo'  
  
  #WIP function. Currently not in use. Will be built to display the Decision tree
@app.route('/tree3',methods=['GET','POST'])
@login_required
def tree3():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))

  chi_key = list()
  init_style_string = template.style_string
  if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		Listkey2 = MultiDict(request.form)
		DV_tree = Listkey2.get('DV')
		df1 = df
		for key1 in Listkey1:
			if(key1 <> "Build Tree" and key1 <> DV_tree):
				chi_key.append(key1)
		df1 = df.loc[:,chi_key]
		df2 = df1.values
		Y = df[DV_tree]
		clf = tree.DecisionTreeClassifier()
		clf = clf.fit(df2,Y.values)
		dot_data = StringIO()
		tree.export_graphviz(clf, out_file=dot_data)
		k = dot_data.getvalue()
		left_px = 600
		width_px = 150
		top_px = 50
		height_px = 309
		s = build_tree_html(k,init_style_string,left_px,width_px,top_px,height_px)
		temp_df = df[0:15]	
		t = """</div><div style="width:600px; height:700px; position: absolute; top: 20px; left:500px;"><br> Decision Tree result <br>"""
		final_html = template.s1 + t + k + "<br><br></div>" + temp_df.to_html()

		#Code to get the key variables used across functions
		save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
		return final_html
  return 'helloo'  
  
#Function gets called on clicking on Missing value treatment link
@app.route('/treat2',methods=['GET','POST'])
@login_required
def treat():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))
  firstkey = False
  secondkey = False
  if request.method == 'POST':
		try:
			Listkey1 = list(MultiDict(request.form).values())
			Listkey2 = MultiDict(request.form)
			for key1 in Listkey1:
				if(key1 == "Replace nulls,NAs with zeros"): 
					firstkey = True
					secondkey = False
				elif(key1 == "Custom: Enter values to replace"):
					secondkey = True
					firstkey = False
			if(secondkey):
				replace_str = str(Listkey2.get('changeval'))
				for key1 in Listkey1:
					if(key1 <> "Replace nulls,NAs with zeros" and key1 <> replace_str and key1 <> "Custom: Enter values to replace"):
						df[key1].fillna(replace_str)
			elif(firstkey):	
				replace_str = str(Listkey2.get('changeval'))
				for key1 in Listkey1:
					if(key1 <> "Replace nulls,NAs with zeros" and key1 <> replace_str and key1 <> "Custom: Enter values to replace"):
						df[key1].fillna(0)
			temp_df = df[1:15]		
			final_html = template.s1 + "<br>Null values were replaced!!<br><br></div>" + temp_df.to_html()
			#Code to get the key variables used across functions
			save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
			return final_html
		except:
			final_html = template.s1 + """<br><font color="lightcoral"> Something went wrong. Please try again !! <font><br><br></div>""" + df[1:15].to_html()
			return final_html
  return 'helloo'  

#Function gets called to create Dummy variables based on conditions
@app.route('/cond1',methods=['GET','POST'])
@login_required
def cond1():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))

  between_key = False
  great_key = False
  less_key = False
  column_key = ""
  new_column_key = ""
  df['decision'] = False
  if request.method == 'POST':
		try:
			Listkey1 = list(MultiDict(request.form).values())
			Listkey2 = MultiDict(request.form)
			Listkey3 = MultiDict(request.form).keys()
			for key1 in Listkey3:
				if(key1 <> "upper_val" and key1 <> "lower_val" and key1 <> "Submit" and key1 <> "func"):
					column_key = str(key1)
			for key1 in Listkey1:
				if(key1 == "between"): 
					between_key = True
					great_key = False
					less_key = False
				elif(key1 == "greater than"):
					between_key = False
					great_key = True
					less_key = False
				elif(key1 == "less than"):
					between_key = False
					great_key = False
					less_key = True
			if(between_key):
				upper_val = float(Listkey2.get('upper_val'))
				lower_val = float(Listkey2.get('lower_val'))
				new_column_key = "Dummy_"+ column_key + "_between_" + str(lower_val) + "_and_" + str(upper_val)
				df['decision'] = Series((df[column_key] > lower_val) & (df[column_key] <	 upper_val))
			elif(great_key):
				upper_val = float(Listkey2.get('upper_val'))		
				new_column_key = "Dummy_"+ column_key + "_great_than_" + str(upper_val)
				df['decision'] = Series(df[column_key] > upper_val)
			elif(less_key):	
				upper_val = float(Listkey2.get('upper_val'))		
				new_column_key = "Dummy_"+ column_key + "_less_than_" + str(upper_val)
				df['decision'] = Series(df[column_key] < upper_val)
			df[new_column_key] = 0
			df[new_column_key][df['decision']] = 1
			df = df.drop('decision',1)
			temp_df = df[1:15]		
			final_html = template.s1 + "<br>New Dummy variables created based on condition <br><br></div>" + temp_df.to_html()
			#Code to get the key variables used across functions
			save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
			return final_html
		except ValueError:
			final_html = template.s1 + """<br><font color="lightcoral"> Please enter valid value </font><br><br></div>""" + df[1:15].to_html()
			return final_html
		except KeyError:
			final_html = template.s1 + """<br><font color="lightcoral"> Please enter valid value </font><br><br></div>""" + df[1:15].to_html()
			return final_html
  return 'helloo'  
  
# Function gets called on clicking VIF function link
@app.route('/vif2',methods=['GET','POST'])
@login_required
def vif():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))

  chi_key = list()
  if request.method == 'POST':
		try:
			Listkey1 = list(MultiDict(request.form).values())
			df1 = df
			for key1 in Listkey1:
				if(key1 <> "Calculate VIF"):
					chi_key.append(key1)
			df1=df.loc[:,chi_key]
			df2 = df1.values
			temp_count = 0
			vif_result=""
			for key1 in chi_key:
				k = of.variance_inflation_factor(df2,temp_count)
				vif_result = vif_result + "<br>" + chi_key[temp_count] + ": " + str(k)
				temp_count = temp_count + 1
			temp_df = df[1:15]		
			final_html = template.s1 + "<br><b> Variance Inflation Factor for selected variables </b><br>"+ vif_result + "<br><br></div>" + temp_df.to_html()
			#Code to get the key variables used across functions
			save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
			return final_html
		except ValueError:
			final_html = template.s1 + """<br><font color="lightcoral"> Error. Please select valid values</font> <br><br></div>""" + df[1:15].to_html()
			return final_html
		except KeyError:	
			final_html = template.s1 + """<br><font color="lightcoral"> Error. Please upload file and select valid values </font> <br><br></div>""" + df[1:15].to_html()
			return final_html
  return 'helloo'  

# Function called to bin variables. The columns checked will be binned
@app.route('/bin2',methods=['GET','POST'])
@login_required
def bin2():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))
  
  unique_count = 0
  firstkey=0
  secondkey=0
  bin_val_fail = False
  if request.method == 'POST':
		try:
			Listkey1 = list(MultiDict(request.form).values())
			Listkey2 = MultiDict(request.form)
			bin_val = int(Listkey2.get('changeval'))
			for key1 in Listkey1:
				if(key1 == "Create Equal-height Bins"):
					firstkey=1
				elif(key1 == "Create Equal-width Bins"):
					secondkey=1
			for key1 in Listkey1:
				if(key1 <> "Create Equal-height Bins" and key1 <> "Create Equal-width Bins" and key1 <> str(bin_val)):
					k3 = set(df[key1])
					unique_count = sum(1 for num in k3)
					if(unique_count <= bin_val):
						bin_val_fail = True
						break
					if(firstkey==1):
						temp_bin_col = pd.qcut(df[key1],bin_val)
						temp_col_name = key1 + "eq_ht_bin"
						df[temp_col_name] = Series(temp_bin_col)
					elif(secondkey==1):	
						fix_bin_temp = np.array(df[key1])
						fix_bin = pd.cut(fix_bin_temp,bin_val)
						temp_col_name = key1 + "eq_wdth_bin"
						df[temp_col_name] = Series(fix_bin)
			temp_df = df[1:15]
			if(bin_val_fail):
				final_html = template.s1 + """<br><br><font color="red"> Bin count is more than the number of categories in columns </font><br> </div>""" + temp_df.to_html()
			else:
				final_html = template.s1 + "Successfully created bins !! </div><br>" + temp_df.to_html()
			 	#Code to get the key variables used across functions
			save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
			return final_html
		except ValueError:
			final_html = template.s1 + """<br><br> <font color="lightcoral"> Invalid value for bins!! Please enter a valid value </font> <br> </div>""" + (df[1:15]).to_html()
			return final_html
  return 'helloo'

# Dummy variables creation. The columns checked will be marked for dummy variables  
@app.route('/dumm1',methods=['GET','POST'])
@login_required
def dumm():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))
  if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		for key1 in Listkey1:
			if(key1 <> "Generate Dummy Variables"):
				pref = "ind_" + key1
				dummies = pd.get_dummies(df[key1], prefix=pref)
				df = df.join(dummies)
		temp_df = df[1:15]		
		final_html = template.s1 + "</div><br>" + temp_df.to_html()
		#Code to get the key variables used across functions
		save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
		return final_html
  return 'helloo'

# Function called to split test and train data
@app.route('/test1',methods=['GET','POST'])
@login_required
def test1():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))

  unique_count = 0
  err_key=0
  if request.method == 'POST':
		try:
			Listkey1 = list(MultiDict(request.form).values())
			Listkey2 = MultiDict(request.form)
			test_per = int(Listkey2.get('test_percent'))
			temp_df = df[1:10]	
			if(float(test_per) < 0 or float(test_per) > 100):
				err_key = 1
			if(err_key==0):
				prop_test = float(test_per)/float(100)
				msk = np.random.rand(len(df)) < prop_test
				df_train = df[~msk]
				df_test = df[msk]
				test_train_created = True
				final_html = template.s1 + "</div><br><br> Test and Train datasets created <br> " + temp_df.to_html()
				save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
			elif(err_key==1):
				final_html = template.s1 + """<br><br> <font color="red"> Please enter a valid percentage value </font> <br></div> """ + temp_df.to_html()
				#Code to get the key variables used across functions
				save_global(str(current_user.get_id()),df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
			return final_html
		except ValueError:
			final_html = template.s1 + """<br><br><font color="lightcoral"> Error. Please enter proper value to create Test and Train dataset. </font><br> </div>""" + df[1:10].to_html()
			return final_html
  return 'helloo'
  
# Function for correlation analysis. Correlation will be found for variables checked  
@app.route('/corr2',methods=['GET','POST'])
@login_required
def corr():
  global final_html
  global df,df_train,df_test,test_train_created,origin_df
  #Code to get the key variables used across functions
  global_filename = "global_vars" + str(current_user.get_id()) + ".txt"
  df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html = read_global(str(current_user.get_id()))
  k4 = MultiDict(request.form)
  print "Values",MultiDict(request.form).values()
  print "keys",MultiDict(request.form).keys()
  chi_key = list(request.form.getlist('correl'))
  
   #= list()
  if request.method == 'POST':
		try:
			Listkey1 = list(MultiDict(request.form).values())
			df1 = df
			#for key1 in Listkey1:
			#	if(key1 <> "Find correlation function"):
			#		chi_key.append(key1)
			df1 = df.loc[:,chi_key]
			corr_res = df1.corr()
			temp_df = df[1:15]		
			final_html = template.s1 + " <br><br> Correlation Matrix <br> "+ corr_res.to_html() + "<br><br></div>"
			return final_html
		except:
			final_html = template.s1 + """ <br><br><font color="lightcoral"> Error. Please try again </font><br><br></div>""" + df[1:15].to_html()
			return final_html
  return 'helloo'

# Upload data file  
@app.route('/upload',methods=['GET','POST'])
@login_required
def upload():
  return render_template('upload.html')

#  
@app.route('/cart',methods=['GET','POST'])
def cart(file=None):
  return render_template('home.html')

#Function to save the global variables  
def save_global(user_id,df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html):
	#global df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html
	try:
	  temp_list=list()
	  temp_list.append(df)
	  temp_list.append(df_train)
	  temp_list.append(df_test)
	  temp_list.append(test_train_created)
	  temp_list.append(lin_model)
	  temp_list.append(log_model)
	  temp_list.append(log_reg_key)
	  temp_list.append(res_log)
	  temp_list.append(log_predict1)
	  temp_list.append(res_lin)
	  temp_list.append(lin_predict1)
	  temp_list.append(lin_reg_key)
	  temp_list.append(final_html)
	  file_nm = "global_vars" + user_id + ".txt"
	  f = open(file_nm,'wb')
	  pickle.dump(temp_list,f)
	  f.close()
	except:
	  if(not(f.closed)):
		f.close()	
	return

#Function to read the global variables  
def read_global(user_id):
  #global df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html
  df = DataFrame()
  df_train = DataFrame()
  df_test = DataFrame()
  origin_df = DataFrame()
  test_train_created = False
  final_html = ""
  log_predict1 = DataFrame({'results':[]})
  lin_predict1 = DataFrame({'results':[]})
  log_model = ()
  lin_model= ()
  res_log = ()
  res_lin = ()
  log_reg_key = list()
  lin_reg_key = list()
  try:
	  temp_list=list()
	  file_nm = "global_vars" + user_id + ".txt" 
	  f = open(file_nm,'rb')
	  glob_list = pickle.load(f)
	  df = glob_list[0]	
	  df_train = glob_list[1]
	  df_test = glob_list[2]
	  test_train_created=glob_list[3]
	  lin_model=glob_list[4]
	  log_model=glob_list[5]
	  log_reg_key=glob_list[6]
	  res_log=glob_list[7]
	  log_predict1=glob_list[8]
	  res_lin=glob_list[9]
	  lin_predict1=glob_list[10]
	  lin_reg_key=glob_list[11]
	  final_html=glob_list[12]
	  f.close()
  except:
	  if(not(f.closed)):
		f.close()
	  return(df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
  return(df,df_train,df_test,test_train_created,lin_model,log_model,log_reg_key,res_log,log_predict1,res_lin,lin_predict1,lin_reg_key,final_html)
# Check-box function to display the list of columns in the form of Check-box  
def create_checkbox(k,func):
  temp_count = 0	
  if(func == "remove"):
	check_html = "<br><b><u> Select list of variables from below to remove </u></b><br><br>" + template.check1
  elif(func == "cond"):
	check_html = "<br><b><u> Select a variable from below to create Dummy variable (only continuous variables) </u></b><br><br>" + template.check4
  elif(func == "variable_dist"):
	check_html = "<br><b><u> Select list of variables from below to see distribution </u></b><br><br>" + vardist.check1
  elif(func == "date_dist"):
	check_html = "<br><b><u> Select a date column from below to see distribution </u></b><br><br>" + vardist.check4
  elif(func == "vif"):
	check_html = "<br><b><u> Select list of variables  from below to calculate VIF </u></b><br><br>" + vif1.check1
  elif(func == "categorical"):
	check_html = "<br><b><u> Select columns  from below to be declared as categorical </u></b><br><br>" + categ.check1
  elif(func == "chi_square"):
	check_html = "<br><b><u> Select 2 variables from below to perform Chi-square test </u></b><br><br>	" + chisqrt.check1
  elif(func == "crosstab"):
	check_html = "<br><b><u> Select 2 variables from below to perform Cross Tabulation </u></b><br><br>	" + crosstab.check1
  elif(func == "missing_value"):
	check_html = "<br><b><u> Select columns from below to be treated for missing values </u></b><br><br>" + treat1.check1
  elif(func == "correlation"):	
	check_html = "<br><b><u> Select 2 or more variables from below to be used to create correlation matrix </u></b><br><br>" + corr1.check1
  elif(func == "outliers"):	
	check_html = "<br><b><u> Select a variables for outlier treatment </u></b><br><br>" + corr1.check4
  elif(func == "bin"):	
	check_html = "<br><b><u> Select columns from below to be binned (give the number of bins to be created </u></b><br><br>" + categ.check5
  elif(func == "dummy_variables"):	
	check_html = "<br><b><u> Select column on which dummy variables need to be created </u></b><br><br>" + categ.check7
  # Replace check box labels with actual data columns names
  for s in k:
	temp_check = template.check2
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"
  # Check for appropriate function before adding submit button
  if(func == "remove"):
	check_html = check_html + "<br>" + template.check3
  elif(func == "cond"):
	check_html = check_html + "<br>" + template.cond_submit
  elif(func == "variable_dist"):
	check_html = check_html + "<br>" + vardist.check3
  elif(func == "date_dist"):
	check_html = check_html + "<br>" + vardist.check5
  elif(func == "vif"):
	check_html = check_html + "<br>" + vif1.check3
  elif(func == "outliers"):
	check_html = check_html + "<br>" + corr1.cond_submit
  elif(func == "categorical"):
	check_html = check_html + "<br>" + categ.check4
  elif(func == "chi_square"):
	check_html = check_html + "<br>" + chisqrt.check3
  elif(func == "crosstab"):
	check_html = check_html + "<br>" + crosstab.check3
  elif(func == "missing_value"):
	check_html = check_html + "<br>" + treat1.check3
  elif(func == "correlation"):	
	check_html = check_html + "<br>" + corr1.check3
  elif(func == "bin"):	
	check_html = check_html + "<br>" + categ.check6
  elif(func == "dummy_variables"):	
	check_html = check_html + "<br>" + categ.check8  
  return check_html	
	
def create_reg_checkbox(k,reg_type):
  temp_count = 0
  if(reg_type == "linear"):
	check_html = linreg1.check1
  elif(reg_type == "logistic"):
	check_html = linreg1.check5
  check_html = check_html + "<br><br><b><u>Select Independent variables for the model</u></b><br><br><br>"		
#Displays the first checkbox to display the variables list for VIF  
  for s in k:
	temp_check = linreg1.check2
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"
  check_html = check_html + "<br><br><br><b><u>Select Dependent variables for the model</u></b></br><br>"		
  temp_count = 0
#Displays the second checkbox to select the DV for VIF	
  for s in k:
	temp_check = linreg1.check4
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"		
  if(reg_type == "linear"):
	check_html = check_html + "<br>" + linreg1.check3
  elif(reg_type == "logistic"):
	check_html = check_html + "<br>" + linreg1.check6
  return check_html
  
def create_treecheckbox(k):
  temp_count = 0
  check_html = tree1.check1
  check_html = check_html + "<br><br><b><u>Select Independent variables for the model</u></b><br><br><br>"	
#Displays the first checkbox to display the variables list for VIF  
  for s in k:
	temp_check = tree1.check2
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"
  check_html = check_html + "<br><br><b><u>Select Dependent variables for the model</u></b><br><br><br>"	
#Displays the second checkbox to select the DV for VIF		
  for s in k:
	temp_check = tree1.check4
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"		
  check_html = check_html + "<br>" + tree1.text1 + tree1.text2 + tree1.check3
  return check_html

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('signin'))
	
if __name__ == '__main__':
  app.run(debug=True,threaded=True)
