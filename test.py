from transformers import pipeline

classifier = pipeline("text-classification", model="bert-base-uncased")
print(classifier("This product is amazing. A++++++ seller!!!"))
