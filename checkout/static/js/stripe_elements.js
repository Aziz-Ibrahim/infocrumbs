// static/js/stripe_elements.js

// Retrieve values from Django's json_script tags using jQuery selectors
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
var planId = $('#id_plan_id').val();
var frequencyId = $('#id_frequency_id').val();

// Retrieve user full name and email from json_script tags
var userFullName = JSON.parse(document.getElementById('id_user_full_name').textContent);
var userEmail = JSON.parse(document.getElementById('id_user_email').textContent);

var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();

// Define custom styling for the Stripe Elements to match Bootstrap/Crispy Forms dark theme
var style = {
    base: {
        color: '#e0e0e0', // Light text color for input (matches your dark theme)
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif', // Consistent font
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4' // Placeholder text color
        },
        ':-webkit-autofill': {
            color: '#e0e0e0', // Text color for autofilled fields
            backgroundColor: '#3a3a3a', // Background for autofilled fields
        },
    },
    invalid: {
        color: '#fa755a', // Error text color
        iconColor: '#fa755a' // Error icon color
    }
};

// Create the card element and hide the postal code
var card = elements.create('card', {
    style: style,
    hidePostalCode: true // <-- This hides the ZIP/Postal Code field
});

// Mount the card element to the div with id="card-element"
card.mount('#card-element');

// Handle real-time validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        $(errorDiv).text(event.error.message);
    } else {
        $(errorDiv).text('');
    }
});

// Handle form submission
var form = document.getElementById('payment-form');

if (form) { // Ensure the form element exists before adding the event listener
    form.addEventListener('submit', function(ev) {
        ev.preventDefault(); // Prevent default form submission
        card.update({ 'disabled': true}); // Disable card input
        $('#submit-button').attr('disabled', true); // Disable submit button
        $('#loading-overlay').fadeIn(100); // Show loading overlay

        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        var postData = {
            'csrfmiddlewaretoken': csrfToken,
            'client_secret': clientSecret,
            'plan_id': planId,
            'frequency_id': frequencyId,
        };
        var url = '/checkout/cache_checkout_data/'; // AJAX URL to cache data

        // Use AJAX to send metadata to cache_checkout_data view
        $.post(url, postData).done(function () {
            // Confirm the payment with Stripe
            stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: userFullName, // Use the safely parsed user data
                        email: userEmail,   // Use the safely parsed user data
                    }
                }
            }).then(function(result) {
                if (result.error) {
                    // Show error to the customer
                    var errorDiv = document.getElementById('card-errors');
                    $(errorDiv).text(result.error.message);
                    card.update({ 'disabled': false}); // Re-enable card input
                    $('#submit-button').attr('disabled', false); // Re-enable submit button
                    $('#loading-overlay').fadeOut(100); // Hide loading overlay
                } else {
                    if (result.paymentIntent.status === 'succeeded') {
                        // Redirect to success page upon successful payment
                        window.location.replace('/checkout/success/' + result.paymentIntent.id + '/');
                    }
                }
            });
        }).fail(function () {
            // Reload page if cache_checkout_data fails to show Django messages
            location.reload();
        });
    });
}
