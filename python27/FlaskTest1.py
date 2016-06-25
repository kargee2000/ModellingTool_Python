from flask import Flask, render_template, request, redirect, url_for
import numpy as np
import pandas as pd
from pandas import Series
from pandas import DataFrame
import template,categ,vardist,chisqrt,treat1,corr1,vif1,tree1,linreg1
from werkzeug.datastructures import MultiDict
import scipy.stats
import statsmodels.stats.outliers_influence as of
from sklearn import tree
from sklearn.externals.six import StringIO  
from StringIO import StringIO
from sklearn import linear_model

#This displays the various nodes in the tree on the HTML form. 
#It will take the Decision tree fit and return the HTML string to be printed on screen. This is still WIP
def build_tree_html(k,px_str,lpx,wpx,tpx,hpx):
    k1 = k.split(";")
    label_df = DataFrame({'label':[],'strin':[]})
    temp_conn_df = DataFrame({'parent':[],'child':[]})
    temp_conn_df2 = DataFrame({'parent':[],'child':[]})
    conn_df = DataFrame({'parent':[],'child':[]})
    temp_df = DataFrame({'label':["a"],'strin':["b"]})
    conn_list = list()
    row_count =0
    conn_count = 0
    label_nm = ""
    label_nm1 = ""    
    string_nm = ""
    temp_str = ""
    nodes = list()
    temp_kar = 0
    #For loop that reads the list and puts the lines into separate list and dataframe
    for i in k1:
        if(i.find("""label=""")>0):
            z = i.find("\n")
            i = i[z:]
            z = i.find("\n")
            i = i[z:]
            z = i.find("0")
            print "first I",i
            label_nm = str(i[1:3])
            print "label_nm",label_nm
            string_nm = str(i[3:len(i)])
            print "There",i
            #temp_df.ix[0,0] = label_nm
            #temp_df.ix[0,1] = string_nm
            
            label_df.ix[row_count,0] = label_nm.strip()
            label_df.ix[row_count,1] = string_nm
            #label_df.append(temp_df)
            row_count = row_count + 1
            #label_list()
        elif(i.find("->")>0):
            temp_str = str(i)
            nodes = temp_str.split("->")
            conn_df.ix[conn_count,0] = str(nodes[1]).strip()
            temp_str = str(nodes[0]).replace("\n","")
            conn_df.ix[conn_count,1] = str(temp_str).strip()
            conn_count = conn_count + 1            
            #conn_list.append(i)
        temp_kar = temp_kar + 1    
    #Read the dataframe and list and print out into string
    conn_dict = {}
    df_counter = 0       
    list_counter = 0
    string_nm1 = ""
    temp_str=""
    html_str=""
    temp_lpx = lpx
    temp_wpx = wpx
    temp_tpx = tpx
    temp_hpx = hpx
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

app = Flask(__name__)      
filename = "E:/test.csv" 

df = DataFrame()
origin_df = DataFrame()
final_html = ""

@app.route('/',methods=['GET','POST'])
def home1():
  return render_template('index.html')
  
@app.route('/<var>',methods=['GET','POST'])
def home(var):
  global final_html
  global df,origin_df
  #Upload the data file
  if (var == 'upl'):
	f = request.files['myfile']
	f.save('E:/test2.csv')
	df = pd.read_csv("E:/test2.csv")
	#Original Data frame
	origin_df = df
	#Take a subset of records to display as sample
	df1 = df[1:15]
	s = "<br><br>" + df1.to_html()
	# String in HTML form to be returned
	final_html = template.s2 +"""<div style="position: absolute; top: 150px; left:500px;">File Uploaded Successfully!!</div>"""+  s
	return final_html
  # This will restore the original data uploaded from CSV. All changes made in the functions will be lost
  elif (var == 'rest'):
	df = pd.read_csv("E:/test2.csv")
	s = "<br><br>" + df[1:15].to_html()
	final_html = template.s1 + "</div>" + s
	return final_html
  elif (var == 'bin1'):
	coln = list(df.columns.values)
	k = create_bincheckbox(coln)
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
  elif (var == 'tree'):
	coln = list(df.columns.values)
	k = create_treecheckbox(coln)
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
  elif (var == 'one'):
	coln = list(df.columns.values)
	k = create_checkbox(coln)
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
  elif (var ==	'four'):
	if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		df1=df
		for key1 in Listkey1:
			if(key1 <> "Remove"):
				df1 = df1.drop(key1,1)
		df = df1
		temp_df = df[1:15]	
		s = "<br><br>" + temp_df.to_html()
		return template.s1 + "</div>" + s
  elif (var == 'linreg'):
	coln = list(df.columns.values)
	k = create_linreg_checkbox(coln)
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html	
  elif (var == 'categ'):
	coln = list(df.columns.values)
	k = create_categcheckbox(coln)
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
  elif (var == 'vardis'):
	coln = list(df.columns.values)
	k = create_vardischeckbox(coln)
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
  elif (var == 'dumm'):
	coln = list(df.columns.values)
	k = create_dummcheckbox(coln)
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html	
  elif (var == 'chisq'):
	coln = list(df.columns.values)
	k = create_chisqcheckbox(coln)
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
  elif (var == 'treat'):
	coln = list(df.columns.values)
	k = create_treatcheckbox(coln)
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
  elif (var == 'corr'):
	coln = list(df.columns.values)
	k = create_corrcheckbox(coln)
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = corr1.s1 + k + "</div>" + s
	return final_html
  elif (var == 'vif'):
	coln = list(df.columns.values)
	k = create_vifcheckbox(coln)
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = corr1.s1 + k + "</div>" + s
	return final_html	
  return render_template('index.html')

@app.route('/categ1',methods=['GET','POST'])
def categ1():
  global final_html
  global df,origin_df
  print "Got IT"
  if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		df1 = df
		for key1 in Listkey1:
			if(key1 <> "Mark as Categorical"):
				df1[key1] = pd.Categorical.from_array(df1[key1]).labels
		df = df1
		temp_df = df[1:15]		
		final_html = template.s1 + "</div><br><br>" + temp_df.to_html()
		return final_html
  return 'helloo'
  
@app.route('/vardis1',methods=['GET','POST'])
def vardis():
  global final_html
  global df,origin_df
  count_val = ""
  print "Got IT2"
  if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		df1 = df
		for key1 in Listkey1:
			if(key1 <> "Display Details"):
				s = df1[key1].value_counts() 
				s = DataFrame(s)
				count_val = s.to_html() + count_val + "  "
		temp_df = df[1:15]		
		final_html = vardist.s1 + count_val + "</div><br><br>" + temp_df.to_html()
		return final_html
  return 'helloo'
  
@app.route('/chisq1',methods=['GET','POST'])
def chisq1():
  global final_html
  global df,origin_df
  chi_key = list()
  #count_val = ""
  #print "Got IT2"
  if request.method == 'POST':
		#print "DIV",dir(request)
		Listkey1 = list(MultiDict(request.form).values())
		df1 = df
		for key1 in Listkey1:
			if(key1 <> "Display Details"):
				#s = df1[key1].value_counts() 
				chi_key.append(key1)
				#s = DataFrame(s)
				#count_val = s.to_html() + count_val
		#df = df1
		#print "Hi there",chi_key[0],chi_key[1]
		ctab = pd.crosstab(df[chi_key[0]],df[chi_key[1]])	
		#print fit[0]
		fit =  scipy.stats.chi2_contingency(ctab)
		temp_df = df[1:15]		
		final_html = template.s1 + "</div> <br><br> Chi-Square Test <br> p-value : "+ str(fit[1]) + "<br><br>" + temp_df.to_html()
		return final_html
  return 'helloo'

@app.route('/linreg2',methods=['GET','POST'])
def linreg2():
  global final_html
  global df,origin_df
  lin_reg_key = list()
  firstkey = ""
  
  if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		Listkey2 = MultiDict(request.form)
		DV_lin_reg = Listkey2.get('DV')
		df1 = df
		for key1 in Listkey1:
			if(key1 <> "Build Linear Regression Model" and key1 <> DV_lin_reg):
				lin_reg_key.append(key1)
		df1 = df.loc[:,lin_reg_key]
		df2 = df1.values
		temp_count = 0
		Y = df[DV_lin_reg]
		linreg = linear_model.LinearRegression()
		fit1 = linreg.fit(df2,Y.values)
		s = fit1.coef_
		temp_df = df[0:15]	
		t = """</div><div style="float:right;"><br> Linear Regression Result <br>"""
		final_html = template.s1 + t + s + "</div><br><br><br>" + temp_df.to_html()
		return final_html
  return 'helloo'  

@app.route('/tree2',methods=['GET','POST'])
def tree2():
  global final_html
  global df,origin_df
  chi_key = list()
  firstkey = ""
  init_style_string = """<p style="position: absolute; font-size: 12px; top: <top>px; width: <width>px;  height: <height>px; left:<left>px; text-align: center;">tree_text_here</p>"""
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
		temp_count = 0
		Y = df[DV_tree]
		clf = tree.DecisionTreeClassifier()
		clf = clf.fit(df2,Y.values)
		dot_data = StringIO()
		tree.export_graphviz(clf, out_file=dot_data)
		k = dot_data.getvalue()
		k1 = k.split(";")
		left_px = 600
		width_px = 150
		top_px = 50
		height_px = 309
		s = build_tree_html(k,init_style_string,left_px,width_px,top_px,height_px)
		temp_df = df[0:15]	
		t = """</div><div style="float:right;"><br> Decision Tree result <br>"""
		final_html = template.s1 + t + k + "</div><br><br><br>" + temp_df.to_html()
		return final_html
  return 'helloo'  


@app.route('/treat2',methods=['GET','POST'])
def treat():
  global final_html
  global df,origin_df
  chi_key = list()
  firstkey = False
  secondkey = False
  if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		Listkey2 = MultiDict(request.form)
		df1 = df
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
		final_html = template.s1 + "</div><br>Null values were removed<br><br>" + temp_df.to_html()
		return final_html
  return 'helloo'  

@app.route('/vif2',methods=['GET','POST'])
def vif():
  global final_html
  global df,origin_df
  chi_key = list()
  firstkey = ""
  if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		Listkey2 = MultiDict(request.form)
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
		final_html = template.s1 + "</div><br> VIF Results for selected variables <br>"+ vif_result + "<br>" + temp_df.to_html()
		return final_html
  return 'helloo'  

# Function called to bin variables. The columns checked will be binned
@app.route('/bin2',methods=['GET','POST'])
def bin2():
  global final_html
  global df,origin_df
  unique_count = 0
  chi_key = list()
  firstkey = ""
  bin_val_fail = False
  if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		Listkey2 = MultiDict(request.form)
		bin_val = int(Listkey2.get('changeval'))
		for key1 in Listkey1:
			if(key1 <> "Bin the Columns" and key1 <> str(bin_val)):
				k3 = set(df[key1])
				unique_count = sum(1 for num in k3)
				if(unique_count <= bin_val):
					bin_val_fail = True
					break
				temp_bin_col = pd.qcut(df[key1],bin_val)
				temp_col_name = key1 + "_bin"
				df[temp_col_name] = Series(temp_bin_col.labels)
		temp_df = df[1:15]		
		if(bin_val_fail):
			final_html = template.s1 + "</div><br><br> Bin count is more than the number of categories in columns <br> " + temp_df.to_html()
		else:
			final_html = template.s1 + "</div><br>" + temp_df.to_html()
		return final_html
  return 'helloo'

# Dummy variables creation. The columns checked will be marked for dummy variables  
@app.route('/dumm1',methods=['GET','POST'])
def dumm():
  global final_html
  global df,origin_df
  unique_count = 0
  chi_key = list()
  firstkey = ""
  bin_val_fail = False
  if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		Listkey2 = MultiDict(request.form)
		for key1 in Listkey1:
			if(key1 <> "Generate Dummy Variables"):
				pref = "ind_" + key1
				dummies = pd.get_dummies(df[key1], prefix=pref)
				df = df.join(dummies)
		temp_df = df[1:15]		
		final_html = template.s1 + "</div><br>" + temp_df.to_html()
		return final_html
  return 'helloo'

# Function for correlation analysis. Correlation will be found for variables checked  
@app.route('/corr2',methods=['GET','POST'])
def corr():
  global final_html
  global df,origin_df
  chi_key = list()
  if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		df1 = df
		for key1 in Listkey1:
			if(key1 <> "Find correlation function"):
				#s = df1[key1].value_counts() 
				chi_key.append(key1)
				#s = DataFrame(s)
				#count_val = s.to_html() + count_val
		df1 = df.loc[:,chi_key]
		corr_res = df1.corr()
		temp_df = df[1:15]		
		final_html = template.s1 + "</div> <br><br> Correlation matrix <br> "+ corr_res.to_html() + "<br><br>" + temp_df.to_html()
		return final_html
  return 'helloo'

# Upload data file  
@app.route('/upload',methods=['GET','POST'])
def upload():
  
  return render_template('upload.html')

#  
@app.route('/cart',methods=['GET','POST'])
def cart(file=None):
  return render_template('home.html')

# Check-box function to display the list of columns in the form of Check-box  
def create_checkbox(k):
  temp_count = 0	
  check_html = template.check1
  for s in k:
	temp_check = template.check2
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"
  check_html = check_html + "<br>" + template.check3
  return check_html	
	
def create_vardischeckbox(k):
  temp_count = 0
  check_html = vardist.check1
  for s in k:
	temp_check = template.check2
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"
  check_html = check_html + "<br>" + vardist.check3
  return check_html	

def create_vifcheckbox(k):
  temp_count = 0
  check_html = vif1.check1
#Displays the first checkbox to display the variables list for VIF  
  for s in k:
	temp_check = vif1.check2
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"
#Displays the second checkbox to select the DV for VIF		
#  for s in k:
#	temp_check = vif1.check4
#	temp_check = temp_check.replace("list_val",s)
#	check_html = check_html + temp_check
#	temp_count = temp_count + 1
#	if ((temp_count % 4 ) == 0):
#		check_html = check_html + "<br><br>"		
  check_html = check_html + "<br>" + vif1.check3
  return check_html
  
def create_categcheckbox(k):
  temp_count = 0
  check_html = categ.check1
  for s in k:
	temp_check = categ.check2
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"
  check_html = check_html + "<br>" + categ.check4
  return check_html	

def create_linreg_checkbox(k):
  temp_count = 0
  check_html = linreg1.check1
  check_html = check_html + "<br><br><b>Select Independent variables for the model</b><br><br><br>"		
#Displays the first checkbox to display the variables list for VIF  
  for s in k:
	temp_check = linreg1.check2
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"
  check_html = check_html + "<br><br><br><b>Select Dependent variables for the model</b></br><br>"		
  temp_count = 0
#Displays the second checkbox to select the DV for VIF	
  for s in k:
	temp_check = linreg1.check4
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		print "inside"
		check_html = check_html + "<br>"		
  check_html = check_html + "<br>" + linreg1.check3
  return check_html
  
def create_treecheckbox(k):
  temp_count = 0
  check_html = tree1.check1
#Displays the first checkbox to display the variables list for VIF  
  for s in k:
	temp_check = tree1.check2
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"
#Displays the second checkbox to select the DV for VIF		
  for s in k:
	temp_check = tree1.check4
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br><br>"		
  check_html = check_html + "<br>" + tree1.check3
  return check_html

def create_chisqcheckbox(k):
  temp_count = 0
  check_html = chisqrt.check1
  for s in k:
	temp_check = chisqrt.check2
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"
  check_html = check_html + "<br>" + chisqrt.check3
  return check_html
  
def create_treatcheckbox(k):
  temp_count = 0
  check_html = treat1.check1
  for s in k:
	temp_check = treat1.check2
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"
  check_html = check_html + "<br>" + treat1.check3
  return check_html  
  
def create_corrcheckbox(k):
  check_html = corr1.check1
  temp_count = 0
  for s in k:
	temp_check = corr1.check2
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"
  check_html = check_html + "<br>" + corr1.check3
  return check_html  

def create_bincheckbox(k):
  temp_count = 0
  check_html = categ.check5
  for s in k:
	temp_check = categ.check2
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"
  check_html = check_html + "<br>" + categ.check6
  return check_html	

def create_dummcheckbox(k):
  temp_count = 0
  check_html = categ.check7
  for s in k:
	temp_check = categ.check2
	temp_check = temp_check.replace("list_val",s)
	check_html = check_html + temp_check
	temp_count = temp_count + 1
	if ((temp_count % 4 ) == 0):
		check_html = check_html + "<br>"
  check_html = check_html + "<br>" + categ.check8
  return check_html	
  
if __name__ == '__main__':
  app.run(debug=True)



