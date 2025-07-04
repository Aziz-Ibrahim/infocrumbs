# Comprehensive Testing Strategy for InfoCrumbs

This document outlines the testing methodologies employed for the InfoCrumbs application, ensuring its robustness, reliability, and adherence to functional requirements. Both automated and manual testing approaches are utilized to cover various aspects of the system.

---

## Table of Contents

1.  [Automated Testing](#automated-testing)
    * [Running the Test Suite](#running-the-test-suite)
    * [Test Coverage](#test-coverage)
    * [Key Areas Covered by Automated Tests](#key-areas-covered-by-automated-tests)
2.  [Manual Testing](#manual-testing)
    * [Key User Flows](#key-user-flows)
    * [Feature-Specific Scenarios](#feature-specific-scenarios)
    * [Edge Cases and Error Handling](#edge-cases-and-error-handling)
    * [Browser and Device Compatibility](#browser-and-device-compatibility)
    * [Performance Observation](#performance-observation)
3.  [Reporting and Documentation](#reporting-and-documentation)

---

## 1. Automated Testing

Automated tests are critical for continuous integration, rapid feedback, and regression prevention. InfoCrumbs utilizes Django's built-in `TestCase` framework to conduct unit and integration tests across its applications.

### Running the Test Suite

To execute the entire test suite for the InfoCrumbs project:

```bash
python manage.py test
```

To run tests for a specific application (e.g., `checkout`):

```bash
python manage.py test checkout
```

### Test Coverage

After running tests, a coverage report can be generated (e.g., using `coverage.py`).

* **To install coverage.py**:

    ```bash
    pip install coverage
    ```

* **To run tests with coverage and generate report**:

    ```bash
    coverage run manage.py test
    coverage report
    coverage html # To generate an HTML report in 'htmlcov/'
    ```

* **Current Coverage**:

    * Overall: [Percentage]%
    * `accounts` app: [Percentage]%
    * `preferences` app: [Percentage]%
    * `subscriptions` app: [Percentage]%
    * `crumbs` app: [Percentage]%
    * `pipeline` app: [Percentage]%

### Key Areas Covered by Automated Tests

* **Model Logic**: Verification of `__str__` methods, default values, unique constraints, and relationships.
    * `UserSubscription.save()` logic for calculating `start_date` and `end_date` based on existing subscriptions.
    * `CustomUser` fields and relationships.
* **Form Validation**: Comprehensive testing of form fields, custom `clean` methods, and error message accuracy.
    * `CustomSignupForm.clean_date_of_birth` to enforce a minimum age of 12 and prevent future dates.
    * `UserUpdateForm.clean_date_of_birth` for consistent date of birth validation during profile updates.
    * `UserPreferenceForm.clean_topics` to enforce subscription-based topic selection limits.
    * `CommentForm` for content length validation.
* **View Functionality**:
    * HTTP method handling (GET/POST).
    * Authentication and authorization (e.g., `@login_required` decorators ensuring redirects to login for unauthenticated users).
    * Conditional rendering and context data passed to templates.
    * Redirection logic (e.g., unsubscribed users redirected to `choose_plan`, invalid plan/frequency selection redirects).
    * Database interactions (object creation, updates, deletions).
    * **AJAX Endpoints**: Verification that partial views (`load_account_details`, `account_update`, `load_saved_crumbs_partial`, `load_comments_partial`, `load_preferences_partial`, `load_subscription_partial`) return valid JSON responses containing expected HTML snippets and data (e.g., pagination info).
    * **Payment Flow**: Mocked Stripe API interactions in `checkout_subscription` and `cache_checkout_data` views.
    * **Webhook Handling**: Testing `StripeWH_Handler` methods (`handle_payment_intent_succeeded`, `handle_payment_intent_payment_failed`) for correct subscription creation/update and error handling.
    * **Race Condition Handling**: Testing the retry mechanism in `checkout_success` view to ensure subscription details load even with webhook delays.
* **Data Pipeline (`pipeline` app)**:
    * API fetching logic (simulated or real API calls in controlled environments).
    * Data parsing and transformation.
    * Integration with summarization (e.g., Hugging Face models) and handling of edge cases (e.g., long text truncation, API timeouts).
    * Crumb creation and updates in the database.

---

## 2. Manual Testing

Manual testing complements automated tests by validating the user experience, visual consistency, and overall flow that automated tests may not fully capture.

### Key User Flows

* **User Registration & Login**:
    * Successful registration with valid credentials.
    * Login with correct/incorrect credentials.
    * Password reset flow.
    * **Date of Birth Validation**: Attempting to register with a future date of birth or an age under 12 (verify clear error messages are displayed).
* **Subscription Management**:
    * Navigating to `choose_plan` page.
    * Selecting a basic plan and completing the Stripe checkout process.
    * Selecting a premium plan and completing the Stripe checkout process.
    * Verifying `checkout_success` page displays correct payment ID and subscription dates.
    * (If applicable) Upgrading/downgrading subscriptions and observing changes.
    * Testing the refund eligibility window (within 24 hours).
* **Topic Preferences (Subscribed Users)**:
    * Accessing the "Edit Topic Preferences" tab from the profile.
    * Selecting topics within the `basic` plan limit (e.g., 2 topics) and saving.
    * **Client-Side Limit Enforcement**: Attempting to select more than the `basic` plan limit (verify immediate client-side alert and prevention of selection).
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
    * Observing profile page links and options for unsubscribed users.
* **API Data Freshness**:
    * Manually running `python manage.py fetch_crumbs`.
    * Verifying new content appears in the database and on the home page.
    * Checking content from all integrated APIs (e.g., Finnhub, Spoonacular, Mediastack).
* **User Profile Management**:
    * Accessing the "Edit Details" tab on the profile page.
    * Updating `first_name`, `last_name`, `email`, and `date_of_birth` with valid data.
    * Submitting invalid data (e.g., future DOB, invalid email format) and verifying AJAX-rendered error messages appear correctly within the tab.

### Edge Cases and Error Handling

* **Invalid Form Submissions**: Beyond automated checks, visually confirm error messages are clear, well-presented, and appear in the correct locations (especially for AJAX-loaded forms).
* **Network Issues/API Downtime**: (Manual simulation, if feasible) Observe how the `fetch_crumbs` command handles API failures and prints error messages. Observe how payment flow handles Stripe API errors.
* **Empty States**: What happens if a user has no preferred topics? No crumbs fetched? No comments? No saved crumbs?
* **Concurrent Actions**: (If applicable) Test scenarios where multiple users or actions occur simultaneously.

### Browser and Device Compatibility

* **Browsers**: Test across major modern browsers:
    * Google Chrome (latest stable)
    * Mozilla Firefox (latest stable)
    * Microsoft Edge (latest stable)
    * Apple Safari (latest stable on macOS/iOS)
* **Responsiveness**: Verify UI/UX across different screen sizes and devices:
    * Desktop monitors (various resolutions).
    * Tablets (portrait and landscape).
    * Mobile phones (portrait and landscape).
    * Use browser developer tools (e.g., Chrome DevTools device mode) to simulate various screen sizes.
    * Ensure all elements scale and rearrange correctly without horizontal scrolling.

### Performance Observation

* **Page Load Times**: Observe initial page load times and subsequent AJAX content loading.
* **UI Responsiveness**: Note the responsiveness of interactive UI elements (buttons, forms, tab switching).
* **API Call Durations**: (If using browser dev tools) Monitor network requests for external API calls and their durations.
* **Database Query Performance**: (During development/local testing) Use Django Debug Toolbar to identify slow database queries.

---

## 3. Reporting and Documentation

* **Automated Test Reports**: HTML coverage reports generated by `coverage.py` provide a detailed overview of code coverage. Console output from `python manage.py test` indicates passing/failing tests.
* **Manual Test Logs**: (Optional) Maintain a separate document or spreadsheet for detailed manual test cases, results, and observations.
* **Bug Reporting**: Any issues discovered during testing are reported through [e.g., GitHub Issues / Jira / Trello] with clear steps to reproduce, expected behavior, and actual behavior.