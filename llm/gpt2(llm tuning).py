import pandas as pd
from datasets import Dataset, DatasetDict, load_metric
from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

# Load the dataset
data = pd.read_json("resumes_dataset.json")

# Combine all fields into a single string for fine-tuning
data['text'] = data.apply(lambda row: f"Name: {row['name']}\nSkills: {', '.join(row['skills'])}\nExperience: {row['experience']}\nEducation: {row['education']}\nProjects: {', '.join(row['projects'])}\n\n", axis=1)

# Split the data into train and evaluation sets
train_texts, eval_texts = train_test_split(data['text'], test_size=0.1, random_state=42)

# Convert to Hugging Face DatasetDict
dataset = DatasetDict({
    'train': Dataset.from_pandas(pd.DataFrame(train_texts, columns=['text'])),
    'eval': Dataset.from_pandas(pd.DataFrame(eval_texts, columns=['text']))
})

# Load the GPT-2 tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Set the pad token
tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = tokenizer.pad_token_id

# Tokenize the dataset
def tokenize_function(examples):
    return tokenizer(examples['text'], padding="max_length", truncation=True, max_length=512)

tokenized_datasets = dataset.map(tokenize_function, batched=True, remove_columns=['text'])

# Prepare inputs for training and evaluation
def format_for_lm_labels(examples):
    examples['labels'] = examples['input_ids'].copy()
    return examples

tokenized_datasets = tokenized_datasets.map(format_for_lm_labels)

# Set up training arguments
training_args = TrainingArguments(
    output_dir="./results",
    overwrite_output_dir=True,
    num_train_epochs=4,
    per_device_train_batch_size=3,
    save_steps=10_000,
    learning_rate=3e-4,
    save_total_limit=2,
    logging_dir="./logs",
    logging_steps=200,
)

# Initialize Trainer with both train and eval datasets
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    eval_dataset=tokenized_datasets['eval'],
)

# Fine-tune the model
trainer.train()

# Save the model and tokenizer
model.save_pretrained("./fine-tuned-model")
tokenizer.save_pretrained("./fine-tuned-tokenizer")

print("Fine-tuning complete. Model and tokenizer saved.")

# Evaluate the model
eval_results = trainer.evaluate()
print("Evaluation Results:", eval_results)

# Initialize ROUGE metric
rouge = load_metric("rouge")

# BLEU score calculation
smoothing_function = SmoothingFunction().method4

# Function to tokenize text for BLEU and ROUGE
def tokenize_text(text):
    return tokenizer.convert_ids_to_tokens(tokenizer.encode(text, max_length=512, truncation=True))

# Ensure you have a valid eval_texts sample
if not eval_texts.empty:
    reference_text = eval_texts.iloc[0]
    reference = reference_text.split()
    
    input_text = reference_text
    inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    outputs = model.generate(**inputs, max_length=512)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    hypothesis = generated_text.split()
    
    # Compute BLEU score
    bleu_score = sentence_bleu([reference], hypothesis, smoothing_function=smoothing_function)
    print(f"BLEU score: {bleu_score:.4f}")

    # Compute ROUGE score
    rouge_results = rouge.compute(predictions=[generated_text], references=[reference_text])
    print("ROUGE scores:", rouge_results)

else:
    print("Evaluation set is empty; cannot compute BLEU or ROUGE scores.")
