#Student Name:
# Ved Lad
#Date:
# April 20, 2026
#Title of Story:
# The Island OR Home Alone
#Description: 
# The Island: The story is about the user waking up ALONE after a plane crash on Isla Nublar.
#             They are completely alone — no other survivors, no buildings, no mansions, no other people.
#             They must survive in dense jungle and find a way to escape while avoiding dinosaurs. 
#
# Home Alone: The story is about the user home alone after coming home late, after a long day at work and hear strange noises around their home (scratching, someone walking, whispering, etc.).
#             He is completely alone — his phone does not work, nobody else is home, not even the neighbors are around. He is trapped inside his own home, with no way to call for help and no escape route.
#             He must survive the night while avoiding the unknown entity that is stalking him.
#
"""
Enhancements:
    - AI Used to generate the story, so everytime the game is launched, the story is always going to be abit different.
        - Makes the amount of endings, and choices basically infinity.
        - AI Error handling
    - Typewriter effect
    - 3 Choices per question
    - Clears screen between choices
    - Coice number/score counter
    - ASCII Art at end.
    - 2 Gamemode rather than 1
"""
#
# AI assistance used for helping me debug and get an model working through codehs.

import httplib2
import json
import subprocess
import time
import random
import sys

API_KEY = "<key>"
h = httplib2.Http()
url = "https://api.groq.com/openai/v1/chat/completions"

def typewriter_print(text, delay=0.03, margin=70, indent="  "):
    words = text.split()
    current_line_length = 0
    
    sys.stdout.write(indent) 
    for word in words:
        # If the word is too long for the current line, move to next
        if current_line_length + len(word) + 1 > margin:
            sys.stdout.write("\n" + indent)
            current_line_length = 0
            
        for char in word + " ":
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
            current_line_length += 1
    print()

# System prompts defined once and reused in every API call

SYSTEM_NARRATOR = {
    "role": "system",
    "content": """You are a narrator for a horror survival game finishing within 10 choices.
You MUST respond ONLY with a JSON object in this exact format, no extra text:
{
  "story": "the narrative here",
  "option1": "first choice",
  "option2": "second choice",
  "option3": "third choice"
}"""
}

# Conversation history — grows each turn so the AI remembers the full story
conversation_history = []

def build_setting1(name):
    # Builds the setting prompt using the player's real name
    return {
        "role": "system",
        "content": f"""The player's name is {name}. Use their name occasionally in the story.
The story is about {name} waking up ALONE after a plane crash on Isla Nublar (do not reveal this name).
They are completely alone — no other survivors, no buildings, no mansions, no other people.
They must survive in dense jungle and find a way to escape while avoiding dinosaurs.

STRICT RULES:
- Dinosaurs are ANIMALS only. No telepathy, no visions, no communication, no mystical elements whatsoever.
- NO magic, NO supernatural events, NO fantasy elements. Realistic survival horror only.
- {name} CAN and SHOULD die sometimes based on bad choices. Deaths should be graphic and final.
- When the story ends (death or escape), set option1 to "Play again", option2 to "Quit", option3 to "Play again".
- NEVER introduce mansions, buildings, ladies, or other people.
- ONLY dinosaurs, jungle, plane wreckage, and raw survival.
- The story MUST finish within 10 choices by either escape or death.
- Within these 10 choices, the {name} must get attacked atleast once.
- Make the horror feel real and tense. The island is dangerous and {name} is truly alone."""
    }

def ai_response1(user_choice, setting):
    # Add player's choice to conversation history
    conversation_history.append({
        "role": "user",
        "content": user_choice
    })

    payload = json.dumps({
        "model": "llama-3.1-8b-instant",
        "max_tokens": 512,
        "response_format": {"type": "json_object"},
        "messages": [SYSTEM_NARRATOR, setting] + conversation_history
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # Retry loop in case of rate limiting
    while True:
        response, content = h.request(url, method="POST", body=payload, headers=headers)
        result = json.loads(content)

        if "error" in result:
            error = result["error"]
            if error.get("code") == "rate_limit_exceeded":
                print("|n  Generating story, please wait...")
                time.sleep(20)
                continue  # Retry the request
            else:
                raise Exception("API error: " + error["message"])

        raw = result["choices"][0]["message"]["content"]
        data = json.loads(raw)

        # Add AI response to history so next turn has full context
        conversation_history.append({
            "role": "assistant",
            "content": raw
        })

        # Safe fallback values in case model skips a key
        story = data.get("story", "The jungle goes silent around you...")
        opt1  = data.get("option1", "Look around carefully")
        opt2  = data.get("option2", "Stay completely still")
        opt3  = data.get("option3", "Run in a random direction")

        return story, opt1, opt2, opt3

# Conversation history — grows each turn so the AI remembers the full story
conversation_history = []

def build_setting2(name):
    # Builds the setting prompt using the player's real name
    return {
        "role": "system",
        "content": f"""The player's name is {name}. Use their name occasionally in the story.
The story is about {name} home alone after coming home late, after a long day at work and hear strange noises around their home (scratching, someone walking, whispering, etc.).
He is completely alone — his phone does not work, nobody else is home, not even the neighbors are around. He is trapped inside his own home, with no way to call for help and no escape route.
He must survive the night while avoiding the unknown entity that is stalking him.

STRICT RULES:
- Only one entity. No telepathy, no visions, no communication, no mystical elements whatsoever.
- NO magic, NO supernatural events, NO fantasy elements. Realistic survival horror only.
- {name} CAN and SHOULD die sometimes based on bad choices. Deaths should be graphic and final.
- When the story ends (death or escape), set option1 to "Play again", option2 to "Quit", option3 to "Play again".
- NEVER introduce mansions, buildings, ladies, or other people.
- ONLY the entity, his home, and raw survival.
- The story MUST finish within 15 choices by either escape or death.
- Within these 15 choices, the {name} must get attacked at least twice.
- Make the horror feel real and tense. The home is dangerous and {name} is truly alone beside the entity."""
    }

def ai_response2(user_choice, setting):
    # Add player's choice to conversation history
    conversation_history.append({
        "role": "user",
        "content": user_choice
    })

    payload = json.dumps({
        "model": "llama-3.1-8b-instant",
        "max_tokens": 512,
        "response_format": {"type": "json_object"},
        "messages": [SYSTEM_NARRATOR, setting] + conversation_history
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # Retry loop in case of rate limiting
    while True:
        response, content = h.request(url, method="POST", body=payload, headers=headers)
        result = json.loads(content)

        if "error" in result:
            error = result["error"]
            if error.get("code") == "rate_limit_exceeded":
                print("|n  Generating story, please wait...")
                time.sleep(20)
                continue  # Retry the request
            else:
                raise Exception("API error: " + error["message"])

        raw = result["choices"][0]["message"]["content"]
        data = json.loads(raw)

        # Add AI response to history so next turn has full context
        conversation_history.append({
            "role": "assistant",
            "content": raw
        })

        # Safe fallback values in case model skips a key
        story = data.get("story", "He snuck up behind you and attacked!")
        opt1  = data.get("option1", "Dodge and run")
        opt2  = data.get("option2", "Try fighting back")
        opt3  = data.get("option3", "Accept your fate")

        return story, opt1, opt2, opt3

# Choice type of story
print("Welcome to Choose your Adventure Game!")
print("=========================================")
print("The goal is to survive the longest you can throughout the story.")
print("")
print("What type of story would you like to play?")
print("Options: The Island (1), Home Alone (2)")
story_type = int(input("    Enter your choice. (1,2): "))
gamemode1 = []
gamemode2 = []
if story_type == 1:
    gamemode1 = True
elif story_type == 2:
    gamemode2 = True

# --- Main Program ---

the_end = "   ~~~ THE END ~~~"

if gamemode1 == True:
    # Ask for player name — used in the story throughout (rubric requirement)
    subprocess.run("printf '\033c'", shell=True, check=True)
    print("""
        #########################################
        ############ The Island #################
        #########################################
        
    """)
    
    typewriter_print("  Your goal is to survive for as long as possible!.")

    typewriter_print("  You are alone. The jungle breathes around you.")
    typewriter_print("  Something is watching.")
    print("")

    typewriter_print("Before we begin... what is your name, survivor?")
    player_name = input("  > ")
    thanks = "  Thanks for playing, " + player_name + ". Stay off the island."

    # Outer play-again loop
    while True:

        # Reset conversation history for a fresh game
        conversation_history = []

        # Build the setting prompt with the player's name baked in
        SYSTEM_SETTING = build_setting1(player_name)

        # Generate the opening scene
        story, option1, option2, option3 = ai_response1(
            f"Begin the story. {player_name} wakes up after the crash.",
            SYSTEM_SETTING
        )

        num = 1

        # Inner game loop — runs until story ends
        while True:

            subprocess.run("printf '\033c'", shell=True, check=True)

            print("""
            #########################################
            ############ The Island #################
            #########################################
            """)

            typewriter_print(f"Choice {num}...", delay=0.1, indent="  ")

            # Print story in wrapped chunks for readability
            print("")
            typewriter_print(story, delay=0.04)
            print("")

            # Ending detected — AI signals end by setting option1 to "Play again"
            if option1.lower() in ["play again", "quit", "restart"]:
                score = f"You got a score of {num}!"
                # Ending: death or escape — story is over
                print(r"""
            .-~.                                               
        .-<|←→↓↑|:                                             
        |↱↱↕↔↱↲↓↲←,                                            
        .,,-⇨↱↱←↑↱⇩.                                           
        .|⇨>~:.|»»↕⇨^,                                        
            .,,,/←↔↕↱↱↓~.                                     
            ,>/↕↑/|⇦↔↱↱↑-.                                   
            ,~~<</>>⇨↕↲↱↲↓/,                                 
                .-^^~~<←↲↲»»↑-                                
                >↑↲»»↱↱↓-$//[]\                               
                -/>⇧←↔↕↔↲↱↑↔↓↔^.                             
                ,<⇨↔↕⇧:./↔^-⇩→↔⇩~                            
                    ,⇩↔/  .⇦↓/-|⇩↕←:.                          
                    ^⇧~   .⇦↓|:~<|↑←~.                        
                    :⇧>      :←|,^⇨↑↓←~..                     
                    <⇨>        |↱,,~|⇨→↓⇦,                    
                    .⇧⇦,        .↲:  ,:~<>|←→⇩<:.              
                .,-~⇧←<.      ..-↔:     ..,.:~>|||||||///><-.  
                .-<<^:        ,~^,                  ......,~.  
            
                """)
                for char in score:
                    print(char, end='', flush=True)
                    time.sleep(0.1)
                for char in the_end:
                    print(char, end='', flush=True)
                    time.sleep(0.1)  
                again = input("  Would you like to play again? (yes / no): ").strip().lower()
                if again == "yes":
                    break 
                else:
                    for char in thanks:
                        print(char, end='', flush=True)
                        time.sleep(0.1)
                    exit()

            # Show the three options (rubric: at least one prompt must have 3+ options)
            print("") # Space above choices
            typewriter_print(f"1: {option1}", delay=0.02)
            typewriter_print(f"2: {option2}", delay=0.02)
            typewriter_print(f"3: {option3}", delay=0.02)

            # Get player input
            try:
                user = int(input("  What is your choice? (1 / 2 / 3): ").strip())
            except ValueError:
                user = 1  
            
            # For the while loo[]
            loop = True
            
            # Map choice to the selected option text
            while loop:
                if user <= 1:
                    chosen = option1
                    loop = False
                elif user == 2:
                    chosen = option2
                    loop = False
                elif user >= 3:
                    chosen = option3
                    loop = False
                else:
                    print("Please Choose a valid choice.")
                    user = int(input("Choice (1,2,3): "))

            # Get next story beat from AI
            story, option1, option2, option3 = ai_response1(chosen, SYSTEM_SETTING)
            num += 1


elif gamemode2 == True:
    subprocess.run("printf '\033c'", shell=True, check=True)
    
    print("""
        #########################################
        ############ Home Alone #################
        #########################################
    """)

    typewriter_print("  Your goal is to survive for as long as possible!.")

    typewriter_print("  You are alone. The house creaks around you.")
    typewriter_print("  Something is watching.")
    print("")

    typewriter_print("Before we begin... what is your name, survivor?")
    player_name = input("  > ")
    thanks = "  Thanks for playing, " + player_name + ". Stay out... This place is no longer yours."

    # Outer play-again loop
    while True:

        # Reset conversation history for a fresh game
        conversation_history = []

        # Build the setting prompt with the player's name baked in
        SYSTEM_SETTING = build_setting2(player_name)

        # Generate the opening scene
        story, option1, option2, option3 = ai_response2(
            f"Begin the story. {player_name} finally arrives home after a long day at work and hears strange noises around the house.",
            SYSTEM_SETTING
        )

        num = 1

        # Inner game loop — runs until story ends
        while True:

            subprocess.run("printf '\033c'", shell=True, check=True)

            print("""
            #########################################
            ############## Home Alone ###############
            #########################################
            """)

            typewriter_print(f"Choice {num}...", delay=0.1, indent="  ")

            # Print story in wrapped chunks for readability
            print("")
            typewriter_print(story, delay=0.04)

            # Ending detected — AI signals end by setting option1 to "Play again"
            if option1.lower() in ["play again", "quit", "restart"]:
                score = f"You got a score of {num}!"
                # Ending: death or escape — story is over
                print("""
                                  
                                                I|jt|ft-'                            
                                       l+    ,v!.       .,(_.                         
                                      ,t-i 'x^             .r:                        
                                '    ,/ ^?-1"    ,|nxxY:     )i                       
                            ?xl~?  [-')(.)~   Ic+.   .|!~_`'.r' '.                   
                             :t. ?-/,.)l<}'_['   .?ff|"^:-:.}{+x;lt+.                
                              ",-]`"u'  ![,.rl        "1<  '^^..   :/                
                              .</:`}_     .1~."tI.      ,-i)-.t{|{_?x:               
                            ^>|,`~["        "t!.;1>'     [(` <{       '               
                          ,|] '~1:   .;ll:.   "|>``{)'     '??                        
                           +}||.    +|^!];1!    ")((;    ^~1"                         
                             ^|    i/><}/><f:   '[)>>><-{~'                           
                         "i`  f    ;1  !] `{,   I?` .]                                
                         _|[' {;    !{+]|_}:   'i? ,|v.                               
                        '->:1_;1. .. .':,. ..'.'<?-]"l)..                             
                        <?''',}/..'''''''''..'':|?:''')i..                            
                       l{'.   '?!  . . ...   . :1.    '{!.                            
                     +n"      I}     ^f1^    .+<      :n<                            
                    ^/i![ ~}j]?;['   ;|^;}I   '|.+|||: ~-<]"                          
                    !. :[^~~x{Y'~< `|v   ,/)` "(Itv+t''/  ^:.                         
                        <_.f<r>?<-   n   ^-;  (:i{[/?.<?                              
                        l-`<|1l,;-"  n   ^-;  x."<}/, r                               
                         ->      ->  n   ^-; >]      <]                               
                         <+'     _<  n   ^-; r.      r                                
                       I/?)I.    "]: u..."?;'r      >}~f!                             
                   "|j;'  .''''''''''''''''''''''''''   .!/}`                         
                   '''^?r-.                           }x_^'''                         
                          +1` ']xnnnx_   `]xunnr-' ^r,                                
                            c{        '1{.       `1`                                 

                """)
                for char in score:
                    print(char, end='', flush=True)
                    time.sleep(0.1)
                for char in the_end:
                    print(char, end='', flush=True)
                    time.sleep(0.1)  
                again = input("  Would you like to play again? (yes / no): ").strip().lower()
                if again == "yes":
                    break 
                else:
                    for char in thanks:
                        print(char, end='', flush=True)
                        time.sleep(0.1)
                    exit()

            # Show the three options (rubric: at least one prompt must have 3+ options)
            option_one = "  1: " + option1
            option_two = "  2: " + option2
            option_three = "  3: " + option3
            
            print("") # Space above choices
            typewriter_print(f"1: {option1}", delay=0.02)
            typewriter_print(f"2: {option2}", delay=0.02)
            typewriter_print(f"3: {option3}", delay=0.02)

            # Get player input
            try:
                user = int(input("  What is your choice? (1 / 2 / 3): ").strip())
            except ValueError:
                user = 1
            
            # For the while loo[]
            loop = True
            
            # Map choice to the selected option text
            while loop:
                if user <= 1:
                    chosen = option1
                    loop = False
                elif user == 2:
                    chosen = option2
                    loop = False
                elif user >= 3:
                    chosen = option3
                    loop = False
                else:
                    print("Please Choose a valid choice.")
                    user = input("Choice (1,2,3): ")

            # Get next story beat from AI
            story, option1, option2, option3 = ai_response2(chosen, SYSTEM_SETTING)
            num += 1
