import os

from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import pymongo
import json
from flask_cors import CORS


myclient = pymongo.MongoClient("mongodb+srv://Hacks:Wisconsin@moviematch.przvx4d.mongodb.net/?retryWrites=true&w=majority") # cluster
db = myclient["MovieMatch"] # database
users = db["users"] # users collection (aka users table)
likedcluster = db["liked"] # liked collection (aka liked table)


# Configure application
app = Flask(__name__)
CORS(app)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    # Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        data = request.get_json(force=True)
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirmPassword')
        # Make sure username is not empty
        if not username:
            return json.dumps({"err": "no username"}), 400
        
        # make sure username is unique
        myquery = {"username": username}
        queryResult = list(users.find(myquery))
        if len(queryResult) != 0:
            return json.dumps({"err": "Username taken"}), 400
        
        # Make sure passwords and confirm password match
        if password != confirm_password:
             return json.dumps({"err": "passwords don't match"}), 400
             # add user and hashed password to the database
        user = {
              "username": username,
              "password": generate_password_hash(password)
        }

        users.insert_one(user)
        session["username"] = user['username']
        return json.dumps({"user": username}), 200

@app.route("/login", methods=["GET","POST"])
def login():
    # gets posted data
    data = request.get_json(force=True)
    username = data.get('username')
    enteredPassword = data.get('password')

    # gets actual username and password from the database
    myquery = { "username": username}
    queryResult = list(users.find(myquery))
    if len(queryResult) == 0:
        return json.dumps({"err":"user not found"}), 400
    
    user = queryResult[0]
    correctPassword = user['password']

    # Checks to see if passwords match
    if check_password_hash(correctPassword,enteredPassword):
        session["username"] = user['username']
        return json.dumps({"user": username}), 200
    else:
        return json.dumps({"err": "incorrect password"}), 400

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return json.dumps({"msg": "Logged out successfully"}), 200

@app.route("/match", methods=["GET", "POST"])
def match():
    data = request.get_json(force=True)
    friend = data.get('friend')
    friends = data.get('friends')

    alreadyafriend = False
    # Checks if the friend is already added
    for i in friends:
        curr_friend = i["name"]
        if curr_friend == friend:
            alreadyafriend = True
            break

    if alreadyafriend:
        return json.dumps({"err": "Already a friend"}), 500

    # Checks if friend is found in the database
    myquery = {"username": friend}
    queryResult = users.find(myquery)
    queryResultList = list(queryResult)
    # id = "none"
    for i in queryResultList:
         id = i
    # # for i in queryResult:
    #     id = i.get("_id")
    # db_friend = queryResult[0]
    # name = db_friend['username']d
    # id = db_friend['_id']
    if len(queryResultList) == 1:
        return json.dumps({"friend": friend , "id": str(id['_id'])}), 200
    else:
        return json.dumps({"err": "This person is not registerd"}), 500



@app.route("/liked", methods=["POST"])
def liked():
    # parse data
    data = request.get_json(force=True)
    movieID = data.get('movieId') # integer
    usernamee = data.get('user')   
    
    # Check if the movie was already liked
    myquery = {"username": usernamee, "Movie": movieID}
    queryResult = likedcluster.find(myquery) # iterable object (check above for the implementation)
    if len(list(queryResult)) > 0:
        return json.dumps({"err": "This person is not registerd"}), 500


    # add to the liked collection: {"username": username, "id", id}
    movie = {
              "username": usernamee,
              "Movie": movieID
        }
    likedcluster.insert_one(movie)
    return json.dumps({"message": "Liked"}),200

@app.route("/getMatches", methods=["POST"])
def getmatches():
    # parse data
    data = request.get_json(force=True)
    movieID = data.get('movieId') # integer
    friends = data.get('friends') # list of dictionaries (each dictionary is one friend)
    usernamee = data.get('user')  
    
    # query the database to get the list of movies like by the current user
    myquery = {"username": usernamee}
    queryResult = likedcluster.find(myquery) # iterable object (check above for the implementation)
    currUserLikedMovies = [] # list of movie ids the current person liked
    for i in queryResult:
        currUserLikedMovies.append(i["Movie"])
        # return str(queryResult)
        
        
    friendsMatchTracker = {} # the dictionary which holds all the users and their movies
    # return a list of dictionaries with the matches movies for each friend
    for i in friends:
        currFriendName = i["name"]
        matchedMovies = []

        # get list of movies of current friend that we are checking
        # return currFriendName
        newmyquery = {"username": currFriendName}
        newqueryResult = likedcluster.find(newmyquery) # iterable object (check above for the implementation)
        UserLikedMovies = [] # list of movie ids the current person liked
        for j in newqueryResult:
            UserLikedMovies.append(j["Movie"])
            #return str(newqueryResult)

        # find matched movies
        for k in currUserLikedMovies:
            if k in UserLikedMovies:
                matchedMovies.append(k)

        friendsMatchTracker[currFriendName] = matchedMovies

    return friendsMatchTracker, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)