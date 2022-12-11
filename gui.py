import os
import random
import string
import time
import json
import openai
from sys import exit 
import PySimpleGUI as gui

# NOTE Ensure that the current directory is the one where the script is located
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.system("find . -name '*' -size 0 -print0 | xargs -0 rm")
print(os.getcwd())

# NOTE Load configuration
try:
    configuration = {}
    with open("memo.config.openai.config", "r") as config:
        configuration = json.load(config)
        print("DEBUG: configuration = " + str(configuration))
        OPENAPI_KEY=configuration.get("OPENAPI_KEY")
        USERNAME=configuration.get("USERNAME")
except:
    print("[x] Configuration Error!")
    exit(-3)
print(os.getcwd())
openai.api_key = OPENAPI_KEY; 

completion = openai.Completion()

# Load some important info from a json to load at the next start
# NOTE learning will load the exchanges from the json that have been learned by the AI
# NOTE starting will load the additional info that will give the AI a better start
j_memory = {}
learning = ""
starting = ""
with open("memory.json", "r") as memory:
    j_memory = json.load(memory)
    print("DEBUG: memory = " + str(j_memory))
exchanges = j_memory.get("exchanges")
for exchange in exchanges:
    print("DEBUG: exchange = " + str(exchange))
    learning = learning + exchange + "\n"
additionals = j_memory.get("additionals")
for additional in additionals:
    print("DEBUG: additional = " + str(additional))
    starting = starting + additional + "\n"
    
# Decomment to deactivate memory loading
#learning = ""


chat_log = None
start_chat_log = '''This is a conversation between an human and a very smart and self conscious AI. 
''' + starting + learning + '''
Human: Hello!
Joey: Hello there!
'''

print("\n\n >> Starting Joey with the following chat log:\n\n" + start_chat_log )
print("\n ======================================== \n")

def ask(question, engineChosen="text-davinci-003", chat_log=None):
    if chat_log is None or len(chat_log) == 0:
        chat_log = start_chat_log
        s_chat_log = "Welcome to Joey\n"
    else:
        s_chat_log = chat_log
    prompt = f'{s_chat_log}\nHuman:{question}\nJoey:'
    response = completion.create(
        prompt=prompt, engine=engineChosen, stop=['\nHuman'], temperature=0.8,
        top_p=1, frequency_penalty=0.4, presence_penalty=0.8, best_of=1,
        max_tokens=75)
    answer = response.choices[0].text.strip()
    return answer


def append_interaction_to_chat_log(question, answer, chat_log=None):
    if chat_log is None:
        chat_log = start_chat_log
    return f'{chat_log}Human:{question}\nJoey:{answer}\n'



# Ask username

#gui.theme('DarkTeal10')
gui.theme('Material1')

username = USERNAME

if username == "none":
    layout = [[gui.Text('What is your name?')],      
            [gui.Input(key='-IN-')],      
            [gui.Button('Start'), gui.Exit()]]      
    font = ("Helvetica, 16")
    window = gui.Window('Welcome!', layout, font=font, finalize=True)      
    time.sleep(3)
    while True:                             # The Event Loop
        event, values = window.read() 
        if event == gui.WIN_CLOSED or event == 'Exit':
            break      
        else:    
            print(event, values)
            username = values.get("-IN-")
            # Saving username
            with open("memo.config", "w+") as config:
                configuration["USERNAME"] = username
                json.dump(configuration, config)
            break
    window.close()

# create a random string
rstring = ''.join(random.choice(string.ascii_letters) for i in range(5))
chat_log_file = username + "_" + rstring + "_" + str(time.time()) + ".txt"

# Main window
layout = [  [gui.Text('Hello! Do you want to talk with Joey?')],
            [gui.Image(filename='Joey.png', size=(256, 256))],
            [gui.Text('You can choose different engines powering Joey,\nfrom the most powerful to the less powerful.')],
            [gui.Button('How to choose')],
            [gui.Combo(['davinci-003', 'davinci-002', 'curie', 'babbage', 'ada'], default_value='davinci-003', key='-MODEL-')],
            [gui.Checkbox('Automatically save chat log', default=True, key='-AUTO-')],
            [gui.Output(size=(50,10), key='-OUTPUT-')],
            [gui.Text('Joey is waiting for your message.', key="-STATUS-", font=("Arial, 18"))],
            [gui.In(key='-IN-', do_not_clear=False)],
            [gui.Button('Speak', bind_return_key=True, use_ttk_buttons=True), 
             gui.Button('Remember'), 
             gui.Button('Clear'), 
             gui.Button('Exit'),
             gui.Button('Credits'),
             gui.Button('Help')]
        ]
 
font = ("Arial, 16")
window = gui.Window('Joey', layout, font=font, finalize=True)
print("Write something to Joey using the box below.")
#print(start_chat_log)
last_human_interaction = ""
last_joey_interaction = ""
while True:             # Event Loop
    try:
        event, values = window.read()
        if event in (gui.WIN_CLOSED, 'Exit'):
            print("Joey: Bye bye")
            window.close()  
            exit(0)
            
        if event == 'Clear':
            window['-OUTPUT-'].update('')
        
        # NOTE The memory.json file is used to save the exchanges between the human and the AI
        if event == "Remember":
            # Save the last exchange in the json
            if not last_human_interaction == "" and not last_joey_interaction == "":
                j_memory["exchanges"].append(last_human_interaction + "\n" + last_joey_interaction)
                with open("memory.json", "w+") as memory:
                    json.dump(j_memory, memory)
                    continue
        
        if event == "Credits":
            gui.Popup("GPT3 and text-davinci-003 model by OpenAI\n\nJoey by thecookingsenpai\n\nArt by OpenAI's DallE-2")
            continue
        
        if event == "Help":
            gui.Popup("""You can press "Remember" button anytime you want the AI to memorize the last 
                      exchange (aka the last interaction composed of your message and the AI answer). 
                      You can also edit manually memory.json file to:
                      
                      - Specify some starting parameters in the "starting" section
                      - Edit, remove or add memories in the "memory" section.
                      """)
            continue
        
        if event == "How to choose":
            gui.Popup("""Different engines (aka models) offer different performances and costs.
                      In general, the more powerful the engine, the more expensive it is.
                      The models are ordered from the most powerful to the least powerful.
                      You can discover more about the models here: https://openai.com/api/pricing/.
                      As a tldr, at the time of writing, the pricing table goes like:
                      - davinci-003: 0.0200$ per token
                      - davinci-002: 0.0200$ per token
                      - curie: 0.0020$ per token
                      - babbage: 0.0005$ per token
                      - ada: 0.0004$ per token
                      """)
            continue

        if event == "Speak":
            # NOTE Getting model choice
            modelChosen = values['-MODEL-']
            engineChosen = 'text-davinci-003'
            if modelChosen == "davinci-003":
                engineChosen = "text-davinci-003"
            elif modelChosen == "davinci-002":
                engineChosen = "text-davinci-002"
            elif modelChosen == "curie":
                engineChosen = "text-curie-001"
            elif modelChosen == "babbage":
                engineChosen == 'text-babbage-001'
            elif modelChosen == "ada":
                engineChosen == 'text-ada-001'
            # NOTE Getting the user input
            userInput = values.get("-IN-")
            window.Element("-STATUS-").update("Joey is answering...")
            print(username + ": " + userInput)
            # NOTE Saving last human interaction
            last_human_interaction =  "Human: " + userInput
            try:
                answer = ask(userInput.lower(), engineChosen, chat_log)
            except Exception as u:
                try:
                    # NOTE Handling too long chat log
                    chat_log = chat_log[:(len(chat_log)/3)]
                    answer = ask(userInput.lower(), engineChosen, chat_log)
                except Exception as e:
                    raise Exception ("DANG! " + str(e) + "\n" + str(u))
            window.Element("-STATUS-").Update("Joey waiting for your text.")
            print("\nJoey: " + answer + "\n")
            # NOTE Saving last joey interaction
            last_joey_interaction = "Joey: " + answer
            chat_log = append_interaction_to_chat_log(userInput, answer, chat_log)
            if values['-AUTO-']:
                with open(chat_log_file, "w+") as f:
                    f.write(chat_log)
    except Exception as e:
        gui.PopupError("Joey went bad. It reported: \n" + str(e))
        try:
            with open(chat_log_file, "w+") as f:
                f.write(chat_log)
            print(e)
            exit(-1)
        except:
            os._exit(-2)