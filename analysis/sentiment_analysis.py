import os
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import re
import logging
from time import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

logging.info("Starting sentiment analysis script.")


def run_sentiment_analysis(model_name, file_path, output_dir="results"):
    """
    Run sentiment analysis using the specified model and save the results to a CSV file.

    Args:
        model_name (str): Hugging Face model name or path.
        file_path (str): Path to the input CSV file containing the posts.
        output_dir (str): Directory to save the output files.
    """

    def _normalise_text(text):
        if pd.isna(text):
            return ""
        text = text.lower()
        text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    if not os.path.exists(output_dir):
        logging.info(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir)

    def _analyse_sentiment_label(text):
        """
        Returns only the sentiment label (e.g., 'POSITIVE', 'NEGATIVE', 'NEUTRAL').
        """
        if text.strip() == "":
            return None
        result = sentiment_analyser(text[:512])
        return result[0]["label"]

    # Check if Metal API is available for GPU acceleration (for M series Macs)
    device = "mps" if torch.backends.mps.is_available() else "cpu"

    logging.info(f"Loading model and tokenizer for: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    logging.info("Initialising sentiment analysis pipeline.")
    sentiment_analyser = pipeline(
        "sentiment-analysis",
        model=model,
        tokenizer=tokenizer,
        device=0 if device == "mps" else -1,
    )

    logging.info(f"Loading data from {file_path}.")
    try:
        df = pd.read_csv(file_path)
        logging.info(f"Loaded {len(df)} rows from the dataset.")
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise

    # Normalise text and analyse sentiment
    logging.info("Normalising text and extracting sentiment labels.")
    start_time = time()
    df["post_title_normalised"] = df["post_title"].apply(_normalise_text)
    df["post_body_normalised"] = df["post_body"].apply(_normalise_text)

    df["title_sentiment_label"] = df["post_title_normalised"].apply(
        _analyse_sentiment_label
    )
    df["body_sentiment_label"] = df["post_body_normalised"].apply(
        _analyse_sentiment_label
    )
    logging.info(
        f"Sentiment label extraction completed in {time() - start_time:.2f} seconds."
    )

    output_path = (
        f"{output_dir}/sentiment_analysis_results_{model_name.replace('/', '_')}.csv"
    )
    logging.info(f"Saving results to {output_path}.")
    df.to_csv(output_path, index=False)
    logging.info("Results saved successfully. Sentiment analysis process completed.")


if __name__ == "__main__":
    input_file_path = "/Users/farhadkhurami/Developer/reddit-scraper/posts.csv"
    models = [
        "ProsusAI/finbert",
        "yiyanghkust/finbert-tone",
        "finiteautomata/bertweet-base-sentiment-analysis",
        "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
        "finiteautomata/beto-sentiment-analysis",
        "StephanAkkerman/FinTwitBERT-sentiment",
    ]

    for model_name in models:
        run_sentiment_analysis(model_name, input_file_path)
