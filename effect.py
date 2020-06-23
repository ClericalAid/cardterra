"""
An implementation of all of the effects. An attempt at the strategy design pattern was employed.
All of the effects follow the same format. They all use the same function, and take the same
parameters.

A non-exhaustive list of effects:
Summon
Buff
Recall (return to hand)
Kill
Decrease mana cost

Thanks to our targeting class, we are able to pick out appropriate targets. The effect then
simply has to act upon said targets. Which makes it easy for the effects to all follow a similar
format in terms of function parameters, etc.

Effect Mapper
This is similar to the cards. The effects are stored in a JSON file, and they are created at
runtime, based off of their description. Factory design pattern again. Factory design pattern
is used for cards and effects so that new cards are easy to implement without having to modify
the source code.
"""
import helper
import json
import copy
import pdb
import targeting

class Effect():
    """
    Effect
    All possible effects will inherit from this.
    Summoning Card
    Return Card to Owner's Hand
    Buff/ De-Buff Card

    Member Variables:
        name - The name of the effect
        targeter - Gathers all valid targets for the effect
        selector - Employs the selection method over the valid targets in order to ensure
            proper card use
        playableOptions - How the card can be played i.e. how many targets need to be specified
        parent - Deprecated I think
    """

    def __init__(self, targeter = None, selector = None):
        self.targeter = targeter
        self.selector = selector

        if (self.targeter == None):
            self.targeter = targeting.BaseTargeter()
        if (self.selector == None):
            self.selector = targeting.Selector()

        self.targeter.set_parent(self)
        self.name = ""
        self.playableOptions = []
        self.parent = None
        pass

    def activate(self, gameObject, card, target = None):
        print("INVALID FUNCTION")
        pass

    def set_owner(self, card):
        self.parent = card
        pass

    def get_targets(self, target = None):
        """
        Retrieves the target from the selector. If input is 'None', we can assume that
        the selector is automatic. I.e. strongest enemy minion, weakest, random, etc.
        """
        if (isinstance(target, int)):
            return self.selector.select_target(self.targeter.targetArray, target)

    def subscribe(self, gameObject, cardOwner):
        self.targeter.subscribe(gameObject, cardOwner)

    def list_playable_options(self):
        """
        Lists how the card can be played. For example, the card might have 1 target, 2
        targets, or not require any targets
        """
        playableOptions = self.selector.list_playable_options(self.targeter.targetArray)
        return playableOptions

    pass

class Summon(Effect):
    """
    Summon
    Summons a card (hero or minion). This effect is activated when a minion card gets played.
    It also occurs under conditions where a card will summon another card. Essentially,
    whenever a card is going to enter the field, this effect should cover that case
    """
    def __init__(self, targeter = None, selector = None):
        super().__init__(targeter, selector)
        pass

    def activate(self, gameObject, card, target = None):
        """
        Summons the card to the appropriate player's field
        """
        gameObject.players[card.owner].bench.append(card)
        return True

class Buff(Effect):
    """
    modifyEffect
    Reserved for buffs/ debuffs. This includes the simple case where a minion's attack or defense
    is increased/ decreased. I think this should also include weird cases where a card's mana
    cost is decreased as well. It could also include cases where a card's attack is reduced to 0,
    or a spell deals damage to a card.
    """
    def __init__(self, targeter, selector, attackBuff, defenseBuff):
        super().__init__(targeter, selector)
        self.attackBuff = attackBuff
        self.defenseBuff = defenseBuff

    def activate(self, gameObject, card, target = None):
        """
        Buffs the targeted card
        
        Parameters:
            gameObject - The main gameObject which stores all of the relevant data
            card - The card which contains the buff effect
            target - The targeted card to be buffed. If there is no target, then no buff happens
                This might happen if a card buffs a random ally, but you have no allies

        Returns:
            Boolean - This should be deprecated
        """
        targetCard = self.get_targets(target)
        if (targetCard == None):
            return True
        targetCard.attack += self.attackBuff
        targetCard.defense += self.defenseBuff
        return True

    def __copy__(self):
        ret = Buff(self.targeter, self.selector, self.attackBuff, self.defenseBuff)
        return ret

class Recall(Effect):
    def activate(self, gameObject, card, target = None):
        """
        Returns the target card to its owner's hand

        Parameters:
            gameObject - The main gameObject which stores all of the relevant data
            card - The card which contains the buff effect
            target - The targeted card to be buffed. If there is no target, then no buff happens
                This might happen if a card buffs a random ally, but you have no allies

        Returns: N/A
        """
        targetCard = self.get_targets(target)
        gameObject.players[targetCard.owner].hand.append(targetCard)
        gameObject.players[targetCard.owner].frontline.remove_from_front_line(targetCard)
        gameObject.players[targetCard.owner].bench.remove_object(targetCard)
        pass
    pass

class EffectMapper():
    """
    EffectMapper
    Creates the effects from a database or textfile in JSON format, and stores them in a
    hashmap.

    Builds the targeter and selector first, then throw them into the effect

    Member variables:
        effectsJSON - The JSON database of the effects
        effectsDatabase - A dictionary which stores the effects, mapped to their name
    """
    def __init__(self):
        self.effectsJSON = None
        self.effectDatabase = dict()
        pass

    def get_effect(self, effectName):
        ret = copy.copy(self.effectDatabase[effectName])
        return ret

    def effect_exists(self, effectName):
        if effectName in self.effectDatabase:
            return True
        return False

    def create_allegiance(self, allegiance):
        pass

    def fill_database(self, fileName = ""):
        """
        Loads up the effects from the JSON database into the effect dictionary
        Builds the appropriate targeter and selector from the information in the JSON file as well
        Parameters:
            fileName - The name of the JSON database for the effects
        Returns: N/A
        """
        if (fileName == ""):
            print("No file given")
            return
        databaseFile = open(fileName, 'r')
        self.effectsJSON = json.load(databaseFile)
        for JSONeffect in self.effectsJSON:
            location = targeting.create_location(JSONeffect)
            targeter = targeting.create_targeter(JSONeffect, location)
            selector = targeting.create_selector(JSONeffect)
            newEffect = self.create_effect(JSONeffect, selector, targeter)

            self.effectDatabase[JSONeffect["name"]] = newEffect
        pass

    def create_effect(self, JSONeffect, selector, targeter):
        """
        Creates an individual effect from the information available in the JSON database
        
        Parameters:
            JSONeffect - The information of the effect in JSON format
            targeter - The targeter which the effect will use
            selector - The selector which the effect will use
        """
        if (JSONeffect["type"] == "buff"):
            newEffect = Buff(targeter, selector, JSONeffect["attack"], JSONeffect["defense"])
        if (JSONeffect["type"] == "recall"):
            newEffect = Recall(targeter, selector)

        newEffect.name = JSONeffect["name"]
        return newEffect
    pass
