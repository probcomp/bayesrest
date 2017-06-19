from flask import Flask, request

@app.route("/analyze", methods=['GET', 'POST'])
def analyze():
	print(request.json)

# https://www.getpostman.com/apps