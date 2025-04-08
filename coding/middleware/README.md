This is a guide for setting up your own virtual environments for middleware. It's adviced to READ THIS GUIDE ALONG WITH GPT HELP.
NOTE: Any commands included in this guide might be machine/OS-specific. Make sure to check for which commands work for you.

---------------

Step 1. Have Python 3 install on your machines (you probably already have it but still check).

Step 2. Install "python3-venv" package.
	- If you're using Ubuntu, run "sudo apt install python3-venv" on the command line. 
	- If you're using another OS, check how to do this on your own OS.
	- This package is needed to create virtual environments.

Step 3. Clone the project directory from GitHub (assuming everyone already did this).

Step 4. Enter into the project directory on the terminal.

Step 5. Go into coding/middleware/ on the terminal.

Step 6. Once you're inside CSCI3100-project/coding/middleware/ , run the command "python3 -m venv middleware_venv"
	- The command itself might differ based on your machine and OS, but make sure that you name the virtual environment as "middleware_venv". If you decide to name it something else, you will need to modify the .gitignore file as well, so just name is as "middleware_venv". 
	- This command will create a directory called "middleware_env" which is the virtual environment. Since this is included in the .gitignore file, git won't keep track of this. 

Step 7. After creating the virtual environment, you need to activate it. The command for Linux/macOS is "source middleware_venv/bin/activate".
	- Look up the specific command for your own machine and OS. 
	- After this command, you'll see that your terminal shows the name of the virtual environment in paranthesis like this: 
			(middleware_venv) $...
	- Every time you need to work on the middleware, go into CSCI3100-project/coding/middleware/ and activate the virtual environment, every time you're done with working on the middleware, deactivate the virtual environment by running the command "deactivate" or whatever you need to run for your specific machine/OS.

Step 8. You'll see that there is a file called "requirements.txt" under CSCI3100-project/coding/middleware/ . This file includes all the dependencies needed for the middleware. Before running the middleware, you need to install these dependencies. The command to install these dependencies is "pip install -r requirements.txt". 
	- Check if the command differs for your machine/OS. 

Step 9. Set the FLASK_APP environment variable to "middleware_app.py" as this is the file that needs to be run when we run flask. The command I used was "export FLASK_APP=middleware_app.py" . Check which command works for you. 
	- After running the command, you can check if it worked by the command "echo $FLASK_APP". It should return "middleware_app.py".
	- Set the Flask envrionment variable, if needed. E.g. "export FLASK_ENV=development".

Step 10. After these steps, you have set your virtual environment, installed necessary dependencies, and specified which program should run when you run Flask. When you type the command "flask run", it will start the Flask server at "http://127.0.0.1:5000" (this address will be specified when you run "flask run" as well). You can go to your web browser, copy-paste this address, and you'll see the Flask server running.

Step 11. When you're done with all these steps, deactivate the virtual environment. This will return you to your system's default Python environment.

NOTE: To check if git is ignoring your virtual environment, run "git status". If the virtual environment shows up, look for ways to make it so that it doesn't show up. DO NOT COMMIT THE VIRTUAL ENVIRONMENT. After setting up the virtual environment, unless you made any changes to any other files like requirements.txt or .gitignore, YOU DO NOT NEED TO PUSH ANYTHING.

NOTE: If you need to install other Python packages when you're working on the middleware, you can do this by the command "pip install <package-name>" (assuming virtual environment is already active since you're working on the middleware). If you install any Python packages, be sure to update requirements.txt file. You can do this by running the command "pip freeze > requirements.txt". After doing this, push the updated requirements.txt to GitHub and specify that you updated the file so that next time, when other teammembers are working on the middleware, they can update the dependencies intalled in their virtual envrionment by running "pip install -r requirements.txt".

NOTE: All the coding must be in coding/middleware/ and not in the virtual environment directory.

NOTE: Each team member should create and configure their middleware virtual environment locally. That's why we don't push it on GitHub.

Thanks for reading the guide until this point. I hope it was helpful. I figured out all this by chatting with ChatGPT for an hour, so I wanted to prepare this guide so that y'all can save some time. You can and should still use GPT when in doubt.

