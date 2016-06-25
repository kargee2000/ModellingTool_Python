
check1 = """<form action="/corr2" method="POST" enctype="multipart/form-data"><select name="correl" multiple>"""

check2 = """
<input type="checkbox" name="list_val" value="list_val">list_val   
"""

check3 = """</select><input type="submit" name="corr1" value="Find correlation function"/><br></form>"""

# Variables for outlier treatment
check4 = """<form action="/outtr2" method="POST" enctype="multipart/form-data"><select name="outlier" multiple>"""

#submit button for Dummy variable based on condition 
cond_submit = """</select><select name="func">
  <option value="greater than">greater than</option>
  <option value="less than">less than</option>
</select><br><br>Lower Value<input type="text" name="lower_val" id="lower1" value="0"/><br><br>
<input type="submit" name="outl1" value="Move Outliers to Mean"/><br><br><input type="submit" name="outl2" value="Remove outliers"/><br></form>"""