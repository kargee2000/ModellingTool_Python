from flask import Flask, render_template, request
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
    conn_df = DataFrame({'parent':[],'child':[]})
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
  elif (var == 'restore'):
	df = pd.read_csv("E:/test2.csv")
	s = "<br><br>" + df[1:15].to_html()
	final_html = template.s1 + "</div>" + s
	return final_html
  # Create Check-box	to display variables for binning
  elif (var == 'bin1'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"bin")
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
# Create Check-box for Dependent and Independent Variables for Decision tree
  elif (var == 'tree'):
	coln = list(df.columns.values)
	k = create_treecheckbox(coln)
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
# Removing variables from data
  elif (var == 'remove'):
	print "Kargee"
	coln = list(df.columns.values)
	k = create_checkbox(coln,"remove")
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
  #Function called after selecting variables from Check-box to be removed	
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
  # Create checkbox for dependent and independent variables for Linear Regression		
  elif (var == 'linreg'):
	coln = list(df.columns.values)
	k = create_linreg_checkbox(coln)
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html	
  # Create checkbox to select variables to be declared as categorical	
  elif (var == 'categ'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"categorical")
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
  # Create Check-box to select variables to view distribution	
  elif (var == 'vardis'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"variable_dist")
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
  # Create check-box to select variables to declare as dummy	
  elif (var == 'dumm'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"dummy_variables")
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
  # Create checkbox to select variables for chi-square
  elif (var == 'chisq'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"chi_square")
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
  # Create checkbox to select variables for missing value treatment	
  elif (var == 'treat'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"missing_value")
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html
  # Create check-box to select variables for correlation test	
  elif (var == 'corr'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"correlation")
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1  + k + "</div>" + s
	return final_html
  # Create checkbox to select variables to test for VIF	
  elif (var == 'vif'):
	coln = list(df.columns.values)
	k = create_checkbox(coln,"vif")
	temp_df = df[1:15]
	s = "<br><br>" + temp_df.to_html()
	final_html = template.s1 + k + "</div>" + s
	return final_html	
  return render_template('index.html')

#Function gets called on clicking on Categorical variable creation link  
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

#Function gets called on clicking on Varaible Distribution link  
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

#Function gets called on clicking on Chi-Square function link. For now this calls chi-square for only two variables - a DV and IDV  
@app.route('/chisq1',methods=['GET','POST'])
def chisq1():
  global final_html
  global df,origin_df
  chi_key = list()
  if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
		for key1 in Listkey1:
			if(key1 <> "Display Details"):
				chi_key.append(key1)
		ctab = pd.crosstab(df[chi_key[0]],df[chi_key[1]])	
		fit =  scipy.stats.chi2_contingency(ctab)
		temp_df = df[1:15]		
		final_html = template.s1 + "</div> <br><br> Chi-Square Test <br> p-value : "+ str(fit[1]) + "<br><br>" + temp_df.to_html()
		return final_html
  return 'helloo'

#Function gets called on calling Linear Regression link
@app.route('/linreg2',methods=['GET','POST'])
def linreg2():
  global final_html
  global df,origin_df
  lin_reg_key = list()
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
		Y = df[DV_lin_reg]
		linreg = linear_model.LinearRegression()
		fit1 = linreg.fit(df2,Y.values)
		s = fit1.coef_
		temp_df = df[0:15]	
		t = """</div><div style="float:right;"><br> Linear Regression Result <br>"""
		final_html = template.s1 + t + s + "</div><br><br><br>" + temp_df.to_html()
		return final_html
  return 'helloo'  

#Function gets called on clicking on Decision Tree creation link  
@app.route('/tree2',methods=['GET','POST'])
def tree2():
  global final_html
  global df,origin_df
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
		t = """</div><div style="float:right;"><br> Decision Tree result <br>"""
		final_html = template.s1 + t + k + "</div><br><br><br>" + temp_df.to_html()
		return final_html
  return 'helloo'  

#Function gets called on clicking on Missing value treatment link
@app.route('/treat2',methods=['GET','POST'])
def treat():
  global final_html
  global df,origin_df
  firstkey = False
  secondkey = False
  if request.method == 'POST':
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
		final_html = template.s1 + "</div><br>Null values were removed<br><br>" + temp_df.to_html()
		return final_html
  return 'helloo'  

# Function gets called on clicking VIF function link
@app.route('/vif2',methods=['GET','POST'])
def vif():
  global final_html
  global df,origin_df
  chi_key = list()
  if request.method == 'POST':
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
		final_html = template.s1 + "</div><br> VIF Results for selected variables <br>"+ vif_result + "<br>" + temp_df.to_html()
		return final_html
  return 'helloo'  

# Function called to bin variables. The columns checked will be binned
@app.route('/bin2',methods=['GET','POST'])
def bin2():
  global final_html
  global df,origin_df
  unique_count = 0
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
  if request.method == 'POST':
		Listkey1 = list(MultiDict(request.form).values())
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
				chi_key.append(key1)
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
def create_checkbox(k,func):
  temp_count = 0	
  if(func == "remove"):
	check_html = "<br><b><u> Select list of variables from below to remove </u></b><br><br>" + template.check1
  elif(func == "variable_dist"):
	check_html = "<br><b><u> Select list of variables from below to see distribution </u></b><br><br>" + vardist.check1
  elif(func == "vif"):
	check_html = "<br><b><u> Select list of variables  from below to calculate VIF </u></b><br><br>" + vif1.check1
  elif(func == "categorical"):
	check_html = "<br><b><u> Select columns  from below to be declared as categorical </u></b><br><br>" + categ.check1
  elif(func == "chi_square"):
	check_html = "<br><b><u> Select 2 variables from below to perform Chi-square test </u></b><br><br>	" + chisqrt.check1
  elif(func == "missing_value"):
	check_html = "<br><b><u> Select columns from below to be treated for missing values </u></b><br><br>" + treat1.check1
  elif(func == "correlation"):	
	check_html = "<br><b><u> Select 2 or more variables from below to be used to create correlation matrix </u></b><br><br>" + corr1.check1
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
  elif(func == "variable_dist"):
	check_html = check_html + "<br>" + vardist.check3
  elif(func == "vif"):
	check_html = check_html + "<br>" + vif1.check3
  elif(func == "categorical"):
	check_html = check_html + "<br>" + categ.check4
  elif(func == "chi_square"):
	check_html = check_html + "<br>" + chisqrt.check3
  elif(func == "missing_value"):
	check_html = check_html + "<br>" + treat1.check3
  elif(func == "correlation"):	
	check_html = check_html + "<br>" + corr1.check3
  elif(func == "bin"):	
	check_html = check_html + "<br>" + categ.check6
  elif(func == "dummy_variables"):	
	check_html = check_html + "<br>" + categ.check8  
  return check_html	
	
def create_linreg_checkbox(k):
  temp_count = 0
  check_html = linreg1.check1
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
 
if __name__ == '__main__':
  app.run(debug=True)



