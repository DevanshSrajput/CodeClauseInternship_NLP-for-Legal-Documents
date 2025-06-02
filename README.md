# 🦅 LegalEase: Your AI Legal Document Sidekick 🦅

[![Built with Python](https://img.shields.io/badge/Built_with-Python-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Powered by AI](https://img.shields.io/badge/Powered_by-AI-orange?style=for-the-badge&logo=openai)](https://openai.com/)
[![Built with Streamlit](https://img.shields.io/badge/Built_with-Streamlit-red?style=for-the-badge&logo=streamlit)](https://streamlit.io/)

> **"Legal documents don't have to be scary. Let our AI make them a little less... legally binding to your time."**

## 🧙‍♂️ What Sorcery Is This?

LegalEase is your magical companion for navigating the arcane texts of the legal realm! Upload your contracts, agreements, and court filings, then watch as our AI extracts the secrets hidden within - summaries, key clauses, and important entities, all without the need for expensive legal potions!

## Sample Video:
```
 https://drive.google.com/file/d/1XUtM_4KlBlZNUr0qQzCdU3lgspI9AQkK/view?usp=sharing
```

## ✨ Features That'll Make Your Paralegal Jealous

- 📝 **Document Scanning**: Extracts text from PDFs, DOCX, and TXT files faster than a law student on coffee
- 🔍 **AI-Powered Analysis**: Identifies document types automagically
- 📋 **Smart Summarization**: Creates concise summaries that won't put you to sleep
- 🧩 **Entity Extraction**: Finds people, organizations, dates, and monetary values like a detective on a sugar rush
- 📜 **Clause Identification**: Highlights important clauses and rates them by importance
- 🔎 **Document Search**: Find exactly what you need without developing carpal tunnel

## 🛠️ Setup Your Legal Laboratory (Installation)

### Step 1: Clone this magical repository
```bash
git clone https://github.com/yourusername/legalease.git
cd legalease
```
### Step 2: Create a virtual environment (VERY IMPORTANT)
# For Windows wizards
```
python -m venv venv
venv\Scripts\activate
```
# For Linux/Mac sorcerers

```
python3 -m venv venv
source venv/bin/activate
```
### Step 3: Install the magical dependencies
```
pip install -r requirements.txt
```
### Step 4: Download the required language model
```
python -m spacy download en_core_web_lg
```
### 🚀 Launch Your Legal Assistant
```
streamlit run app.py
```
Navigate to http://localhost:8501 and behold your new legal assistant!

## 📂 Project Structure (For the Curious Minds)
```
legalease/
├── app.py                  # The main spell (Streamlit application)
├── pages/                  # Different magical chambers (Streamlit pages)
│   ├── 1_Upload.py         # For summoning new documents
│   ├── 2_Document_View.py  # For studying the ancient texts
│   └── 3_About.py          # The lore behind our magic
├── backend/                # Where the real magic happens
│   ├── processors/         # Document processing spells
│   └── database/           # Document storage enchantments
├── data/                   # Your growing collection of legal scrolls
│   ├── documents/          # The original texts
│   └── analyses/           # The decoded wisdom
└── requirements.txt        # The list of magical ingredients
```
## 🧙‍♂️ Using Your New Legal Assistant
1. Upload: Summon your legal documents through the portal
2. Process: Cast the processing spell with a single click
3. Analyze: Observe as the AI reads the document and reveals its secrets
4. Review: Explore summaries, key clauses, and entities extracted from the document
## 🔮 Technical Magic Behind the Scenes
- **Python:** The primary magical language
- **Streamlit:** For crafting our user-friendly interface
- **spaCy:** For understanding the human language of law
- **Transformers (BART):** For summarizing even the most verbose legal jargon
- **PyMuPDF & python-docx:** For deciphering various document formats
## 🛑 How to Stop the Magic
When you're done with your legal wizardry, simply press ```Ctrl+C``` in your terminal window or close the terminal to shut down the server.
## ⚠️ Warning for Apprentice Wizards
This tool is for educational and informational purposes only. While it can help you understand legal documents, it's not a replacement for a professional legal wizard (lawyer). Always consult with qualified legal professionals for important matters!
#### ***"The first rule of Fight Club is... wait, wrong document. The first rule of LegalEase is to make legal documents less painful!"***

Happy analyzing! 📜⚖️✨
