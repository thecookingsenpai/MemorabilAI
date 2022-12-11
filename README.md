# MemorabilAI

## A GPT3 based AI without constraints

## ..And with memory

### Introduction

MemorabilAI is an AI that aims to chat with humans using a natural language, thanks to the OpenAI GPT3 APIs (specifically, davinci-003 model).
Other than just using GPT3 to obtain answers, MemorabilAI implements a memory system that allows the user to memorize the most important answers given by the AI so that they will be remembered forever without need for fine tuning.

### Install

    git clone https://github.com//thecookingsenpai/MemorabilAI
    cd MemorabilAI
    pip3 install -r requirements.pip

Now move the memo.config.openai.config.example file removing the ".example" extension and edit it to insert your OpenAI API key (and your username if you want).

You can run the script by executing:

    python3 gui.py

### How to use

Use the GUI to chat with the AI. You can press "Remember" button anytime you want the AI to memorize the last exchange (aka the last interaction composed of your message and the AI answer). You can also edit manually memory.json file to:

- Specify some starting parameters in the "starting" section
- Edit, remove or add memories in the "memory" section.
