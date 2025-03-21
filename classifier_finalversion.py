# -*- coding: utf-8 -*-
"""Classifier_FinalVersion.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1QzUPkfQ9Aj5nbO-gxU1SeWP5cBwQQ9RH
"""

# Marieke Schelhaas
# 16 dec. 2024
# Scriptie Dog Whistles
# Credit to Gunjit Bedi for Text Classification Manual
# https://medium.com/@bedigunjit/simple-guide-to-text-classification-nlp-using-svm-and-naive-bayes-with-python-421db3a72d34
# Credit to Preethi Prakash for Accuracy Assesment Manual
# https://medium.com/@preethi_prakash/understanding-baseline-models-in-machine-learning-3ed94f03d645


import sys
import pandas as pd
import numpy as np
import spacy
import nltk
import spacy.cli
nltk.download('stopwords')
spacy.cli.download("nl_core_news_sm")
from nltk.corpus import stopwords
from sklearn.preprocessing import LabelEncoder
from nltk.corpus import wordnet as wn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import model_selection, naive_bayes, svm
from sklearn.metrics import accuracy_score
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, classification_report


def Distribution(Corpus):
      # Print the results
    print(Corpus.Relevancy.value_counts())
    print("---")
    print(Corpus.Sentiment.value_counts())
    print("---")
    print(Corpus.DogWhistle.value_counts())


def BaselineModel(Corpus):
    # Split Dataset and encode labels
    Train_X, Test_X, Train_Y, Test_Y = model_selection.train_test_split(Corpus['LowerTokenizedText'],Corpus['DogWhistle'],test_size=0.2)
    Encoder = LabelEncoder()
    Train_Y = Encoder.fit_transform(Train_Y)
    Test_Y = Encoder.fit_transform(Test_Y)

    # Create a baseline random classifier
    dummy_clf = DummyClassifier(strategy='stratified', random_state=0)
    # Fit the baseline classifier on the training data
    dummy_clf.fit(Train_X, Train_Y)
    # Make predictions on the test data
    Pred_Y = dummy_clf.predict(Test_X)
    # Calculate accuracy and other metrics
    accuracy = accuracy_score(Test_Y, Pred_Y)
    report = classification_report(Test_Y, Pred_Y)

    # Print results
    print("0= Not annotated, 1= Contains Dog Whistle, 2= Contains No Dog Whistle, 3= Potentially \n")
    print("Baseline Classifier Accuracy:", accuracy)
    print("Baseline Classification Report:")
    print(report)


def TextToDW(Corpus, DesiredInput, DesiredOutput, NB):
    # Split Dataset and encode labels
    Train_X, Test_X, Train_Y, Test_Y = model_selection.train_test_split(DesiredInput,DesiredOutput,test_size=0.2)
    Encoder = LabelEncoder()
    Train_Y = Encoder.fit_transform(Train_Y)
    Test_Y = Encoder.fit_transform(Test_Y)

    # Make vector with the tfidf values
    Tfidf_vect = TfidfVectorizer(ngram_range=(1,3), max_features=5000)
    Tfidf_vect.fit(DesiredInput)
    Train_X_Tfidf = Tfidf_vect.transform(Train_X)
    Test_X_Tfidf = Tfidf_vect.transform(Test_X)

    if NB == True :
      # fit the training dataset on the NB classifier
      Naive = naive_bayes.MultinomialNB()
      Naive.fit(Train_X_Tfidf,Train_Y)
      # predict the labels on validation dataset
      predictions_NB = Naive.predict(Test_X_Tfidf)

      # Print Legenda
      print("0= Not annotated, 1= Positive, 2= Negative, 3= Potentially \n")

      # Use accuracy_score function to get the accuracy
      print("- Naive Bayes -")
      print("Accuracy Score: ",accuracy_score(predictions_NB, Test_Y)*100)
      reportNB = classification_report(Test_Y, predictions_NB)
      print("Classification Report:")
      print(reportNB)


    # Classifier - Algorithm - SVM
    # fit the training dataset on the classifier
    SVM = svm.SVC(C=1.0, kernel='linear', degree=3, gamma='auto')
    SVM.fit(Train_X_Tfidf,Train_Y)
    # predict the labels on validation dataset
    predictions_SVM = SVM.predict(Test_X_Tfidf)
    # Use accuracy_score function to get the accuracy
    print("- Support Vector Machine -")
    print("Accuracy Score: ",accuracy_score(predictions_SVM, Test_Y)*100)
    reportSVM = classification_report(Test_Y, predictions_SVM)
    print("Classification Report:")
    print(reportSVM)


def lemmatizer(texts):
    stopword_list = stopwords.words('dutch')
    nlp = spacy.load("nl_core_news_sm")

    cleaned_texts = []
    for text in texts:
        cleaned_text = text.replace("\n", "").strip()
        cleaned_texts.append(cleaned_text)
    docs = nlp.pipe(cleaned_texts)

    # Removes stopwords and non-alpha words
    cleaned_lemmas = []
    for doc in docs:
        lemmas = []
        for t in doc:
            if t.lemma_ not in stopword_list and t.lemma_.isalpha():
                lemmas.append(t.lemma_)
        cleaned_lemmas.append(" ".join(lemmas))
    return cleaned_lemmas


def predictAnnotation(Corpus, DesiredInput, DesiredOutput):
    # Split Dataset and encode labels
    Encoder = LabelEncoder()
    Output = Encoder.fit_transform(DesiredOutput)

    # Make vector with the tfidf values
    Tfidf_vect = TfidfVectorizer(ngram_range=(1,3), max_features=5000)
    Tfidf_vect.fit(DesiredInput)
    Input_Tfidf = Tfidf_vect.transform(DesiredInput)

    # Classifier - Algorithm - SVM
    # fit the training dataset on the classifier
    SVM = svm.SVC(C=1.0, kernel='linear', degree=3, gamma='auto')
    SVM.fit(Input_Tfidf, Output)
    # predict the labels on validation dataset
    predictions_SVM = SVM.predict(Input_Tfidf)
    return predictions_SVM


def main():
    np.random.seed(20012025)  # Setting seed for consistency
    Corpus = pd.read_csv('Cleaned1000annotations - New1000annotations.tsv.tsv', sep="\t")

    # Prints how variables are distributed
    print("\n\n\n --- Distribution Annotations ---")
    Distribution(Corpus)

    # Change all the text to lower case
    Corpus['LowerTokenizedText'] = [entry.lower() for entry in Corpus['TokenizedText']]

    # Create and print result Baseline Model
    print("\n\n\n --- Baseline Classifier ---")
    BaselineModel(Corpus)


    # --- Classifying Dog Whistles ---
    NB = True # We want a Naive Bayes Classifier
    # Create and print result, Raw Text to Dog Whistle Model
    print("\n\n\n --- Raw Text to Dog Whistle Classifier ---")
    DesiredInput = Corpus['LowerTokenizedText']
    DesiredOutput = Corpus['DogWhistle']
    TextToDW(Corpus, DesiredInput, DesiredOutput, NB)

    # Create and print result, Raw Text to Dog Whistle Model
    print("\n\n\n --- Lemmatized Text to Dog Whistle Classifier ---")
    # Remove Stop words, Non-Numeric and perfom Word Stemming/Lemmenting.
    Corpus['LemmatizedText'] = lemmatizer(Corpus['LowerTokenizedText'])
    DesiredInput = Corpus['LemmatizedText']
    DesiredOutput = Corpus['DogWhistle']
    TextToDW(Corpus, DesiredInput, DesiredOutput, NB)


    # --- Classifying Dog Whistles with Annotations---
    NB = False # We do not want a Naive Bayes Classifier
    # Create and print result, Raw Text + Annotations to Dog Whistle Model
    print("\n\n\n --- Raw Text + Annotations to Dog Whistle Classifier ---")
    # Take Relevancy and sentiment into account
    Corpus['RawTextAnnotations'] = Corpus['LowerTokenizedText'] + ' ' + Corpus['Relevancy'] + ' ' + Corpus['Sentiment']
    DesiredInput = Corpus['RawTextAnnotations']
    DesiredOutput = Corpus['DogWhistle']
    TextToDW(Corpus, DesiredInput, DesiredOutput, NB)

    # # --- Classifying Dog Whistles with Predicted Relevancy Annotations---

    # Create and print result, Raw Text to Relevancy Model
    print("\n\n\n --- Raw Text to Relevancy Classifier ---")
    DesiredInput = Corpus['LowerTokenizedText']
    DesiredOutput= Corpus['Relevancy']
    TextToDW(Corpus, DesiredInput, DesiredOutput, NB)

    # Predict for all messages, and save to column
    predictedRelevancy = predictAnnotation(Corpus, DesiredInput, DesiredOutput)
    Corpus['PredictedRelevancy'] = predictedRelevancy
    Corpus['TextPredictedRel'] = Corpus['LowerTokenizedText'] + ' ' + Corpus['PredictedRelevancy'].astype(str)

    # Create and print result, Raw Text to Relevancy to Dog Whistle Model
    print("\n\n\n --- Raw Text to Relevancy to Dog Whistle Classifier ---")
    DesiredInput = Corpus['TextPredictedRel']
    DesiredOutput= Corpus['DogWhistle']
    TextToDW(Corpus, DesiredInput, DesiredOutput, NB)

    # # --- Classifying Dog Whistles with Predicted Relevancy + Predicted Sentiment Annotations---
    # Create and print result, Raw Text & Predicted Relevancy to Predicted Sentiment Model
    print("\n\n\n --- Raw Text to Predicted Relevancy to Predicting Sentiment Classifier ---")
    DesiredInput = Corpus['TextPredictedRel']
    DesiredOutput= Corpus['Sentiment']
    TextToDW(Corpus, DesiredInput, DesiredOutput, NB)

    # Predict for all messages, and save to column
    PredictedSentiment = predictAnnotation(Corpus, DesiredInput, DesiredOutput)
    Corpus['PredictedSentiment'] = PredictedSentiment
    Corpus['TextPredictedRel&Sent'] = Corpus['TextPredictedRel'] + ' ' + Corpus['PredictedSentiment'].astype(str)

    # Create and print result, Raw Text to Predicted Relevancy to Predicted Sentiment to Dog Whistle Model
    print("\n\n\n --- Raw Text to Predicted Relevancy to predicting Sentiment to Dog Whistle Classifier ---")
    DesiredInput = Corpus['TextPredictedRel&Sent']
    DesiredOutput= Corpus['DogWhistle']
    TextToDW(Corpus, DesiredInput, DesiredOutput, NB)


if __name__ == "__main__":
    main()

