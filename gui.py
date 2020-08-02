from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
import asyncio
from client_calls import *

app = Flask(__name__)


@app.route('/register')
def registration:
	return render_template('registration.html')

@app.route('/')
def login():
    return render_template('login.html')

if __name__ == "__main__":
    app.run()
