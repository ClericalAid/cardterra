"""
This module implements cards. It has a card base class from which all other types of cards
inherit.

Card
Base class for cards. Minion, hero, and spell cards inherit from this

    Minion
    Follower cards with an attack and HP stat

    Hero
    Like minions, but can level up

    Spell
    Trigger an effect when played.

CardMapper
Maps all the cards from the JSON file, into a dictionary database. Factory for cards.
"""
import json
import copy
import effect
import pdb
import enum

class Speed(enum.Enum):
    BURST = 0
    FAST = 1
    SLOW = 2

class Card:
    """
    Card
    The base object for all cards: minions, heroes, spells, etc.

    member variables:
        manaCost
            The mana cost of the card. Players expend this mana to play the card

        name
            The name of the card

        playEffect
            The effect which occurs when the card is played

        Owner
            The owner of the card (either 0 or 1, as it's a 1v1 game)

        Speed
            The speed of the card (burst, fast, slow, etc.)

        inPhase
            Only fast and burst spells can be cast during battle phase. This bool
            ensures that the card is being used in the proper phase

        enoughMana
            A boolean to track whether or not the player meets the mana requirements
            to play the card

    """
    def __init__(self, name, manaCost):
        self.manaCost = manaCost
        self.name = name
        self.playEffect = None
        self.owner = -1
        self.speed = Speed.SLOW
        self.inPhase = True
        self.enoughMana = True

    def __copy__(self):
        pass
    
    def get_targets(self):
        return self.playEffect.targetArray

    def list_playable_options(self):
        self.playEffect.list_playable_options()

    def play(self, gameObject, target = None):
        """
        play()
            parameters:
                gameObject - the game object which stores the players, field, etc.
                target - the victim of the card, assuming the card is targeted

            return:
                Boolean - This is subject to change

            Plays the card from the hand. This function is overriden by each different 
            card type i.e. minions, spells, and heroes will all have different play functions
        activate
        """

        cardPlayed = self.playEffect.activate(gameObject, self, target)
        if (cardPlayed == True):
            return True
        return False

    def activate(self, gameObject):
        """
        Tells the card to begin tracking whatever is relevant to itself. For
        example, keeping track of allies killed
        """
        if (self.playEffect != None):
            self.playEffect.subscribe(gameObject, self.owner)
        pass

    def info(self):
        pass

    def is_playable(self, currentMana, attackPhase):
        """
        Tells us whether or not the card can be played or not 
        """
        if (attackPhase == True and self.speed == Speed.SLOW):
            return False
        elif (currentMana < self.manaCost):
            return False
        return True

    def is_burst(self):
        if (self.speed == Speed.BURST):
            return True

class Minion(Card):
    """
    Minion
    A minion card.

    variables
        attack - The attack power of the minion
        defense - The defense/ hp of the minion
        playEffect - The effect which the card has (not all minions have effects)

        Statistic variables (These might be removed)
        totalDamageTaken - Total damage which the card has sustained
        totalDamageDealt - Total damage which the card has dealt (in combat)
        strikeCount - How many times the card has attacked another card
        nexusStrikeCount - How many times the card has struck the nexus
        killCount - How many enemy cards the card has killed

        Effect related variables (These might be removed)
        quickAttack
        trigger
        stikeEffect
    """

    def __init__(self, name, manaCost, attack, defense):
        super().__init__(name, manaCost)
        self.attack = attack
        self.defense = defense
        self.playEffect = effect.Summon()

        self.totalDamageTaken = 0
        self.totalDamageDealt = 0
        self.strikeCount = 0
        self.nexusStrikeCount = 0
        self.killCount = 0

        self.quickAttack = False
        self.trigger = None
        self.strikeEffect = None

    def __copy__(self):
        ret = Minion(self.name, self.manaCost, self.attack, self.defense)
        return ret

    def attack_card(self, card):
        """
        Causes this card to attack another card
        """
        if card == None:
            return
        card.defense -= self.attack

    def attack_nexus(self, player):
        """
        Attacks the nexus
        """
        player.health -= self.attack

    def activate_strike(self, gameObject, target):
        """
        Activates the strike effect of the card. This implementation needs work
        """
        self.strikeCount += 1
        if target == None:
            self.nexusStrikeCount += 1
            #We struck the nexus

        if self.strikeEffect == None:
            return
        self.strikeEffect.activate(gameObject, self, target)

    def info(self):
        """
        Returns information relevant to the card at hand
        """
        ret = {
            "name": self.name,
            "cost": self.manaCost,
            "attack": self.attack,
            "defense": self.defense
        }
        return ret

class Hero(Minion):
    """
    A minion which has another effect: it can level up
    """
    def __init__(self, name, manaCost, attack, defense):
        super().__init__(name, manaCost, attack, defense)
        self.levelUpEffect = None
        pass

    def level_up(self):
        pass

    pass

class Spell(Card):
    """
    A spell card. You play it, the effect happens. Boom
    Member variables:
        speed - The speed of the spell:
            Burst: So fast, you get to act again
            Fast: So fast, your opponent gets to react to it (wait, what?)
            Slow: So slow, it happens the next turn (or cycle?)
    """
    def __init__(self, name, manaCost, playEffect, speed = None):
        super().__init__(name, manaCost)
        self.playEffect = playEffect
        self.playEffect.set_owner(self)
        self.speed = speed

    def __copy__(self):
        ret = Spell(self.name, self.manaCost, self.playEffect)
        return ret

    pass

class CardMapper():
    """
    CardMapper
    Makes the cards from the database or textfile (ideally this would be in JSON format), and then
    stores them into a hash map 

    member variables
        cardsJSON - Stores all of the cards from the database, after having been 
            parsed. It stores the parsed data in an array/ dict of sorts

        cardDatabase - A dictionary mapping the cards to their names. Each name will 
            return a card object which corresponds to the respective card.

        effectMapper - It's similar to a card mapper, but it maps effects.

    """


    def __init__(self):
        self.cardsJSON = None
        self.cardDatabase = dict()
        self.effectMapper = effect.EffectMapper()
        pass

    def get_card(self, cardName):
        ret = copy.deepcopy(self.cardDatabase[cardName])
        return ret

    def fill_effect_database(self, fileName = ""):
        self.effectMapper.fill_database(fileName)

    def fill_database(self, fileName = ""):
        """
        Reads the cards from the text file which contains the cards in JSON format. Converts 
        the JSON information into actual cards

        Parameters:
            fileName - The name of the database file
        """
        if (fileName == ""):
            return
        databaseFile = open(fileName, 'r')
        self.cardsJSON = json.load(databaseFile)
        for JSONcard in self.cardsJSON:
            newCard = self.create_card(JSONcard)
            self.cardDatabase[JSONcard["name"]] = newCard

    def create_card(self, JSONcard):
        """
        Creates a card based on the information in the JSON object.

        Parmaeters:
            JSONcard - The card information in JSON format

        Return:
            The card which has been freshly made
        """ 
        if JSONcard["type"] == "minion":
            newCard = Minion(JSONcard["name"], JSONcard["manaCost"], \
                             JSONcard["attack"], JSONcard["defense"])
            if self.effectMapper.effect_exists(JSONcard["name"]):
                newCard.playEffect = self.effectMapper.get_effect(JSONcard["name"])
            pass

        if JSONcard["type"] == "spell":
            newCard = Spell(JSONcard["name"], JSONcard["manaCost"], \
                            self.effectMapper.get_effect(JSONcard["name"]), \
                            Speed[JSONcard["speed"]])
            pass

        return newCard
