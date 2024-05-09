# Riki_Fox

Riki is the version that is modified to be executed from Ubuntu server. 
You can use PyCharm and command line tools to start the Flask/Wiki system with “python Riki.py”.
You can access the wiki [http://wiki440.ms2ms.com](http://wiki440.ms2ms.com).

## Configuration
    
1. Update CONTENT_DIR and USER_DIR in config.py. 
    * CONTENT_DIR should point to the directory where your `content' is located.
    * USER_DIR should point to the directory where your `user' is located.
2. When you want to use login, make PRIVATE = True in config.py. Remember you can use id "name" and password "1234".
3. Always use virtualenv and pip.
    * pip install -r requirements.txt

# Team Rules
Communicate frequently with team members, but if you encounter a serious issue inform the team leader ASAP (NO SURPRISES).

Follow and meet deadlines and milestones set as a team, in the event you will not meet your deadline inform the team leader ASAP and at least 24 hours in advance of the deadline.

Attend all weekly meetings, and inform the team leader ASAP and at least 24 hours in advance that you can not attend.

Make sure to inform the team leader before committing any changes to the 'main' branch of the GitHub repository.

# Requirements
As a user, I want to be able to create a User Account as to track my status on the site for any uploads or edits I make, so that I can keep up to date with my activity on the site.

As a user, I want to be able to track analytics on the site to be able to see popular results and figure out what the community is actively interested in, so that I can stay involved on the wiki community.

As a user, I want to be able to upload files and images and be able to access them, so that I can useful information to pages.

As a user, I want to be able to download files in different file formats and photos, so that I can retrieve information from pages.

As a user, I want some sort of search feature that will allow me quick and general access to the wiki's knowledge base

As a user, I want a more robust advanced search feature so I can search the pages based off of keywords, phrases, and users, so that it is easier for me to navigate between pages.
