import streamlit as st
from classifier import EmailClassifier

def main():
    st.title("Email Sentiment Classifier")
    st.write("Enter the raw email text below:")

    email_text = st.text_area("Email Text", height=300)

    if st.button("Classify"):
        if email_text:
            classifier = EmailClassifier()
            sentiment, priority = classifier.classify_email(email_text)
            st.success(f"Sentiment: {sentiment}")
            st.success(f"Priority: {priority}")
        else:
            st.error("Please enter some email text.")

if __name__ == "__main__":
    main()