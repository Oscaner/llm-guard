from llm_guard.util import lazy_load_dep, logger

from .base import Scanner

_lexicon = "vader_lexicon"


class Sentiment(Scanner):
    """
    A sentiment scanner based on the NLTK's SentimentIntensityAnalyzer. It is used to detect if a prompt
    has a sentiment score lower than the threshold, indicating a negative sentiment.
    """

    def __init__(self, *, threshold: float = -0.1, lexicon: str = _lexicon):
        """
        Initializes Sentiment with a threshold and a chosen lexicon.

        Parameters:
           threshold (float): Threshold for the sentiment score (from -1 to 1). Default is -0.1.
           lexicon (str): Lexicon for the SentimentIntensityAnalyzer. Default is 'vader_lexicon'.

        Raises:
           None.
        """

        nltk = lazy_load_dep("nltk")
        nltk.download(lexicon)

        sentiment = lazy_load_dep("nltk.sentiment", "nltk")
        self._sentiment_analyzer = sentiment.SentimentIntensityAnalyzer()
        self._threshold = threshold

    def scan(self, prompt: str) -> (str, bool, float):
        sentiment_score = self._sentiment_analyzer.polarity_scores(prompt)
        sentiment_score_compound = sentiment_score["compound"]
        if sentiment_score_compound > self._threshold:
            logger.debug(f"Sentiment score: {sentiment_score}, threshold: {self._threshold}")

            return prompt, True, 0.0

        logger.warning(
            f"Sentiment score is over threshold: {sentiment_score}, threshold: {self._threshold}"
        )

        # Normalize such that -1 maps to 1 and threshold maps to 0
        score = round((sentiment_score_compound - (-1)) / (self._threshold - (-1)), 2)
        return prompt, False, score
