import pickle
import pdb

inFile = open("gamestate.dump", 'rb')
gameObject = pickle.load(inFile)
#pdb.set_trace()

"""
# TESTING THE TARGETING ARRAYS
print("target array 0")
print(gameObject.players[0].hand.list[0].playEffect.targetArray)
print(gameObject.players[0].hand.list[0].playEffect.list_playable_options())

print("target array 1")
print(gameObject.players[1].hand.list[0].playEffect.targetArray)
print(gameObject.players[1].hand.list[0].playEffect.list_playable_options())

print(gameObject.players[1].bench.targetObservers)
"""

print("Checking the spell speed")
print(gameObject.players[0].deck[0])
print(gameObject.players[0].deck)
print(gameObject.players[0].deck.count(gameObject.players[0].deck[0]))
