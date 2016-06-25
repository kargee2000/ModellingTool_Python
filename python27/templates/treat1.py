s1 = """<title>Main Page</title> <div>
<form action="/upl" method="POST" enctype="multipart/form-data">
Upload file Hi there: <input type="file" name="myfile" /> <br/>
             <input type="submit" name="submit" value="Submit"/>
</form>
</div>
<div style="float:left;">
<a href="/one" id="one">Remove variables</a><br>
<a href="/two" id="two">Bin the variables</a><br>
<a href="/three" id="three">Perform CART on the data</a><br>
<a href="/treat" id="miss">Treat missing values</a><br>
<a href="/vardis" id="vardis">Variable Distributions</a><br>
<a href="/categ" id="">Select Categorical variables</a><br>
<a href="/chisq" id="">Chi-square test</a><br>
</div>
<div style="float:right;">
"""

check1 = """<form action="/treat" method="POST" enctype="multipart/form-data">"""

check2 = """
<input type="checkbox" name="list_val" value="list_val">list_val<br>
"""

check3 = """<input type="submit" name="treat1" value="Replace nulls,NAs with zeros"/><input type="submit" name="treat2" value="Custom: Enter values to replace"/></form>"""