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
</div>
<div style="float:right;">
"""

check1 = """<form action="/vardis1" method="POST" enctype="multipart/form-data">"""

check2 = """
<input type="checkbox" name="list_val" value="list_val">list_val<br>
"""

check3 = """<input type="submit" name="Dispchart" value="Display Details"/></form>"""