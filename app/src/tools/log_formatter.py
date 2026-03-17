import json
import logging


def format_exception_for_logging(exception):
    # Extract the exception message
    exception_message = str(exception)

    # Find the part of the message that contains the JSON data
    try:
        start_index = exception_message.index("Response")
        exception_message = exception_message[start_index:]
        start_index = exception_message.index(" Data    : ") + len("Data    : ")
        json_data_str = exception_message[start_index:]
        json_data = json.loads(json_data_str)

        # Extract relevant information
        status_code = json_data.get("statusCode")
        error_type = json_data.get("type")
        message = json_data.get("message")
        details = json_data.get("details", [])
        error = json_data.get("error")
        error_code = json_data.get("errorCode")
        error_details = json_data.get("errorDetails", {}).get("errors", []) or json_data.get("errors", {})

        # Ensure details are strings
        details_str = ", ".join([str(detail) for detail in details])
        error_details_str = json.dumps(error_details, indent=2)

        # Format the message
        formatted_message = (
            f"Exception occurred:\n"
            f"Status Code: {status_code}\n"
            f"Type: {error_type}\n"
            f"Message: {message}\n"
            f"Error: {error}\n"
            f"Error Code: {error_code}\n"
            f"Details: {details_str}\n"
            f"Error Details: {error_details_str}"
        )

        return formatted_message
    except (ValueError, json.JSONDecodeError) as e:
        logging.warning(f"Failed to parse exception data: {e}")
        return f"Exception occurred: {exception_message}"


# Function to reset the logger
def reset_logger(logger_name):
    logger = logging.getLogger(logger_name)

    # Remove all handlers associated with the logger
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
