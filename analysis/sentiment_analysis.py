import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import re
import nltk

nltk.download("punkt")

# Check if Metal API is available for GPU acceleration (Only for M series Macs)
device = "mps" if torch.backends.mps.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

sentiment_analyser = pipeline(
    "sentiment-analysis", 
    model=model, 
    tokenizer=tokenizer, 
    device=0 if device == "mps" else -1
)

def normalise_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def analyse_sentiment(text):
    if text.strip() == "":
        return {"label": None, "score": 0.0}
    result = sentiment_analyser(text[:512])
    return result[0]

file_path = "/Users/farhadkhurami/Developer/reddit-scraper/analysis/posts.csv"
df = pd.read_csv(file_path)

df["post_title_normalized"] = df["post_title"].apply(normalise_text)
df["post_body_normalized"] = df["post_body"].apply(normalise_text)

df["title_sentiment"] = df["post_title_normalized"].apply(analyse_sentiment)
df["body_sentiment"] = df["post_body_normalized"].apply(analyse_sentiment)

df["title_sentiment_label"] = df["title_sentiment"].apply(lambda x: x["label"])
# df["title_sentiment_score"] = df["title_sentiment"].apply(lambda x: x["score"])
df["body_sentiment_label"] = df["body_sentiment"].apply(lambda x: x["label"])
# df["body_sentiment_score"] = df["body_sentiment"].apply(lambda x: x["score"])

df.to_csv("sentiment_analysis_results.csv", index=False)
