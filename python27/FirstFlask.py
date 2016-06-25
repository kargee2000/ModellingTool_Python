
# coding: utf-8

# In[2]:

from flask import Flask, render_template, request, redirect
import kargee
 
app = Flask(__name__)      
 
@app.route('/',methods=['GET','POST'])
def home():
  print request.method
  if request.method == 'POST':
    f = request.files['myfile']
    return redirect('/recieved')
  return render_template('index.html')

@app.route('/recieved',methods=['GET','POST'])
def rec():
  return 'recieved'

if __name__ == '__main__':
  app.run(debug=True)


# In[ ]:



