# [InfoCrumbs](https://infocrumbs-9d4b700e944a.herokuapp.com/): Summarized insights. Personalized for you.

## Project Overview

InfoCrumbs is a sophisticated Django-based web application engineered to revolutionize how users consume digital content. In today's overwhelming information landscape, InfoCrumbs cuts through the noise by delivering **personalized news and articles**—or "crumbs"—directly tailored to individual interests and tiered subscription plans. This project showcases a robust backend data pipeline, dynamic content summarization, and a meticulously designed user experience, built with scalability and maintainability in mind.

A deployed version can be seen [here](https://infocrumbs-9d4b700e944a.herokuapp.com/)

---

## Table of Contents

1. [Features](#features)

2. [Technical Architecture & Stack](#technical-architecture--stack)

3. [Entity-Relationship Diagram (ERD)](#entity-relationship-diagram)

4. [Installation and Setup](#installation-and-setup)

    * [Prerequisites](#prerequisites)

    * [Cloning the Repository](#cloning-the-repository)

    * [Virtual Environment Setup](#virtual-environment-setup)

    * [Install Dependencies](#install-dependencies)

    * [Environment Variables](#environment-variables)

    * [Database Setup](#database-setup)

    * [Create Superuser](#create-superuser)

    * [Populate Initial Data](#populate-initial-data)

5. [Running the Application](#running-the-application)

    * [Development Server](#development-server)

    * [Running the Data Pipeline](#running-the-data-pipeline)

6. [Testing](#testing)

7. [Code Quality & Linting Reports](#code-quality--linting-reports)

8. [Wireframes](#wireframes)

9. [Screenshots](#screenshots)

10. [Future Improvements](#future-improvements)

11. [Contributing](#contributing)

12. [License](#license)

---

## Features

* **Intelligent Content Aggregation**: Automated integration with diverse external APIs (Finnhub, Spoonacular, Mediastack) to fetch a wide array of content, from financial insights and cutting-edge tech news to curated recipes.

* **Real-time Content Summarization**: Leveraging the Hugging Face Inference API, InfoCrumbs generates concise summaries for lengthy articles. This intelligent processing ensures users get essential information quickly, enhancing content digestibility.

* **Dynamic Data Pipeline (`pipeline` app)**: A custom-built, scheduled management command orchestrates the fetching, processing, and storage of content. This pipeline is designed for efficiency and extensibility, ensuring fresh "crumbs" are always available.

* **Granular User Preferences (`preferences` app)**: Users can define their specific interests by selecting preferred topics. The system intelligently manages these preferences, directly influencing the content delivered. Includes a responsive topic selection form.

* **Personalized User Profile**: A dynamic user profile page featuring AJAX-driven tabs for Subscriptions, Topic Preferences, Saved Crumbs, and Comment History, enhancing responsiveness and user experience.

* **Flexible Subscription Tiers**: A robust subscription model empowers tiered access (Basic, Premium) to content. This includes dynamic topic limits and exclusive content features, providing a scalable business logic foundation.

* **Secure User Authentication**: Full user registration, login, and profile management capabilities, ensuring a secure and personalized user journey, including email verification.

* **Email Notification System**: Comprehensive transactional email support for key user interactions:
    * **Welcome/Verification Emails**: Sent upon user registration (managed via `django-allauth`).
    * **Subscription Confirmation**: Automated emails sent upon successful subscription purchase/renewal.
    * **Subscription Expiry Reminders**: Proactive notifications sent when a subscription is nearing its end.
    * **Security Alerts**: Automated emails for critical account changes (e.g., password change).

* **"Troll-Proof" Comment System**: Implemented character limits (min/max) and refined form design for user comments to encourage constructive engagement.

* **Enhanced User Support Pages**: Dedicated **FAQ** and **Contact Us** pages for comprehensive user assistance. The Contact form allows users to directly email `infocrumbs.app@gmail.com`.

* **Dynamic Homepage CTA**: The main call-to-action button on the homepage intelligently adapts its text and destination based on the user's login and subscription status (e.g., "Join InfoCrumbs", "Upgrade to Premium", "Explore Crumbs").

* **Responsive UI & Neon Theme**: A meticulously designed, responsive user interface utilizing Bootstrap 5 and a custom neon-inspired theme, ensuring an engaging visual experience across all devices.

* **Dynamic Access Control**: Critical views and features, such as topic preference management and payment processing, are protected by intelligent redirects, ensuring only active, subscribed users can access privileged functionalities.

---

## Technical Architecture & Stack

InfoCrumbs is built upon a modern, modular Django architecture, prioritizing clear separation of concerns and maintainability.

* **Backend**: **Django (Python Web Framework)** - Chosen for its "batteries-included" approach, ORM capabilities, and strong community support, accelerating development while ensuring robust application logic.

* **Database**: **PostgreSQL (Recommended)** / SQLite (Development) - Provides reliable data storage, with flexibility for easy local setup (SQLite) and scalable deployment (PostgreSQL).

* **Email Service**: **Brevo (formerly Sendinblue)** - Utilized for reliable transactional email delivery (welcome, confirmations, reminders, security alerts).

* **Payment Gateway**: **Stripe** - Integrated for secure and seamless handling of subscription payments via webhooks.

* **External APIs**:

    * **Finnhub**: Utilized for real-time financial news, demonstrating integration with market data APIs.

    * **Spoonacular**: Integrates rich food and drink recipe content, showcasing versatility in content types.

    * **Mediastack**: Powers technology news aggregation, highlighting broad news fetching capabilities.

    * **Hugging Face Inference API**: A testament to advanced NLP integration for on-the-fly text summarization, tackling challenges like API timeouts for large text inputs.

* **Frontend**: Standard Django Templates (HTML, CSS, JavaScript) - Ensures a direct, efficient rendering pipeline for dynamic content, complemented by Bootstrap 5 for responsiveness.

* **Development Tools**: `pip` (Python package management), `Git` (version control), `pytest` (testing).

---

## Entity Relationship Diagram

For through explanation of Entity-Relationship Diagram (ERD)please refer to [ERD file](docs/ERD.md)

---

## Installation and Setup

Getting InfoCrumbs running locally is straightforward, emphasizing best practices for development environments.

### Prerequisites

* Python 3.9+

* `pip` (Python package installer)

* `Git`

### Cloning the Repository

Start by cloning the project to your local machine:

```
git clone 
```
[https://github.com/aziz-ibrahim/infocrumbs.git](https://github.com/aziz-ibrahim/infocrumbs.git)
```
cd infocrumbs
```

### Virtual Environment Setup

Isolate project dependencies using a virtual environment for a clean development experience:

```
python -m venv .venv
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

### Install Dependencies

Install all required Python packages:

```
pip install -r requirements.txt
```

### Environment Variables

Crucially, create a `.env` file in the project root (`infocrumbs/`) to store sensitive API keys and configuration. **This file is explicitly excluded from version control (`.gitignore`) for security.**

```
# .env example - Populate with your actual keys and settings
SECRET_KEY='your_django_secret_key_here'
DEBUG=True # Set to False for production deployments
DATABASE_URL='sqlite:///db.sqlite3' # Or your PostgreSQL connection string
FINNHUB_API_KEY='your_finnhub_api_key'
SPOONACULAR_API_KEY='your_spoonacular_api_key'
MEDIASTACK_API_KEY='your_mediastack_api_key'
HUGGINGFACE_API_KEY='your_huggingface_api_key'

# Email Service (Brevo/Sendinblue Example)
EMAIL_HOST_USER='your_brevo_account_email@example.com'
EMAIL_HOST_PASSWORD='YOUR_BREVO_SMTP_KEY_HERE'
DEFAULT_FROM_EMAIL='InfoCrumbs <noreply@your-verified-domain.com>' # Must be a verified sender in Brevo

# Stripe Webhooks (Crucial for payment confirmations)
STRIPE_WH_SECRET='whsec_your_stripe_webhook_secret' # From Stripe Dashboard

# Site URL (used for absolute URLs in emails, e.g., verification links)
SITE_URL='http://127.0.0.1:8000' # Change to your production domain for deployment (e.g., https://www.infocrumbs.com)

# Add any other environment-specific variables here
```

### Database Setup

Initialize the database schema by applying migrations:

```
python manage.py migrate
```

### Create Superuser

Set up an administrative account to access the Django admin panel and manage initial data:

```
python manage.py createsuperuser
```

### Populate Initial Data

For the application to function, essential **Subscription Plans** and **Topics** must be pre-populated. You can do this via the Django admin interface:

* Create two `SubscriptionPlan` entries: one named `'basic'` with `topic_limit=2`, and one named `'premium'` with `topic_limit=12`.

* Create `Topic` entries (e.g., 'Finance', 'Food & Drink', 'Technology') ensuring their slugs match the `topic_slug` values used in the API handlers (e.g., `stock-crypto-finance`, `food-and-drink`, `technology`).

---

## Running the Application

### Development Server

Launch the Django development server:

```
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000/`.

### Running the Data Pipeline

To initiate content fetching and processing from the integrated APIs, execute the custom management command:

```
python manage.py fetch_crumbs
```

This command runs the `pipeline` app's tasks, populating your database with fresh, summarized content.

### Automated Tasks (Heroku Scheduler)

In a production environment, InfoCrumbs leverages Heroku Scheduler to automate critical background tasks, ensuring data freshness and timely user communication. The following management commands are scheduled to run daily:


```
python manage.py fetch_crumbs
```
* Purpose: Fetches, processes, and summarizes new content from external APIs.

* Schedule: Daily at midnight UTC.

```
python manage.py send_subscription_reminders
```
* Purpose: Dispatches subscription expiry reminder emails to users whose subscriptions are nearing their end.

* Schedule: Daily at 09:00 UTC.

These automated tasks ensure the application's content is always up-to-date and users are kept informed without manual intervention.

---

## Testing: A Commitment to Quality

InfoCrumbs boasts a comprehensive test suite covering models, forms, views, and critical business logic. This rigorous approach ensures code reliability, prevents regressions, and validates expected system behavior across various user scenarios and subscription states. Our iterative development process, including tackling complex issues like multi-hop redirects, dynamic form validation, and email sending, has significantly strengthened the application's stability.

For detailed instructions on running the test suite and reviewing coverage, please consult the dedicated [TESTING.md](docs/TESTING.md) document.

---

## Code Quality & Linting Reports

*(Placeholder for evidence of adherence to coding standards and best practices.)*

* **PEP 8 Compliance (Python)**:
A comprehensive review of all Python files within the project was conducted using Code Institute's PEP 8 linter tool. The detailed report, including screenshots of the linter output for each file, is available below, demonstrating a strong commitment to Python's style guide.
    * [View PEP 8 Compliance Report (PDF)](docs/infocrumbs-pep8-check.pdf)

* **JavaScript Linting (JSHint)**:
All JavaScript files have been thoroughly checked for quality and adherence to best practices using JSHint. The comprehensive report, including linter output, is provided to ensure robust and maintainable frontend scripting.

    * [View JSHint Compliance Report (PDF)](docs/infocrumbs-jshint-report.pdf)

* **HTML/CSS Markup Checks**:

    * [Link to HTML/CSS validation reports if available]

---

## Wireframes
The application's design process began with detailed wireframes, outlining the layout and user flow for all pages across different device sizes (small, medium, and large). These visual blueprints guided the development of the responsive user interface.

* [View Wireframes (PDF):](docs/infocrumbs-wireframes.pdf)

---
## Screenshots

Below are screenshots demonstrating the application's key features and responsive user interface across various screen sizes.

* **Home Page**:
    * Small: ![Home Page (Small)](docs/home-sm.png)
    * Medium: ![Home Page (Medium)](docs/home-md.png)
    * Large: ![Home Page (Large)](docs/home-lg.png)

* **About Page**:
    * Small: ![About Page (Small)](docs/about-sm.png)
    * Medium: ![About Page (Medium)](docs/about-md.png)
    * Large: ![About Page (Large)](docs/about-lg.png)

* **Contact Page**:
    * Small: ![Contact Page (Small)](docs/contact-sm.png)
    * Medium: ![Contact Page (Medium)](docs/contact-md.png)
    * Large: ![Contact Page (Large)](docs/contact-lg.png)

* **FAQ Page**:
    * Small: ![FAQ Page (Small)](docs/faq-sm.png)
    * Medium: ![FAQ Page (Medium)](docs/faq-md.png)
    * Large: ![FAQ Page (Large)](docs/faq-lg.png)

* **Sign Up Page**:
    * Small: ![Sign Up Page (Small)](docs/profile-sm.png)
    * Medium: ![Sign Up Page (Medium)](docs/profile-md.png)
    * Large: ![Sign Up Page (Large)](docs/profile-lg.png)

* **Profile Page**:
    * Small: ![Profile Page (Small)](docs/profile-sm.png)
    * Medium: ![Profile Page (Medium)](docs/profile-md.png)
    * Large: ![Profile Page (Large)](docs/profile-lg.png)

* **Crumbs List Page**:
    * Small: ![Crumbs List Page (Small)](docs/list-sm.png)
    * Medium: ![Crumbs List Page (Medium)](docs/list-md.png)
    * Large: ![Crumbs List Page (Large)](docs/list-lg.png)

* **Crumbs Detail Page**:
    * Small: ![Crumbs Detail Page (Small)](docs/detail-sm.png)
    * Medium: ![Crumbs Detail Page (Medium)](docs/detail-md.png)
    * Large: ![Crumbs Detail Page (Large)](docs/detail-lg.png)

* **Subscription Plans Page**:
    * Small: ![Subscription Plans Page (Small)](docs/plan-sm.png)
    * Medium: ![Subscription Plans Page (Medium)](docs/plan-md.png)
    * Large: ![Subscription Plans Page (Large)](docs/plan-lg.png)

* **Checkout Page**:
    * Small: ![Checkout Page (Small)](docs/checkout-sm.png)
    * Medium: ![Checkout Page (Medium)](docs/checkout-md.png)
    * Large: ![Checkout Page (Large)](docs/checkout-lg.png)

* **Topic Preferences Page**:
    * Small: ![Topic Preferences Page (Small)](docs/topics-sm.png)
    * Medium: ![Topic Preferences Page (Medium)](docs/topics-md.png)
    * Large: ![Topic Preferences Page (Large)](docs/topics-lg.png)

---

## Future Improvements

InfoCrumbs is continuously evolving. Here are some key features and enhancements planned for future development:

* Enhanced Content Recommendation (Liked Crumb Feature):
  - Goal: To significantly improve the content recommendation algorithm.
  - Mechanism: Leverage user "likes" (captured by the existing `LikedCrumb` model in the `feedback` app) to understand individual preferences at a deeper level. This data will be used to fine-tune the content delivery, ensuring users receive even more relevant and engaging "crumbs." Research into collaborative filtering and content-based recommendation algorithms is ongoing.

* Comprehensive Automated Testing for API Integrations:
   - Goal: Expand the test suite to include robust automated testing for all components interacting with external APIs.
   - Focus Areas: Prioritize testing for the `pipeline` app (ensuring reliable data fetching, processing, and summarization from Finnhub, Spoonacular, Mediastack, and Hugging Face) and the `checkout` app (verifying seamless interaction with Stripe's API and webhooks). This will enhance system stability and data integrity.

* Transition to a Modern React Frontend:
  - Goal: Evolve the user interface into a dynamic and highly interactive Single Page Application (SPA).
  - Preparation: The groundwork has been laid with the inclusion of `api_urls.py` and `api_views.py` files in relevant Django apps. These API endpoints are designed to serve data to a decoupled frontend, facilitating a smooth transition to a React-based UI for improved responsiveness, user experience, and development scalability.

---

## Contributing

I welcome contributions to InfoCrumbs! Please feel free to open issues, suggest enhancements, or submit pull requests.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.