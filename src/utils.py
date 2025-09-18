def clean_text(text):
    # Function to clean the email text by removing unwanted characters and formatting
    import re
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text.strip()

def tokenize_text(text):
    # Function to tokenize the cleaned text into words
    return text.split()

def preprocess_email(email_text):
    # Function to preprocess the email text
    cleaned_text = clean_text(email_text)
    tokens = tokenize_text(cleaned_text)
    return tokens