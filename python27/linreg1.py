# For linear regression
check1 = """<form action="/linreg2" method="POST" enctype="multipart/form-data">"""

check2 = """
<input type="checkbox" name="list_val" value="list_val">list_val
"""

check4 = """
<input type="radio" name="DV" value="list_val">list_val
"""

check3 = """<input type="submit" name="lin_reg1" value="Build Model on Train data"/><input type="submit" name="lin_reg2" value="Build Model on full data"/></form>"""


# For Logistic regression

check5 = """<form action="/logreg2" method="POST" enctype="multipart/form-data">"""

check6 = """<input type="submit" name="log_reg1" value="Build Model on Train data"/><br><br><input type="submit" name="log_reg2" value="Build Model on full data"/><br></form>"""