# ============================================================
# LLM ERROR HANDLER
# ============================================================


def is_rate_limit_error(error):

    error_message = str(error).lower()

    rate_limit_keywords = [
        "429",
        "rate limit",
        "rate_limit_exceeded",
        "tokens per day",
        "tokens per minute",
        "requests per minute"
    ]

    return any(
        keyword in error_message
        for keyword in rate_limit_keywords
    )