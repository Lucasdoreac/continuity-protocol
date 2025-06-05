"""
Install required language models for semantic analysis
"""

import subprocess
import sys
import os
import logging

logger = logging.getLogger("continuity.utils.install_models")

def install_models():
    """Install required language models for semantic analysis."""
    print("Installing language models for semantic analysis...")
    
    # Models to install
    spacy_models = [
        "en_core_web_sm",
        "pt_core_news_sm",
        "es_core_news_sm",
        "fr_core_news_sm",
        "de_core_news_sm",
        "it_core_news_sm"
    ]
    
    # Install each model
    for model in spacy_models:
        print(f"Installing {model}...")
        try:
            subprocess.check_call([sys.executable, "-m", "spacy", "download", model])
            print(f"✅ {model} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {model}: {e}")
    
    # Install sentence-transformers
    try:
        print("Installing sentence-transformers...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "sentence-transformers"])
        print("✅ sentence-transformers installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install sentence-transformers: {e}")
    
    print("Installation complete!")

if __name__ == "__main__":
    install_models()
