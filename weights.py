import torch
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

model = None

def computeWeights(df, question):
    global model
    if model is None:
        print("Loading SentenceTransformer model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded successfully.")
    if isinstance(df, list):
        try:
            df = pd.DataFrame(df)
            print("Converted MongoDB list to DataFrame. Columns:", df.columns.tolist())
        except Exception as e:
            raise ValueError(f"Failed to convert MongoDB list to DataFrame: {str(e)}")
    
    # Validate that input is a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"Input must be a pandas DataFrame or list of dicts, got {type(df)}")
    
    # Validate required columns
    required_columns = ['question', 'tool', 'score']
    df = df[required_columns]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"DataFrame missing required columns: {required_columns}. Found: {df.columns.tolist()}")
    
    # Check if DataFrame is empty
    if df.empty:
        print("Warning: DataFrame is empty. Returning equal weights.")
        return [1.0 / 3] * 3

    uniqueQuestions = df['question'].unique()
    questionEmbeddings = model.encode(uniqueQuestions, convert_to_tensor=True, normalize_embeddings=True)
    newEmbedding = model.encode([question], convert_to_tensor=True, normalize_embeddings=True)[0]
    similarities = torch.sum(newEmbedding * questionEmbeddings, dim=1).numpy()
    simDict = dict(zip(uniqueQuestions, similarities))

    weights = []

    for toolId in [1, 2, 3]:
        toolDf = df[df['tool'] == toolId]

        weightedSum = sum(simDict[row['question']] * row['score'] for index, row in toolDf.iterrows())

        weights.append(weightedSum)
    
    total = sum(weights)
    if total > 0:
        normalizedWeights = [w / total for w in weights]

    else:
        normalizedWeights = [1.0 / 3] * 3
    return normalizedWeights