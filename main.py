"""
The main function for running the card simulator. It essentially puts you in a loop where
you input commands.

All possible commands with use cases are as follows
play int1 int2 ... int_n
    int1 - The index of the card which you wish to play. If it's the first card in
        your hand, this number would be 0, if it's the second card, it'd be 1.
    int2 - The card you wish to target. It's the index of said card in the target
        array. You can never mistarget a card, but targeting is less intuitive now
    int3... int_n - Extra targets, as some cards target multiple cards

attack int1 ... int_n
    int1... int_n - The cards which you wish to bring to the frontline. They are integers
    reflecting the index of their location in your bench. This is responded to with defenders.
    The command for defenders looks like:
int1 int2 ... int_n
    int1 - The card which you wish to bring to the frontline - its index in the bench
    int2 - The position which you wish the card to have. You choose which card blocks which
        attacker
    int3 - Card
    int4 - Position
    This pattern continues, with every other argument alternating between being a card, and
    the position where we are placing said card
    Example:
        0 1 1 2 2 0
    This command takes card at index 0, and places it at position 1. Then the card at index 1
    goes to position 2, and the card at index 2 goes to position 0. Assume the enemy is attacking
    with 5 attackers
    Another way to write this is:
        Frontline = [None]*5
        Frontline[1] = Bench[0]
        Frontline[2] = Bench[1]
        Frontline[0] = Bench[2]
    The frontline is now
        [Minion, Minion, Minion, None, None]
    There can be empty spaces when defending. This simply means the attacker attacks the nexus

pass
    Passes the turn for the current active player


---Help Commands---

print
    Prints the board state for the player (not in a good state yet)

moves
    Prints out all legal moves which the player can perform. I.e. play 0 1, etc.

---Debug Commands---

switch
    Switches which player is currently acting

draw int
    int - The index of the player which we wish to have draw a card. 0 or 1, as there are
        only 2 players
    Forces the player to draw a card

debug
    Enters debug mode

quit
    Exits the program

dump
    Dumps the gamestate to a file, using pickle. Pickle can load the gamestate too. Cool tool

load
    Ideally would load a gamestate, but sadly we can't do that, because I'm dumb
"""
import pdb
import game
import pickle

CARD_DATABASE = "databases/carddb.json"
EFFECT_DATABASE = "databases/effectdb.json"
DECK_1 = "default.deck"
DECK_2 = "default.deck"

def print_card(cardInfo):
    for key, value in cardInfo.items():
        print ("\t",key,": ",value)

    pass

def player_turn(gameObject):
    isPlayerDone = False
    while(isPlayerDone == False):
        command = str(input())
        command = command.split()


# Actions
        if (command[0] == "attack"):
            print("preparing attackers")
            command.pop(0)
            for i in range (len(command)):
                command[i] = int(command[i])
            gameObject.prepare_attack(command)

            print("please declare defenders...")
            command = str(input())
            command = command.split()
            for i in range (len(command)):
                command[i] = int(command[i])

            gameObject.prepare_defense(command)

        if (command[0] == "play"):
            if (len(command) == 2):
                gameObject.play_card(int(command[1]))
            if (len(command) == 3):
                gameObject.play_card(int(command[1]), int(command[2]))

        if (command[0] == "pass"):
            gameObject.pass_turn()

# Help commands

        if (command[0] == "print"):
            print("printing board...")
            for i in range(2):
                print(gameObject.players[i].name)
                print("health: ", gameObject.players[i].health)
                print("mana: ", gameObject.players[i].mana)
                print("bench: ", gameObject.players[i].bench.list)

                for j in range(len(gameObject.players[i].bench.list)):
                    print_card(gameObject.players[i].bench.list[j].info())

                print("front line: ", gameObject.players[i].frontline.list)
                print("hand: ", gameObject.players[i].hand.list)
                print()

        if (command[0] == "moves"):
            print("printing all legal moves...")
            decisionSpace = gameObject.list_all_moves()
            print(decisionSpace["playable cards"])
            print(decisionSpace["target list"])

# debug commands
        if (command[0] == "switch"):
            print("Switching active player")
            gameObject.switch_active_player()

        if (command[0] == "draw"):
            if (len(command) < 2):
                print("invalid command")
            gameObject.draw_card(int(command[1]))

        if (command[0] == "debug"):
            pdb.set_trace()

        if (command[0] == "quit"):
            isPlayerDone = True

        if (command[0] == "dump"):
            fileName = "gamestate.dump"
            if (len(command) > 1):
                fileName = command[1]
            outFile = open(fileName, 'wb')
            pickle.dump(gameObject, outFile)
            outFile.close()
            print("saved game state to ", fileName)
            pass

        if (command[0] == "load"):
            #blank for now
            pass

        pass
    return

"""
Main function
"""
#setup
gameObject = game.Game()
gameObject.import_effects(EFFECT_DATABASE)
gameObject.import_database(CARD_DATABASE)


decks = []
deck1 = deck2 = ""
deck1 = str(input("Please input deck 1\n"))
deck2 = str(input("Please input deck 2\n"))
if (deck1 == "" or deck2 == ""):
    decks.append(DECK_1)
    decks.append(DECK_2)
else:
    decks.append(deck1)
    decks.append(deck2)

for i in range(2):
    gameObject.create_deck(decks[i], i)

#game loop
isGameDone = False
while (isGameDone == False):
    isGameDone = player_turn(gameObject)


