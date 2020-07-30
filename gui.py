from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template('login.html')


if __name__ == "__main__":
    app.run()
