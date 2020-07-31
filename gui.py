from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
import asyncio
from client_calls import *

loop = asyncio.get_event_loop

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template('login.html')


if __name__ == "__main__":
    app.run()

loop.run_until_complete(<client call>)
