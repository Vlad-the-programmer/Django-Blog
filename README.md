
# (resume_website):

## Django Personal Blog Project ✨
A full-featured blog platform with user authentication, social login, post management, and admin controls—built with Django.


🚀 Key Features
👥 User Features
✅ Authentication: Register, Login, Logout

📧 Email Confirmation: Account activation & password reset

🌐 Social Login: Google, Facebook (via allauth)

📝 Profile Management: CRUD operations for user profiles

🔍 Post Discovery:

Filter posts by categories or custom fields

Search functionality

💬 Interactions:

Leave reviews/comments (CRUD)

View other users’ profiles

⚙️ Admin Features
✏️ Post Management: Full CRUD for posts

🏷️ Category Management: CRUD for categories

🔧 Technical Highlights
Custom User Model: AbstractUser + UserManager

Social Auth: Custom AccountAdapter for social logins

Email Handling: Custom email service for activation

Database Relations:

Many-to-Many: Posts ↔ Tags

UI/UX:

Pagination

crispy_forms + bootstrap5 for sleek forms

Admin Panel: Customized with Jazzmin

Advanced Features:

Django signals

Custom permissions

FilterSet for dynamic queries

Context processors for global template vars

🛠️ Technologies/Libraries
Backend	Django, Python
Auth	allauth (social + email)
UI	    crispy_forms, crispy_bootstrap5
Filters	django_filters
Misc	django_countries, Jazzmin


![image1](https://github.com/Vlad-the-programmer/Django-Blog/blob/main/resume_website/Screenshots/image1.png?raw=true)

![image2](https://github.com/Vlad-the-programmer/Django-Blog/blob/main/resume_website/screenshots/image2.png?raw=true)

![image3](https://github.com/Vlad-the-programmer/Django-Blog/blob/main/resume_website/screenshots/image3.png?raw=true)

![image4](https://github.com/Vlad-the-programmer/Django-Blog/blob/main/resume_website/screenshots/image4.png?raw=true)

# (resume_website_restapi):

## Django Blog REST API 🔥
A RESTful API version of the Django Blog project with JWT authentication, social login, and full CRUD operations.

🌟 Key Features
✅ All features from the original Django Blog
🔐 JWT Authentication (Token-based access)
⚡ Dual View Types:

Class-Based Views (CBV)

Function-Based Views (FBV)
🌐 Social Auth: Google/Facebook login via allauth
🚨 Custom API Exceptions (Structured error handling)

🛠️ Technologies/Libraries
Backend	DRF, Python
Auth	allauth (social + email)
Filters	django_filters
Misc	django_countries, Jazzmin




