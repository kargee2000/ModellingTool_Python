from flask import Flask, render_template, request, redirect
import numpy as np
import pandas as pd
from pandas import DataFrame
 
app = Flask(__name__)      
 
@app.route('/',methods=['GET','POST'])
def home():
  #print request.method
  if request.method == 'POST':
   # f = request.files['myfile']
    return redirect('/cart')
  return render_template('index.html')

@app.route('/recieved',methods=['GET','POST'])
def rec():
  return 'recieved'

@app.route('/cart',methods=['GET','POST'])
def cart():
  #return 'Hello'
  #return request.file['myfile']
  df = pd.read_csv("E:/Default_On_Payment_CHAID.csv");
  df = df[1:10]
  s = df.to_html()
  return render_template('home2.html',s=s)
  
if __name__ == '__main__':
  app.run(debug=True)



