# BookReader

BookReader is a simple Python script using the Google Gemini API which bulk summarizes PDFs and ePUBs in a method that would give you more detailed summaries than had you just put the entire book into the prompter. It also exports these summaries as Markdown files so you can easily add them in bulk to an Obsidian or Notion database. 

# How It Works

There are two phases to the program:

1. Text Segmentation: For each PDF/ePub (sorry djvu, I don't use you!) we segment the book into roughly 10 to 25 pages -- an amount that, heuristically speaking, can be read by any AI model without coming up on context limits. These segments are exported as text files for our next step.

2. AI Processing: For each text file, we ask Gemini to give us a bullet point list of key takeaways from the segment. I've found that asking specifically for a bullet list rather than a summarization makes the output 1) more easily readable, and 2) makes the AI look into the text for more details than it would otherwise. 


# Disclaimers

Currently attached as the model here is Gemini 2.0 Flash. This is obscenely overkill for what this script is trying to accomplish. The main reason for me doing so is that the model is currently completely free in its experimental phase and so you won't have any costs associated with running this script. HOWEVER, if you are reading this at some point in the future, I can not guarantee that 1) this model is still free, and 2) I remembered to change the repo to a new model. Honestly you can do anything in this script with a 7B local model no problem, but I'm on a shitty Macbook Air as of current and I want my summarizes NOW. Also I haven't tried out the Google API yet so I wanted to make something with it. 

Another thing is rate limits. You can (currently) ask Gemini for 10 requests per minute without being limited. This script is naturally slow enough that I didn't have any issue with this, but it might be something to keep in mind if you're using a different model or service. 


# TODO

- Create a version that just uses a local model


# CHANGELOG 

2025/02/22
- Added Pycryptdome to required packages for PDFs that had AES Encryption turned on
- Added a sleep timer to the AI summary portion that makes it less likely to trigger a quota limit
- Updated the prompt so that it automatically kills gibberish/useless excerpts