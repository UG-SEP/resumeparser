class StatusMessages:
    SUCCESS = "Resume processed successfully"
    FAILURE_EXTRACT_TEXT = "Failed to extract text from the PDF."
    FAILURE_PARSE_DATA = "Failed to parse resume data."
    FAILURE_SAVE_DATA = "Failed to save resume data."
    EMAIL_NOT_FOUND = "Email not found in the resume"
    MOBILE_NOT_FOUND = "Mobile no. not found "

class TimeFilter:
    ONE_HOUR = "one_hour"
    SIX_HOUR = "six_hour"
    TWELEVE_HOUR = "tweleve_hour"
    ONE_DAY = "one_day"
    SEVEN_DAY = "seven_day"
    ONE_MONTH = "one_month"