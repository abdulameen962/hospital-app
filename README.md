# Distinctiveness and Complexity
The hospital web app is an appointments making webapp of an hospital for patients to make appointments to see their doctors and also go to the hospital pharmacy 
to order for drugs and check them out and for doctors to be able to create appointments and track their appointments thereby making the interaction between a doctor and a patient easier. Every page is fully mobile responsive with both custom css(made with scss) and bootstrap.,vue js,django,vanilla js and html. The features of my webapp below shows how distinct and complex my app truly is.

## The hospital web app is made up of two sides
* Patient
* Doctor

## Features of the webapp

#### Superadmin
1. The superadmin is in charge,he can see all databases on the website such as the users,patientinfos,doctor infos,patient appointments,doctor appointments,messages,deleted appointments,Skills,Pharmacy and Orders 

#### Background updates
1 There is an update appointments scripts checking for stale appointments,unattended appointments and sending the right message to the user and the doctor without reload of the page

2  A script checking and updating for new messages notifications of the user

3 A database available to the admin showing appointments that were not attended or no patient made the appointment before they expired (Deleted Appointments)

#### Default index page: 
1. It is visible to users that have not signed in or have logged out of the app
2. Contains the landing page section,about section,services and testimonials with a footer

#### Registration
1 Users can register either as a patient or as a doctor. Because it is a test app anyone can be a doctor

2 For a doctor there are additional fields such as skills and descriptions

3 General fields include: username,first name,last name,profile picture, email address,role and password

4 A verification link is sent to the user to verify his email,a one time link

5 If verification link has been used,using it again renders a failed page

6 A welcome email is also sent to the user on successful signup

### Login
1 Users on the login screen need to enter a username and a password and will be redirected to the appropiate dashboard

2 Users can also reset password and be sent a password verification link which is also one time

3 If password link has been used,using it again renders a failed page,with an option to resend

### Patient

1 Home page. It includes the following features:

* First loads the first 10 doctors,page has infinite scrolling feature to show new doctors
* An advanced search bar to search for doctors based on either names,skills or description
* Also to view details of each doctor,on it, user can add an available appointment of a doctor(if any) and also remove appointments he/she has made with the doctor

2 Appointments. It includes the following features:

* A table showing all the current appointments the user has made with the doctors
* An option to remove appointment with the doctor

3 Pharmacy. It includes the following features:
* A search bar to search for drugs both by name and description
* A reset search button option 
* Displays 10 drugs at first with pagination options
* Also an option to view the details of each drug
* On the details of each drug,user can view the description and prescription of the drug with an option of adding the drug to cart or to checkout the drug
* Incase the drug is already added,an option is also provided to remove it

4 Cart. It includes the following features:
* Shows all the drugs the user has added to the cart with an option to remove the drug
* Also a form to add/remove pieces from the cart

5 Profile. It includes the following features:
* Information about the user including name,username and the profile picture with a brief history of the activity of the Patient
* Showing ongoing appointments, completed appointments, drugs added to cart successful orders and failed/cancelled orders
* An option to change password of the user which sends a password verification link to the email
* An option to also edit profile

6 Edit profile. It includes the following features:
* Patient can change first and last name also profile picture

7 Messages. It includes the following features:
* Displays the first 15 messages with pagination
* Unread messages have a grey background
* An option to view the details of the message to see the body of the message which automatically marks the message as read
* Messages related to confirming appointments have an option to click that he/she attended an appointment or didn't

8 Logout: Patients can logout from the platform if signed in

### Doctor

1 Home page: It has the following features:
* It displays all the upcoming appointments the Doctor has showing the startdate,enddate and the user that made the appointment

2 Availability: It has the following features:
* Displays to the Doctor all the available dates of the doctor with an option to remove the availability
* An option to add new availability specifying the startdate and enddate and automatically updates the current appointments
* And all is done via apis without the reload of the page

3 Profile: It has the following features:
* Information about the user including name,username,description of the doctor and the profile picture,skills
* Showing ongoing patient appointments, created appointments and the completed appointments
* An option to change password of the user which sends a password verification link to the email
* An option to also edit profile

4 Edit Profile: It has the following features:
* Users can change first and last name also profile picture
* Also edit description and skills


## File Structure
1. On the hospital app, the following files and folders are included:
* The views.py file,showing the logic for each of the view functions on the web app
* Utils.py file,custom created by me for generating one time verification and password authentication links
* Urls.py showing all the urls and api urls on the app
* Models.py showing all the models created for my webapp,contains models with one to one relationships,many to many fields,foreign keys,etc
* Admin.py file showing all the databases registered(which was all of them) and edits and modifications to how they are seen by the admin
* The template folder containing 18 html pages including the layout,index page,patient home page,doctor home page,login,register,activattionfailed,pharmacy,reset password and so on
* The static folder contains all my css and js code with some vendor js like vue,splide.min.js,aos.js etc and my scss codes that I used in writing the styles.css and a package.json file used with node js command prompt to inteprete the scss code
* Static folder also contains images,a folder containing images uploaded by me for design purposes and not that uploaded by the users on the app
* And all other files automatically created by django during installation and initialization of the project

2 On the general folders: the following files and folders are included:
* Media folder,containing all images uploaded by the users
* The requirements.txt file showing all the modules installed on the environment with their versions
* manage.py file - created by django during installation
* the readme file to explain the project
* .gitignore file - to prevent vital information from showing
* And all other files automatically created by django during installation and initialization of the project

3 In the capstone folder,the following files are included:
* The settings.py showing all the settings of the app,and some custom modifications by me to send emails to user,set the timezeon
* .env file containing secret information used in the setting such as the sender email address,django secret key,the password used,email_port etc
* And all other files automatically created by django during installation and initialization of the project

# How to run the application

1 Install all the following modules and dependencies in requirements.txt file

2 Migrate the database

3 Run the server(*python manage.py runserver*)

