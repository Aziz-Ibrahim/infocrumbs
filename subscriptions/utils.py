

def calculate_subscription_price(plan_name, duration_days):
    base_price = 5 if plan_name.strip().lower() == "basic" else 10

    if duration_days == 7:
        return base_price
    elif duration_days == 30:
        return round(base_price * 52 / 12 * 0.9, 2)
    elif duration_days == 365:
        return round(base_price * 52 * 0.7, 2)
    else:
        return None
