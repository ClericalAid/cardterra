"""
This module implements the targeting and selecting mechanism. 

Targeter:
The targeting mechanism is two separate targeters, and one wraps the other. The 2 levels 
are as follows:

Allegiance targeting:
    Allied
    Enemy
    Any
Location targeting (non-exhaustive):
    Bench
    Battlefield
    Hand
    Deck
    Graveyard
For example. A card buffs an ally on your side of the field. Or it decreases the cost of spells
in your hand. Almost every effects' targets can be generalized with the cases above.

Selector:
For the selection mechanism, it looks at the targets available, and then applies the appropriate
selection method. These can be (non-exhaustive):
    Random selection
    Strongest card
    Weakest card

Creation Functions:
These functions create the appropriate selector/ targeter. They are used because the effect/
trigger mapping tools need to create targeters/ selectors based on the information given in the
JSON file. With the overlap between these two mapping tools, we moved the functions here.
"""
import itertools

class BaseTargeter():
    """
    BaseTargeter
    Cards focus on targeting either the enemy or ally (you wouldn't buff an enemy card for
    example), but there are other cards which can target either faction (returning a card to the
    owner's hand perhaps).

    This class wraps the LocationTargeter, and together they specify an exact location where
    we would find our targets. I.e. enemy minion on the field, cards in our hand, or an ally on
    our side of the field.

    Member variables:
        locationTargeter - The bench, battlefield, hand, deck, etc.
        targetArray - List of all valid targets
    """
    def __init__(self, locationTargeter = None):
        self.locationTargeter = locationTargeter
        self.targetArray = []
        self.parentEffect = None
        if self.locationTargeter == None:
            self.locationTargeter = LocationTargeter()
    
    def set_parent(self, parent):
        self.parentEffect = parent

    def subscribe(self, gameObject, cardOwner):
        self.locationTargeter.subscribe(gameObject, self, cardOwner)

    def trigger_subscribe(self, gameObject):
        pass

    def receive_list(self, inputList):
        self.targetArray.extend(inputList)

    def remove_object(self, delObject):
        self.targetArray.remove(delObject)

    def add_object(self, newObject):
        self.targetArray.append(newObject)


class Enemy(BaseTargeter):
    """
    Specifies that we are looking at the enemy.
    """
    def subscribe(self, gameObject, cardOwner):
        enemy = helper.switch_zero_one(cardOwner)
        super().subscribe(gameObject, self, enemy)
    pass

class Allied(BaseTargeter):
    """
    We look at allied cards
    """
    def __init__(self, locationTargeter = None):
        super().__init__(locationTargeter)
        pass

    pass

class Any(BaseTargeter):
    """
    We can target either the enemy's cards or ours
    """
    def subscribe(self, gameObject, cardOwner):
        enemy = helper.switch_zero_one(cardOwner)
        super().subscribe(gameObject, self, cardOwner)
        super().subscribe(gameObject, self, enemy)

    pass

class LocationTargeter():
    """
    LocationTargeter
    Specifies the location where we search for targets. This could be the bench, hand, or deck.
    In order for all effects to behave in a similar fashion (even those that don't need targets),
    default behaviour must be defined. We define that behaviour here.

    If a target does not need targets, it gets the default behaviour which is to return an empty
    targetArray.
    """
    def __init__(self):
        pass
    
    def subscribe(self, gameObject, baseTargeter, playerNumber):
        pass

class Bench(LocationTargeter):
    """
    Targeting the bench/ field. The cards that have been played are on the bench. Those in
    combat are the battlefield. Those in the battlefield are also in the bench.
    """
    def subscribe(self, gameObject, baseTargeter, playerNumber):
        """ 
        Subscribes to the correct bench based on the allegiance
        """
        gameObject.players[playerNumber].bench.add_target_observer(baseTargeter)
        pass

    pass

class Self(LocationTargeter):
    """
    I don't know if this should be here, or if the selector should deal with this
    """
    def subscribe(self, gameObject, baseTargeter, playerNumber):
        """
        """
        targetArray.append(self.parent.parent)
    pass

class Selector():
    """
    Selector
    Defines the method of selecting targets. This could be the player choosing the targets. It
    could also be automatic (random target, strongest monster on the field, etc.).

    When asked to return the playable options, an empty array means that there are no targets
    (just play the card). This should be the default behaviour, and will be used when the player
    should not be declaring targets i.e. when summoning a minion, or an ability that targets a
    random card.
    """
    def __init__(self):
        pass

    def list_playable_options(self, targetArray):
        ret = []
        return ret

    def select_target(self, target):
        pass
    pass

class Player(Selector):
    """
    Player Selector
    This class means that the player chooses the victim upon which to enact the effect
    """
    def __init__(self, choices):
        self.choices = choices
        pass

    def list_playable_options(self, targetArray):
        """
        Instructs the user on how the card can be played. For example, if an effect has
        2 targets, the user specifies to use the card, followed by 2 targets. This also
        helps us describe how to play the game for an automated player
        Parameters:
            targetArray - The list of all valid targets

        Returns:
            An array detailing the different ways the card can be played. It tells us the
            parameters we can use to play the card
        """
        targetIndices = list(range(len(targetArray)))
        ret = list(itertools.combinations(targetIndices, self.choices))
        return ret
    
    def select_target(self, targetArray, target):
        """
        Selects the target based on the player input 
        """
        if target == None:
            return None
        return targetArray[target]

class Strongest(Selector):
    def select_target(self, targetArray, target = None):
        """
        Selects the strongest target
        Parameters:
            targetArray - A list of all valid targets
            target - None by default, this parameter should not be sent to this function
                It exists due to inheritance/ uniformity amongst the effects
        """
        if len(targetArray) == 0:
            return None
        strongestTarget = targetArray[0]
        for target in targetArray:
            if target.attack > strongestTarget.attack:
                strongestTarget = target
        pass
    pass

class Random(Selector):
    def select_target(self, targetArray, target = None):
        pass
    pass

#Helper functions to create targeting classes
def create_location(JSONeffect):
    if (JSONeffect["location"] == "bench"):
        location = Bench()
    if (JSONeffect["location"] == "self"):
        location = Self()
    return location

def create_targeter(JSONeffect, location):
    if (JSONeffect["allegiance"] == "allied"):
        targeter = Allied(location)

    if (JSONeffect["allegiance"] == "enemy"):
        targeter = Enemy(location)

    if (JSONeffect["allegiance"] == "any"):
        targeter = Any(location)

    return targeter

def create_selector(JSONeffect):
    if (JSONeffect["selection"] == "human"):
        selector = Player(JSONeffect["choices"])
    if (JSONeffect["selection"] == "random"):
        selector = Random()
    if (JSONeffect["selection"] == "strongest"):
        selector = Strongest()
    return selector

