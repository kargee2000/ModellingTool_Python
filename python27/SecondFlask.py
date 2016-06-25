
# coding: utf-8

# In[2]:
from flask import Flask, render_template, request, redirect 

app = Flask(__name__)

#@app.route('/hello/')

@app.route('/hello/<name>',methods=['GET','POST'])
def home(name=None):
	print 'Hi'
    #return render_template('hello.html')
	return render_template('home.html',name=name)
	
#if __name__ == '__main__':
app.run(debug=True)
# In[ ]:



