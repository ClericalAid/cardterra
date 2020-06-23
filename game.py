"""
This module implements the main game object. The game object contains all the information
relevant to the game state. That is it contains the players, and the players in turn
keep track of their own boards, decks, hands, graveyard, etc.

It also keeps track of which player is the attacker, whose turn it is to act, when to
continue to the next turn.

The gamestate is designed to contain everything. For debugging purposes, the game object
can be dumped and analyzed further.

ObservableList
A list which supports observers, and can notify said observers of changes to the list.
Objects which inherit from observable lists:
    Hand
    Deck
    Graveyard
    Bench
    Frontline
As can be seen, all of these objects can have triggers. I.e. a card is drawn, a card
is summoned, a card dies, etc.

Player
The player object

Game
The primary game object
"""
import card
import copy
import helper

class ObservableList:
    """
    ObservableList implements a list which broadcasts information to subscribed subjects. It 
    wraps a list, and also keeps track of observers, and updates them accordingly.

    Information broadcasted is important for cards to keep up-to-date with their available
    targets. It's also useful for cards who have trigger effects which depend on cards being
    added or removed from the hand, field, etc.

    For example, you summon a card to the field. Then you buff it with a spell card. In
    order to buff the newly summoned card, the buff spell card needed to be updated with the
    fact that a new valid target has emerged. In a similar vein, you might have a card that
    says "if an ally is summoned, give me 1/1". This means that it needs to be aware of
    when a new card is summoned to your side of the field. We therefore, needed a class
    which expanded upon lists in the sense that it handled observers.

    Member variables:
        list - The list which we are wrapping
        targetObservers - A list of observers which need to keep track of valid targets for
            targeted abilities. I.e. buff an ally monster by 1/1
        triggerObservers - A lit of observers whch keeps track of valid targets for their
            triggers. I.e. when an ally takes damage
    """
    def __init__(self):
        self.list = []
        self.targetObservers = []
        self.triggerObservers = []
        pass

    def add_target_observer(self, observer):
        self.targetObservers.append(observer)
        observer.receive_list(self.list)

    def remove_target_observer(self, observer):
        self.targetObservers.remove(observer)

    def append(self, newObject):
        """
        Adds a new object to the end of the list, but also notifies observers of the change
        """
        self.list.append(newObject)
        for observer in self.targetObservers:
            observer.add_object(newObject)

    def pop (self):
        self.list.pop()

    def remove_object(self, delObject):
        """
        Removes an object from the list, and notifies observers of the change
        """
        self.list.remove(delObject)
        for observer in self.targetObservers:
            observer.remove_target(delObject)

    def add_object(self, newObject):
        pass

    def get_object(self, objectIndex):
        """
        Returns an object at a specified index
        """
        return self.list[objectIndex]

    def clear(self):
        """
        Removes all objects from the list, and notifies all observers of the change
        """
        while self.list:
            if self.list[0] != None:
                self.remove_object(self.list[0])
            else:
                self.list.remove(None)
        pass
    pass

class Hand(ObservableList):
    """
    Has functions which can cause even more triggers to the observers.
    I.e. when a card is played, when a certain card is in hand, etc.
    """
    def play_card(self, gameObject, cardNumber, target):
        """
        Plays a card from the hand, returns the card that was played
        """
        self.list[cardNumber].play(gameObject, target)
        cardPlayed = self.list.pop(cardNumber)
        return cardPlayed
    pass

class Bench(ObservableList):
    """
    """
    pass

class Frontline(ObservableList):
    """
    Cards attack each other, get attacked, die, etc. All of these need different ways to
    notify the subscribers. Again, combat is very weird with a lot of edge cases, this
    class is subjet to change in the future.
    """
    def add_strike_trigger(self, observer):
        pass

    def remove_from_frontline(self, delObject):
        for i in range(len(self.list)):
            if self.list[i] == delObject:
                self.list[i] = None

        for observer in self.targetObservers:
            observer.remove_target(delObject)

    def set_defender(self, defender, position):
        self.list[position] = defender

    def create_empty(self, size):
        self.list = [None]*size

class Graveyard(ObservableList):
    """
    """
    pass

class Player:
    """
    Player character, has health, mana, and cards, etc.

    class variables
        playerCount
            A count of how many players have been made to give them unique names

    member variables
        mana - How much mana the player has
        health - How much health the player has
        name - The name of the player, to help differentiate them (not too important)
        bench - The cards on the bench (minions/ heroes)
        hand - The cards in the player's hand, an array of cards
        deck - The player's deck, an array of cards
        frontline - The player's cards which are involved in combat



        draw_card
            parameters: N/A
            return: N/A
            Make the player draw a card from the deck. When your hand is full are the 
            cards thrown away?

        play_card
            parameters:
                cardNumber
                    The index of the card in the "hand" array. This is the card to be played.
            return: N/A
            Play a card from the player's hand, the card played reflects the cardNumber, which
            was sent as a parameter
    """
    STARTING_MANA = 1
    MAX_HP = 20
    MAX_MANA = 10
    MAX_CARDS_IN_HAND = 10
    MAX_CARDS_IN_DECK = 40
    DEFAULT_PLAYER_NAMES = ["Bunny", "Rabbit"]

    playerCount = 0;

    def __init__(self):
        self.mana = Player.STARTING_MANA
        self.maxMana = Player.STARTING_MANA
        self.health = Player.MAX_HP
        self.name = Player.DEFAULT_PLAYER_NAMES[Player.playerCount]
        self.bench = Bench()
        self.frontline = Frontline()
        self.playableCards = []
        self.hand = Hand()
        self.deck = []
        self.graveyard = Graveyard()
        self.playerNumber = Player.playerCount

        Player.playerCount += 1
        Player.playerCount = Player.playerCount % 2

    def create_deck(self, cardMap, deckFile = ""):
        """
        create_deck
            parameters:
                cardDatabase
                    The database of cards stored as a dict. The name of the card is the key, 
                    which returns the corresponding card
                deckFile
                    A textfile which describes the player's deck. It is a list of names 
                    essentially seprated by newline characteers
            return: N/A
            Creates an array of cards which should correspond to the player's deck. The deck is
            unshuffled, and matches the order of the text file.
        """

        if (deckFile == ""):
            return
        with open(deckFile, "r") as file:
            for line in file:
                line = line.rstrip()
                inputCard = cardMap.get_card(line)
                inputCard.owner = self.playerNumber
                self.deck.append(inputCard)

    def new_turn(self, gameObject):
        """
        Each new turn, the player draws a card, has their mana replenished, etc.
        """
        self.increment_max_mana()
        self.mana = self.maxMana
        self.draw_card(gameObject)

    def increment_max_mana(self):
        self.maxMana += 1
        if self.maxMana > 10:
            self.maxMana = 10

    def draw_card(self, gameObject):
        newCard = self.deck.pop()
        self.hand.append(newCard)
        newCard.activate(gameObject)

    def play_card(self, gameObject, cardNumber, target = None):
        cardPlayed = self.hand.play_card(gameObject, cardNumber, target)
        return cardPlayed

    def prepare_attackers(self, cardIndices):
        """
        Calls selected cards to the frontline
        """
        for cardNumber in cardIndices:
            self.frontline.append(self.bench.list[cardNumber])
        pass

    def prepare_defenders(self, defendersAndPositions, numAttackers):
        """
        Calls selected cards to the frontline, and chooses which card to block
        Parameters:
            defendersAndPositions - The card indices, which we wish to use as defenders
                as well as the positions we wish to assign them to.
            numAttackers - The total number of attackers whic we are defending against.

        Returns
            N/A
        """
        self.frontline.create_empty(numAttackers)
        defendingCards = defendersAndPositions[::2]
        cardPositions = defendersAndPositions[1::2]
        for i in range(len(defendingCards)):
            defender = self.bench.list[defendingCards[i]]
            position = cardPositions[i]
            self.frontline.set_defender(defender, position)
        pass

    def test_card(self, gameObject, cardNumber):
        pass

    def playable_cards(self, attackPhase):
        """
        """
        self.playableCards = []
        for card in self.hand.list:
            self.playableCards.append(card.is_playable(self.mana, attackPhase))
        return self.playableCards


class Game:
    """
    Game object to be controlled externally. It can skip turns, make players draw cards, etc.

    member variables
        players
            an array of player objects, one for the opponent, one for the player
        activePlayer
            Either a 0 or 1. Tells us which player is the active one between the two
        inactivePlayer
            Vice versa of active player
        cardMap
            The card map object which reads the database. Each game object will have it's 
            own cardMap, so it only imports the necessary cards. We don't want to import the 
            whole database all the time. Of course, this may change depending on future 
            design decisions.

    functions
        setup

        create_deck
            parameters
                deckFile
                    The text file from which we wish to create the deck
                playerNumber
                    The player who will come into posession of said deck

    """
    #class variables, constants and other...
    MAX_BENCHED_CARDS = 6

    def __init__(self):
        # Default class variables. They more or less stay constant
        self.players = []
        self.players.append(Player())
        self.players.append(Player())
        self.cardMap = card.CardMapper()

        # Game state variables
        self.numAttackers = 0
        self.passedTurn = False
        self.attackToken = True
        self.attackPhase = False
        self.activePlayer = 0
        self.inactivePlayer = 1
        self.attackingPlayer = 0
        self.defendingPlayer = 1

        # Observers
        self.strikeObservers = []


    def setup(self):
        pass

    def import_database(self, fileName = ""):
        """
        Fills up the card database from the JSON file
        """
        if (fileName == ""):
            return
        self.cardMap.fill_database(fileName)
        pass

    def import_effects(self, fileName = ""):
        """
        Fills up the effects database
        """
        self.cardMap.fill_effect_database(fileName)
        pass

    def create_deck(self, deckFile, playerNumber):
        self.players[playerNumber].create_deck(self.cardMap, deckFile) 

# Actions
    def play_card(self, cardNumber, target = None):
        """
        Commands a player to play a card. It also keeps track of the game flow to ensure
        the turn ends when it's supposed to.

        Parameters:
            cardNumber - The index of the card in the hand's list
            target - The target of the card, assuming the card is a targeted one
        Returns:
            N/A
        """
        if (self.attackPhase == True):
            self.passedTurn = True
        else:
            self.passedTurn = False

        cardPlayed = self.players[self.activePlayer].play_card(self, cardNumber, target)
        if (cardPlayed.is_burst()):
            self.passedTurn = False
            return
        self.switch_active_player()

    def prepare_attack(self, attackers):
        """
        Sets up the turn order to enter the battle phase, then commands the player to
        prepare their attackers
        Parameters:
            attackers - the attackers which the player wishes to attack with
        """
        self.passedTurn = False
        if (self.activePlayer != self.attackingPlayer):
            print("You must be assigned the attack token to declare an attack!")
            return

        self.attackPhase = True
        self.attackToken = False
        self.numAttackers = len(attackers)
        self.players[self.attackingPlayer].prepare_attackers(attackers)

    def prepare_defense(self, defenders):
        self.players[self.defendingPlayer].prepare_defenders(defenders, self.numAttackers)
        pass

    def pass_turn(self):
        """
        Passes a players turn and ensures the game flow is maintained
        Parameters: N/A

        Return: N/A
        """
        if (self.passedTurn == True):
            self.passedTurn = False

            if (self.attackPhase == True):
                self.perform_all_attacks()
                return

            else:
                self.begin_new_turn()
                return

        else:
            self.passedTurn = True

        self.switch_active_player()
        pass

# Automatic actions
    def draw_card(self, playerNumber):
        self.players[playerNumber].draw_card(self)

    def perform_all_attacks(self):
        """
        All monsters on the frontline attack their counterpart simultaneously
        Case 1: Defending position has no card
                1) Attack the nexus
                2) Damage + results
                3) Trigger strike effects
        Case 2: Attacking card has quick attack, break down the attack
                1) Attacker attacks
                2) Damage + results
                3) Trigger strike effect
                4) Defnder returns fire (if still alive)
                5) Damage + results
                6) Trigger strike effect
        Case 3: Both cards just strike each other
                1) Both cards hurt each other
                2) Damage calculations come in
                3) Strike effects are triggered
        NOTE: Tryndamere, and other weird cards mean that this interaction is actually
        a lot more complicated than what was given above. This needs to be better fleshed
        out and addressed later.

        Parameters: None
        Return: None
        """
        attackingPlayer = self.players[self.attackingPlayer]
        attackingFrontline = attackingPlayer.frontline.list
        defendingPlayer = self.players[self.defendingPlayer]
        defendingFrontline = defendingPlayer.frontline.list

        for i in range(len(attackingFrontline)):
            # Case 1
            if defendingFrontline[i] == None:
                attackingFrontline[i].attack_nexus(defendingPlayer)
                attackingFrontline[i].activate_strike(self, defendingFrontline[i])
                self.clear_dead_cards()

            # Case 2
            elif attackingFrontline[i].quickAttack == True:
                attackingFrontline[i].attack_card(defendingFrontline[i])
                attackingFrontline[i].activate_strike(self, defendingFrontline[i])
                self.clear_dead_cards()

                if defendingFrontline[i] != None:
                    defendingFrontline[i].attack_card(attackingFrontline[i])
                    defendingFrontline[i].activate_strike(self, attackingFrontline[i])
                    self.clear_dead_cards()

            # Case 3
            else:
                attackingFrontline[i].attack_card(defendingFrontline[i])
                defendingFrontline[i].attack_card(attackingFrontline[i])
                attackingFrontline[i].activate_strike(self, defendingFrontline[i])
                defendingFrontline[i].activate_strike(self, attackingFrontline[i])
                self.clear_dead_cards()

        for player in self.players:
            player.frontline.clear()

        self.attackPhase = False

    def clear_dead_cards(self):
        """
        Clears all deads cards from the field
        """
        for player in self.players:
            for card in player.bench.list:
                if card.defense <= 0:
                    self.kill_card(card)

    def kill_card(self, card):
        """
        Kills a card on the field. Maybe it can be expanded to deal with cards being
        discarded from the hand too
        """
        self.players[card.owner].frontline.remove_from_frontline(card)
        self.players[card.owner].bench.remove_object(card)
        self.players[card.owner].graveyard.append(card)

    def switch_active_player(self):
        self.activePlayer = helper.switch_zero_one(self.activePlayer)

    def resolve_skirmish(self, attackingCard, defendingCard):
        pass

    def begin_new_turn(self):
        """
        Begins a new turn, and notifies the players to ensure proper game flow. Each turn
        the attacking token changes hands, and the player with the attacking token is given
        initiative.
        """
        print("BEGINNING A NEW TURN")
        for player in self.players:
            player.new_turn(self)
        
        self.switch_attacking_player()
        self.activePlayer = self.attackingPlayer
        self.attackToken = True

    def switch_attacking_player(self):
        self.attackingPlayer = helper.switch_zero_one(self.attackingPlayer)
        self.defendingPlayer = helper.switch_zero_one(self.defendingPlayer)

    def card_attack_card(self, attackingCard, defendingCard):
        """
        DEPRECATED
        """
        if (attackingCard.quickAttack == True):
            self.card_quick_attack(attackingCard, defendingCard)
            self.card_quick_attack_counter(attackingCard, defendingCard)
            return

        defendingCard.defense -= attackingCard.attack
        attackingCard.defense -= defendingCard.attack
        for observer in self.strikeObservers:
            observer.event_triggered(self, attackingCard, defendingCard)

    def card_quick_attack(self, attackingCard, defendingCard):
        """
        DEPRECATED
        """
        defendingCard.defense -= attackingCard.attack
        for observer in self.strikeObservers:
            observer.event_triggered(self, attackingCard, defendingCard)

    def card_quick_attack_counter(self, attackingCard, defendingCard):
        """
        DEPRECATED
        """
        if (self.players[attackingCard.owner].frontline.list.count(attackingCard) == 0):
            return
        attackingCard.defense -= defendingCard.attack
        for observer in self.strikeObservers:
            observer.event_triggered(self, defendingCard, attackingCard)

    def card_attack_player(self, attackingCard, defendingPlayer):
        """
        DEPRECATED
        """
        defendingPlayer.health -= attackingCard.attack

# Help actions
    def list_playable_cards(self):
        return self.players[self.activePlayer].playable_cards(self.attackPhase)

    def list_all_moves(self):
        decisionSpace = dict()
        playableCards = self.players[self.activePlayer].playable_cards(self.attackPhase)
        targetList = []
        for card in self.players[self.activePlayer].hand.list:
            targetList.append(card.get_targets())
        decisionSpace["playable cards"] = playableCards
        decisionSpace["target list"] = targetList
        return decisionSpace

# Observer management
    def add_strike_subscriber(self, strikeObserver):
        """
        DEPRECATED
        """
        self.strikeObservers.append(strikeObserver)

    def remove_strike_subscriber(self, strikeObserver):
        """
        DEPRECATED
        """
        self.strikeObservers.remove(strikeObserver)
