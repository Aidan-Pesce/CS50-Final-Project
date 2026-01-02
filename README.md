
Link to Project Video: https://www.youtube.com/watch?v=YYztfp4uNPI - Title: CS50 Final Project - Ask Harvard


Firstly, the user should download the appropriate zip file (project.zip) and unzip it in VS Code. The project folder should contain 3 folders and 5 files:

Folders:
    flask_session (flask information)

    static (CSS styling)

    templates (html pages)

Files:
    app.py

    final.db - to view the structure, the user should cd into the file's directory and enter "sqlite3 final.db" in the terminal and then .schema to examine how different tables are connected

    helpers.py

    README.md

    DESIGN.md

Once the file has been unzipped, the user must open up the terminal, cd into the project folder, and run “flask run” as this program uses flask to operate. A link will appear, and the user should click on the link to open up the project page in their internet browser.

The first screen that will appear will be the Login screen. To view any posts, the user must first login, so the login page is the first screen that the user will see. However, if the user does not have an account, they should navigate to the “register” tab in the upper-right corner of the screen. After clicking on “register”, the user will be prompted to input a valid email address, a username, their password, and confirmation of their password. Once the user inputs all of this information, they must click the register button. After the user registers, it will bring them to the login screen, where the user must login using the username and password they just created. After this information has been input, they must click the login button.

Clicking the login button brings the user to the home page, and it changes the nav bar (the black bar at the top of the file). This gives the user access to the home page, the new post page, the profile page, as well as giving an option for the user to logout by clicking the “logout” link in the top right corner of the screen. This would direct the user back to the login screen, forcing them to register a new account or to login again.

Home Page

	The home page is where all of the post information is displayed and can be accessed by clicking on “CS50: Ask Harvard”. Each post shows the date that it was posted, the title of the post, the user who posted it, the message, as well as interactive like and dislike buttons, a load comment button, a comment button, and a text field to input a comment.

	With the like and dislike buttons, if the user clicks on one, it will turn blue to indicate that the user has either liked or disliked the post. If they wish to unlike/undislike the post, they must simply click the blue button to revert the thumbs up/thumbs down back to its original design.

	With the load comment button, the user should click this if they want to see any comments that exist for a post. If there are no comments for that post, nothing will appear. Otherwise, there will be a menu that expands below the button containing all of the comments for that post.

	With the comment button and the text field next to it, this is how the user adds a comment. The user must input a message in the text field, and then click where it says “Comment:” to post a comment otherwise an error is returned directing the user to input a message.

New Post Page

	If the user clicks on “New Post” at the top of the page, it will direct them to the New Post page. This page is where a user can add a post. First, there is an input field for the title of the post. Underneath that input field is a second input field with the placeholder “message”. This is where the message of the post should go. After both of these fields have been filled out, the user should click on the red “Make Post” button below the message input field. If the user has not filled out either field, clicking on this button will render an error message prompting the user to complete all fields.

Profile

	If the user clicks on the profile tab in the upper right corner of the screen, it will bring them to the profile page. This page displays the username of the logged-in user and all of the posts that user has. If the user has made a post, the user can interact with the page by clicking on one of their posts, and this will take them to that post back on the home page.

