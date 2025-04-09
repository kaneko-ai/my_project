# utils/model_recommender.py

def recommend_model(text: str) -> str:
    length = len(text)

    if length < 800:
        return "pegasus"
    elif length < 1500:
        return "bart"
    else:
        return "default"
