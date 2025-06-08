# TESTING.md: Comprehensive Testing Strategy for InfoCrumbs

This document outlines the testing methodologies employed for the InfoCrumbs application, ensuring its robustness, reliability, and adherence to functional requirements. Both automated and manual testing approaches are utilized to cover various aspects of the system.

---

## Table of Contents

1. [Automated Testing](#automated-testing)

   * [Running the Test Suite](#running-the-test-suite)

   * [Test Coverage](#test-coverage)

   * [Key Areas Covered by Automated Tests](#key-areas-covered-by-automated-tests)

2. [Manual Testing](#manual-testing)

   * [Key User Flows](#key-user-flows)

   * [Feature-Specific Scenarios](#feature-specific-scenarios)

   * [Edge Cases and Error Handling](#edge-cases-and-error-handling)

   * [Browser and Device Compatibility](#browser-and-device-compatibility)

   * [Performance Observation](#performance-observation)

3. [Reporting and Documentation](#reporting-and-documentation)

---

## 1. Automated Testing

Automated tests are critical for continuous integration, rapid feedback, and regression prevention. InfoCrumbs utilizes Django's built-in `TestCase` framework to conduct unit and integration tests across its applications.

### Running the Test Suite

To execute the entire test suite for the InfoCrumbs project:

```
python manage.py test

```

To run tests for a specific application (e.g., `preferences`):

```
python manage.py test preferences

```

### Test Coverage

*(Placeholder for test coverage details.)*
After running tests, a coverage report can be generated (e.g., using `coverage.py`).

* **To install coverage.py**:

  ```
  pip install coverage
  
  ```

* **To run tests with coverage and generate report**:

  ```
  coverage run manage.py test
  coverage report
  coverage html # To generate an HTML report in 'htmlcov/'
  
  ```

* **Current Coverage**:

  * Overall: \[Percentage\]%

  * `accounts` app: \[Percentage\]%

  * `preferences` app: \[Percentage\]%

  * `subscriptions` app: \[Percentage\]%

  * `crumbs` app: \[Percentage\]%

  * `pipeline` app: \[Percentage\]%

### Key Areas Covered by Automated Tests

* **Model Logic**: Verification of `__str__` methods, default values, unique constraints (e.g., `Topic` slug generation), and relationships.

* **Form Validation**: Comprehensive testing of form fields, custom `clean` methods (e.g., `UserPreferenceForm`'s topic limits based on subscription), and error message accuracy.

* **View Functionality**:

  * HTTP method handling (GET/POST).

  * Authentication and authorization (e.g., `@login_required` decorators).

  * Conditional rendering and context data.

  * Redirection logic (e.g., unsubscribed users redirected to `choose_plan`).

  * Database interactions (object creation, updates, deletions).

* **Data Pipeline (`pipeline` app)**:

  * API fetching logic (simulated or real API calls in controlled environments).

  * Data parsing and transformation.

  * Integration with summarization (Hugging Face) and handling of edge cases (e.g., long text truncation, API timeouts).

  * Crumb creation and updates in the database.

---

## 2. Manual Testing

Manual testing complements automated tests by validating the user experience, visual consistency, and overall flow that automated tests may not fully capture.

### Key User Flows

* **User Registration & Login**:

  * Successful registration with valid credentials.

  * Login with correct/incorrect credentials.

  * Password reset flow.

* **Subscription Management**:

  * Navigating to `choose_plan` page.

  * Selecting a basic plan.

  * Selecting a premium plan.

  * (If applicable) Upgrading/downgrading subscriptions.

* **Topic Preferences (Subscribed Users)**:

  * Accessing the "Edit Topic Preferences" page from the profile.

  * Selecting topics within the `basic` plan limit (e.g., 2 topics).

  * Attempting to select more than the `basic` plan limit (verify error message).

  * Selecting topics with a `premium` plan (verify no strict limit shown/enforced).

  * Saving preferences successfully.

  * Updating existing preferences.

* **Content Display**:

  * Viewing the main content feed (Home page).

  * Verifying that only crumbs from preferred topics are displayed.

  * Testing pagination (navigating between pages of crumbs).

  * Verifying content summaries are legible.

  * Testing individual crumb detail views.

### Feature-Specific Scenarios

* **Unsubscribed User Experience**:

  * Attempting to access `set_preferences` URL directly (verify redirection to `choose_plan`).

  * Observing profile page links for unsubscribed users.

* **API Data Freshness**:

  * Manually running `python manage.py fetch_crumbs`.

  * Verifying new content appears in the database and on the home page.

  * Checking content from all integrated APIs (Finnhub, Spoonacular, Mediastack).

* **User Profile Management**:

  * Updating user details (if available).

### Edge Cases and Error Handling

* **Invalid Form Submissions**: Beyond automated checks, visually confirm error messages are clear and well-presented.

* **Network Issues/API Downtime**: (Manual simulation, if feasible) Observe how the `fetch_crumbs` command handles API failures and prints error messages.

* **Empty States**: What happens if a user has no preferred topics? No crumbs fetched?

### Browser and Device Compatibility

*(Placeholder for browser/device compatibility checks.)*

* **Browsers**: Test across major browsers (Chrome, Firefox, Edge, Safari).

* **Responsiveness**: Verify UI/UX across different screen sizes and devices (desktop, tablet, mobile) to ensure a consistent experience.

### Performance Observation

*(Placeholder for performance observations.)*

* Observe page load times.

* Note responsiveness of UI elements.

* Monitor API call durations (if dev tools are used).

---

## 3. Reporting and Documentation

*(Placeholder for details on how test results are reported.)*

* **Automated Test Reports**: HTML coverage reports, console output of passing/failing tests.

* **Manual Test Logs**: \[Link to manual test log document/template if applicable\]

* **Bug Reporting**: \[Details on bug reporting process if applicable, e.g., GitHub Issues\]
