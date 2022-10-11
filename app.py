# Using flask to make an api
# import necessary libraries and functions
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from SpellCheck import load1stCluster, loadLastCluster, loadcharIndex, readForwardFSA, readReverseFSA, loadTrigramFreqHash, loadTrigramOpt, loadCiC, spellchk, split_chars,suggestionGeneration

#SSL Certificate Generation
# from OpenSSL import SSL
# context = SSL.Context(SSL.TLSv1_2_METHOD)
# context.use_privatekey_file('server.key')
# context.use_certificate_file('server.crt')


# Initial Loader
load1stCluster()
loadLastCluster()
loadcharIndex()
readForwardFSA()
readReverseFSA()
loadTrigramFreqHash()
loadTrigramOpt()
loadCiC()

# creating a Flask app
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, support_credentials=True)

# on the terminal type: curl http://127.0.0.1:5000/
# returns hello world when we use GET.
# returns the data that we send when we use POST.
@app.route('/', methods = ['GET', 'POST'])
@cross_origin(supports_credentials=True)
def home():
	if(request.method == 'GET'):

		data = "hello World"
		return jsonify({'data': data})


# A simple function to calculate the square of a number
# the number to be squared is sent in the URL when we use GET
# on the terminal type: curl http://127.0.0.1:5000 / home / 10
# this returns 100 (square of 10)
@app.route('/spellCheck/', methods=['GET'])
@cross_origin(supports_credentials=True)
def spellCheck():
    # words = request.form['text']
    words = request.args.get('words')
    errorWords = []
    if words:
        for word in words.split(' '):
            if spellchk(word) == 0:
                errorWords.append(word)
    return jsonify(errorWords)

@app.route('/suggestions/', methods=['GET'])
@cross_origin(supports_credentials=True)
def suggestions():
    # word = request.form['text']
    word = request.args.get('word')
    suggestions = []
    if word:
        if spellchk(word) == 0:
            suggestions = suggestionGeneration(split_chars(word))
    return jsonify(suggestions.split(','))



	


# driver function
if __name__ == '__main__':

	app.run(debug = True, ssl_context='adhoc', port=5000)
