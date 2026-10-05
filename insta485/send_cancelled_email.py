def send_cancelled_email(
    buyer_email, event_name, price=None, seller_email=None, send_email_func=None
):
    subject = f"Your transaction for {event_name} was cancelled"
    body = (
        f"Hello,\n\nWe regret to inform you that your transaction for '{event_name}' has been cancelled. "
        + (f"Price: ${price}\n" if price else "")
        + (f"Seller: {seller_email}\n" if seller_email else "")
        + "\nIf you have any questions, please contact support.\n\nBest,\nTicketVault Team"
    )
    html = f"""
        <p>Hello,</p>
        <p>We regret to inform you that your transaction for <b>{event_name}</b> has been <span style=\"color:#dc3545;font-weight:bold;\">cancelled</span>.</p>
        {(f"<p>Price: <b>${price}</b><br></p>" if price else "")}
        {(f"<p>Seller: <b>{seller_email}</b></p>" if seller_email else "")}
        <p>If you have any questions, please contact support.</p>
        <p style=\"margin-top:24px;\">Best,<br>TicketVault Team</p>
    """
    if send_email_func is not None:
        return send_email_func(buyer_email, subject, body, html=html)
    try:
        from insta485.email_utils import send_email

        return send_email(buyer_email, subject, body, html=html)
    except ImportError:
        return False
