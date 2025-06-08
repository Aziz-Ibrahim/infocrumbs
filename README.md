# InfoCrumbs: Your Personalized Content Dashboard

## Project Overview

InfoCrumbs is a sophisticated Django-based web application engineered to revolutionize how users consume digital content. In today's overwhelming information landscape, InfoCrumbs cuts through the noise by delivering **personalized news and articles**—or "crumbs"—directly tailored to individual interests and tiered subscription plans. This project showcases a robust backend data pipeline, dynamic content summarization, and a meticulously designed user experience, built with scalability and maintainability in mind.

---

## Table of Contents

1. [Features](#features)

2. [Technical Architecture & Stack](#technical-architecture--stack)

3. [Installation and Setup](#installation-and-setup)

   * [Prerequisites](#prerequisites)

   * [Cloning the Repository](#cloning-the-repository)

   * [Virtual Environment Setup](#virtual-environment-setup)

   * [Install Dependencies](#install-dependencies)

   * [Environment Variables](#environment-variables)

   * [Database Setup](#database-setup)

   * [Create Superuser](#create-superuser)

   * [Populate Initial Data](#populate-initial-data)

4. [Running the Application](#running-the-application)

   * [Development Server](#development-server)

   * [Running the Data Pipeline](#running-the-data-pipeline)

5. [Testing](#testing)

6. [Code Quality & Linting Reports](#code-quality--linting-reports)

7. [Screenshots](#screenshots)

8. [Contributing](#contributing)

9. [License](#license)

---

## Features

* **Intelligent Content Aggregation**: Automated integration with diverse external APIs (Finnhub, Spoonacular, Mediastack) to fetch a wide array of content, from financial insights and cutting-edge tech news to curated recipes.

* **Dynamic Data Pipeline (`pipeline` app)**: A custom-built, scheduled management command orchestrates the fetching, processing, and storage of content. This pipeline is designed for efficiency and extensibility, ensuring fresh "crumbs" are always available.

* **Real-time Content Summarization**: Leveraging the Hugging Face Inference API, InfoCrumbs generates concise summaries for lengthy articles. This intelligent processing ensures users get essential information quickly, enhancing content digestibility.

* **Granular User Preferences (`preferences` app)**: Users can define their specific interests by selecting preferred topics. The system intelligently manages these preferences, directly influencing the content delivered.

* **Flexible Subscription Tiers**: A robust subscription model empowers tiered access (Basic, Premium) to content. This includes dynamic topic limits and exclusive content features, providing a scalable business logic foundation.

* **Secure User Authentication**: Full user registration, login, and profile management capabilities, ensuring a secure and personalized user journey.

* **Dynamic Access Control**: Critical views and features, such as topic preference management, are protected by intelligent redirects, ensuring only active, subscribed users can access privileged functionalities.

---

## Technical Architecture & Stack

InfoCrumbs is built upon a modern, modular Django architecture, prioritizing clear separation of concerns and maintainability.

* **Backend**: **Django (Python Web Framework)** - Chosen for its "batteries-included" approach, ORM capabilities, and strong community support, accelerating development while ensuring robust application logic.

* **Database**: **PostgreSQL (Recommended)** / SQLite (Development) - Provides reliable data storage, with flexibility for easy local setup (SQLite) and scalable deployment (PostgreSQL).

* **External APIs**:

  * **Finnhub**: Utilized for real-time financial news, demonstrating integration with market data APIs.

  * **Spoonacular**: Integrates rich food and drink recipe content, showcasing versatility in content types.

  * **Mediastack**: Powers technology news aggregation, highlighting broad news fetching capabilities.

  * **Hugging Face Inference API**: A testament to advanced NLP integration for on-the-fly text summarization, tackling challenges like API timeouts for large text inputs.

* **Frontend**: Standard Django Templates (HTML, CSS, JavaScript) - Ensures a direct, efficient rendering pipeline for dynamic content.

* **Development Tools**: `pip` (Python package management), `Git` (version control), `pytest` (testing).

---

## Installation and Setup: A Developer's Guide

Getting InfoCrumbs running locally is straightforward, emphasizing best practices for development environments.

### Prerequisites

* Python 3.9+

* `pip` (Python package installer)

* `Git`

### Cloning the Repository

Start by cloning the project to your local machine:

```
git clone [https://github.com/your-username/infocrumbs.git](https://github.com/your-username/infocrumbs.git)
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

---

## Testing: A Commitment to Quality

InfoCrumbs boasts a comprehensive test suite covering models, forms, views, and critical business logic. This rigorous approach ensures code reliability, prevents regressions, and validates expected system behavior across various user scenarios and subscription states. Our iterative development process, including tackling complex issues like multi-hop redirects and dynamic form validation, has significantly strengthened the application's stability.

For detailed instructions on running the test suite and reviewing coverage, please consult the dedicated [TESTING.md](docs/TESTING.md) document.

---

## Code Quality & Linting Reports

*(Placeholder for evidence of adherence to coding standards and best practices.)*

* **PEP 8 Compliance (Python)**:

  * \[Link to PEP 8 report/badge if available\]

* **JavaScript Linting (JSLint/ESLint)**:

  * \[Link to JSLint/ESLint report/badge if available\]

* **HTML/CSS Markup Checks**:

  * \[Link to HTML/CSS validation reports if available\]

---

## Screenshots

*(Placeholder for visual documentation demonstrating the application's key features and user interface.)*

* **Home Page**:

* **User Profile & Preferences Page**:

* **Topic Selection Form**:

* **Content Display (Crumbs List)**:

* **Admin Interface (Models)**:

---

## Contributing

We welcome contributions to InfoCrumbs! Please feel free to open issues, suggest enhancements, or submit pull requests.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
