// Retrieve values from Django's json_script tags using jQuery selectors
const stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
const clientSecret = $('#id_client_secret').text().slice(1, -1);
const planId = $('#id_plan_id').val();
const frequencyId = $('#id_frequency_id').val();

// Retrieve user full name and email from json_script tags
const userFullName = JSON.parse(document.getElementById('id_user_full_name').textContent);
const userEmail = JSON.parse(document.getElementById('id_user_email').textContent);

const stripe = Stripe(stripePublicKey);
const elements = stripe.elements();

// Define custom styling for the Stripe Elements to match Bootstrap/Crispy Forms dark theme
const style = {
    base: {
        color: '#f8f9fa', // Bright text color for input (contrasts with dark background)
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif', // Consistent font
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#adb5bd' // Slightly muted placeholder text color
        },
        // CRITICAL: Adjusted padding for vertical centering.
        // (48px total height - 16px font-size) / 2 = 16px top/bottom padding
        padding: '16px 12px', // Top/bottom 16px, left/right 12px
        backgroundColor: '#343a40', // Explicitly set background color for the input field itself
        ':-webkit-autofill': {
            color: '#f8f9fa', // Text color for autofilled fields
            backgroundColor: '#343a40', // Background for autofilled fields
        },
        // Removed explicit 'height' and 'lineHeight' from here,
        // relying on external CSS for overall container height and padding for internal spacing.
    },
    invalid: {
        color: '#fa755a', // Error text color
        iconColor: '#fa755a' // Error icon color
    }
};

// Create the card element and hide the postal code
const card = elements.create('card', {
    style: style,
    hidePostalCode: true // This hides the ZIP/Postal Code field
});

// Mount the card element to the div with id="card-element"
card.mount('#card-element');

// Handle real-time validation errors on the card element
card.addEventListener('change', function (event) {
    const errorDiv = document.getElementById('card-errors');
    if (event.error) {
        $(errorDiv).text(event.error.message);
    } else {
        $(errorDiv).text('');
    }
});

// Handle form submission
const form = document.getElementById('payment-form');

if (form) {
    form.addEventListener('submit', function(ev) {
        ev.preventDefault();
        card.update({ 'disabled': true});
        $('#submit-button').attr('disabled', true);
        $('#loading-overlay').fadeIn(100);

        const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        const postData = {
            'csrfmiddlewaretoken': csrfToken,
            'client_secret': clientSecret,
            'plan_id': planId,
            'frequency_id': frequencyId,
        };
        const url = '/checkout/cache_checkout_data/';

        $.post(url, postData).done(function () {
            stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: userFullName,
                        email: userEmail,
                    }
                }
            }).then(function(result) {
                if (result.error) {
                    const errorDiv = document.getElementById('card-errors');
                    $(errorDiv).text(result.error.message);
                    card.update({ 'disabled': false});
                    $('#submit-button').attr('disabled', false);
                    $('#loading-overlay').fadeOut(100);
                } else {
                    if (result.paymentIntent.status === 'succeeded') {
                        window.location.replace('/checkout/success/' + result.paymentIntent.id + '/');
                    }
                }
            });
        }).fail(function () {
            location.reload();
        });
    });
}
