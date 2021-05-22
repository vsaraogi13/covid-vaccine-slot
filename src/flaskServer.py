#!/usr/bin/env python3

from flask import Flask, request, jsonify
app = Flask(__name__)
@app.route('/otp', methods=['POST'])
def otp_receiver():
    otp = request.args.get('otp')
    print("OTP received is " + otp)
    f = open("otp.txt", "w")
    f.write(otp)
    f.close()
    response = jsonify(message="Job is Done!")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == '__main__':
    app.run()