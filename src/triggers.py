"""
This module implements trigger effects. Triggers share a targeting mechanism with effects.
There is a lot of overlap between these two for example: a spell card can be a buff that
only targets allies on the field. A trigger could occur when an ally (on the field) takes
damage. Both rely on targeting allies on the field.

A trigger also contains an effect. For example, when an ally takes damage, buff a random ally
by 1/1. This means that there are 2 targers. One to see when the trigger happened, and the
effect would have its own targeter.

Triggers do not work right now. They are far from complete.
"""
import copy
import targeting

class Trigger():
    """
    Trigger
    All possible triggers will inherit from this.
    """
    def __init__(self, targeter = None, subscriber = None):
        self.targeter = targeter
        self.subscriber = subscriber
        self.triggerEffect = None

        if (self.targeter == None):
            self.targeter = targeting.BaseTargeter()

        self.name = ""
        pass

    def is_valid_trigger_card(self, card):
        if (self.targeter.targetArray.count(card) != 0):
            return True
        return False

    def subscribe(self, gameObject, cardOwner):
        self.targeter.subscribe(gameObject, self, cardOwner)

    def __copy__(self):
        pass

    def event_triggered(self):
        pass

    pass

class Subscriber():
    """
    Subscriber
    This class just tells the parent class where to subscribe to.
    """
    def subscribe(self, gameObject):
        pass
    pass

class AttackSubscriber(Subscriber):
    pass

class TriggerMapper():
    """
    TriggerMapper
    """
    def __init__(self):
        self.triggersJSON = None
        self.triggerDatabase = dict()
        pass

    def get_trigger(self, triggerName):
        ret = copy.copy(self.triggerDatabase[triggerName])
        return ret

    def create_allegiance(self, allegiance):
        pass

    def fill_database(self, fileName = ""):
        if (fileName == ""):
            print("No file given")
            return
        databaseFile = open(fileName, 'r')
        self.triggersJSON = json.load(databaseFile)
        for JSONtrigger in self.triggersJSON:
            location = targeting.create_location(JSONeffect)
            targeter = targeting.create_targeter(JSONeffect, location)
            newTrigger = self.create_effect(JSONeffect, selector, targeter)

            self.triggerDatabase[JSONeffect["name"]] = newEffect
        pass

    def create_trigger(self, JSONtrigger, selector, targeter):
        newTrigger.name = JSONtrigger["name"]
        return newTrigger
    pass

