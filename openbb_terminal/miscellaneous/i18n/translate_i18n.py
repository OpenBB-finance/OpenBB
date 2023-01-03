# pip install transformers sentencepiece
# pip install sacremoses

import yaml
from transformers import pipeline
from tqdm import tqdm

languages = {
    "es": "Helsinki-NLP/opus-mt-en-es",
    "fr": "Helsinki-NLP/opus-mt-en-fr",
    "it": "Helsinki-NLP/opus-mt-en-it",
    "pt": "Helsinki-NLP/opus-mt-tc-big-en-pt",
    "zh": "Helsinki-NLP/opus-mt-en-zh",
    "ja": "Helsinki-NLP/opus-tatoeba-en-ja",
    "ru": "Helsinki-NLP/opus-mt-en-ru",
    "ar": "Helsinki-NLP/opus-mt-tc-big-en-ar",
    "hi": "Helsinki-NLP/opus-mt-en-hi",
    "id": "Helsinki-NLP/opus-mt-en-id",
}

# Load the i18n.yml file
with open("en.yml", "r") as stream:
    try:
        file_content = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# Extract the English content from the file
english_content = file_content["en"]

for language, url in languages.items():
    print(f"Translating: {language}")
    # Initialize the translation pipeline

    translate_pipeline = pipeline(f"translation_en_to_{language}", model=url)
    # Initialize the dictionary for the translations
    final_translations = {}

    # Iterate through the English content and translate each item into Spanish
    for key, value in tqdm(english_content.items()):
        # Use the translate_pipeline to translate the value
        translated = translate_pipeline(
            value, max_length=1024, top_k=1, top_p=1, temperature=1
        )[0]["translation_text"]
        # Add the translated value to the Spanish translations dictionary using the original key
        final_translations[key] = translated

    # Save the Spanish translations to the i18n_es.yml file
    with open(f"{language}.yml", "w") as outfile:
        yaml.dump(
            {language: final_translations},
            outfile,
            default_flow_style=False,
            allow_unicode=True,
        )
