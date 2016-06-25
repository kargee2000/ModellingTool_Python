s1 = """<html>
<head>
  <meta charset="UTF-8">
  <title>Model Builder - Main Page</title>
<style>
@import url(http://fonts.googleapis.com/css?family=Exo:100,200,400);
@import url(http://fonts.googleapis.com/css?family=Source+Sans+Pro:700,400,300);

body{
	margin: 0;
	padding: 0;
	background: #fff;
	position: absolute;
	top: calc(10% - 75px);
	left: calc(10% - 50px);
	background-color: gainsboro;
	height: 150px;
	width: 350px;
	padding: 10px;
	z-index: 2;
	color: #000000;
	font-family: 'Exo', sans-serif;
	font-size: 15px;
}
</style>
<script type="text/javascript">
function CheckFunc(val){
 var element=document.getElementById('lower1');
 if(val=='between')
   element.style.display='block';
 else  
   element.style.display='none';
}
</script>
</head>

<body>
<div class="body">
<form action="/upl" method="POST" enctype="multipart/form-data">
<br><br>
Click to upload Data File : <input type="file" name="myfile" /> <br><br>
             <input type="submit" name="submit" value="Submit"/><br>
</form>
</div>
<div class="body">
<a href="/restore" id="rest">Restore original data</a><br>
<a href="/view" class="hyp" id="rest">View Sample data (15 rows)</a><br>
<a href="/remove" id="one">Remove variables</a><br>
<a href="/bin1" id="bin1">Bin the variables</a><br>
<a href="/chisq" id="">Chi-square test</a><br>
<a href="/dumm" id="dumm">Create Dummy variables</a><br>
<a href="/tree" id="tree">Decision Tree</a><br>
<a href="/treat" id="miss">Treat missing values</a><br>
<a href="/corr" id="corr">Correlation Function</a><br>
<a href="/vardis" id="vardis">Variable Distributions</a><br>
<a href="/datedis" id="datedis">Date-field Distributions</a><br>
<a href="/cross" id="cross">Cross Tabulation</a><br>
<a href="/vif" id="">Variance inflation Factor(VIF) Test</a><br>
<a href="/outtr" id="">Outlier Treatment</a><br>
<a href="/cond" id="">Prepare Dummy variable on condition <small><small>(only Continuous variables)</small></small></a><br>
<a href="/testrain" id="testrain">Split into Test and Train data</a><br>
<a href="/linreg" id="">Linear Regression</a>
<a href="/lin_test" id="">         Predict on Test data</a><br>
<a href="/logreg" id="">Logistic Regression</a>
<a href="/log_test" id="">         Predict on Test data</a><br>
Export Results in CSV<a href="/export1" id="">Predicted Test data   </a>   
<a href="/export2" id="">  Prepared dataset</a><br>
<a href="/export3" id="">        Train data</a><br>
</div>
<div style="width:700px; height:700px; position:absolute; top: 20px; left:500px;">
"""

check1 = """<form action="/vardis1" method="POST" enctype="multipart/form-data">"""

check2 = """
<input type="checkbox" name="list_val" value="list_val">list_val
"""

check3 = """<input type="submit" name="Dispchart_categ" value="Display Categorical Distribution"/><br><input type="submit" name="Dispchart_cont" value="Display Continuous Distribution"/><br></form>"""

#Constants for date-field distributions
check4 = """<form action="/datedis1" method="POST" enctype="multipart/form-data">"""

check5 = """<input type="submit" name="Dispchart_categ" value="Display Date-fields distribution"/><br></form>"""
