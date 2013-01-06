EmotionDiaryPython
==================
An application for evaluating emotions on Facebook.

For now the code is simply hosted here and run on Heroku.

## Testing, Games & Tips
The application provides various means of engagement. 

## Points
Points are awarded for many tasks in the application. 

- Completing Scientific Surveys
- Learning about Depression
- Playing Games
- Inviting Friends
- Sharing to Facebook
- Posting feedback
- Using the App regularly

Points are used to increase the probability of winning rewards, a system communicated to users in terms of their chances to win things of varying values.

## How to Work on this Project (on a mac)

### Setting up your system
1. Install the [Github App](http://mac.github.com/)
2. Set up this source in a working directory on your computer
3. Install [Xcode from Apple App Store](http://itunes.apple.com/us/app/xcode/id497799835?ls=1&mt=12) and Comand Line Tools the from [Apple Developer Site](https://developer.apple.com/downloads/index.action)
4. Set up a Python Virtual Environment (do not do this in the repository on your computer, use the folder your repository is inside or another folder in your system to store the virtual environment)
5. Install Heroku
6. Install Flaks
5. Set up DB

### Editing Code
1. In terminal, set up your working environment and navigate to the project folder
2. Open the project folder in SublimeText by running `subl .` in the terminal
2. Open utilities.py and make sure `DEBUG = True` (this means you will be accessing a local DB and a different Facebook app)
2. Launch the app from the terminal with `python app.py` it will now be running at  [`0.0.0.0:5000`](http://0.0.0.0:5000). 
2. Make edits and save changes. It will update imediatly, however, every time you save one of the python files, return to [`0.0.0.0:5000`](http://0.0.0.0:5000) to see the cahnges (because it need to redo the login).

### More Reading
* [The Hichicker's Guide to Python](http://docs.python-guide.org/en/latest/)
* [Flask Tutorial](https://github.com/jakecoffman/flask-tutorial)
* [Getting Started with Python on Heroku](https://devcenter.heroku.com/articles/python)
* [Flask and PostgreSQL on Heroku](http://blog.y3xz.com/blog/2012/08/16/flask-and-postgresql-on-heroku/)
* [Getting the most out of Sublime Text](https://tutsplus.com/course/improve-workflow-in-sublime-text-2/) - This has a few mistakes, so if you are wondering why something does not work, let me know.