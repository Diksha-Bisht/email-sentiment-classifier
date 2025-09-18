# Email Sentiment Classifier

This project is a simple email sentiment and priority classifier built using Streamlit. It takes raw email text as input and outputs the sentiment (Positive, Negative, Neutral) and priority (High, Medium, Low) based on the content and urgency signals in the email.

## Features

- Input raw email text
- Predict sentiment of the email using VADER sentiment analysis
- Determine priority level of the email using advanced heuristics
- User-friendly interface built with Streamlit

## Project Structure

```
email-sentiment-classifier
├── src
│   ├── app.py          # Main entry point for the Streamlit 
│   ├── classifier.py   # Contains the EmailClassifier class for 
│   └── utils.py        # Utility functions for text preprocessing
├── requirements.txt     # Lists project dependencies
└── README.md            # Project documentation
```

## Installation

1. **Clone the repository:**
   ```sh
   git clone <repository-url>
   cd email-sentiment-classifier
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command:
```
streamlit run src/app.py
```


## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License.
