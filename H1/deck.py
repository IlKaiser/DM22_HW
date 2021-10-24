import time
import pydealer

import matplotlib.pyplot as plt
import numpy as np

trials = 1000000  # ~3 mins for a million trials
FORMAT = '{0:.5f}'

c_at_least_1_ace_2_cards = 0
c_all_equals_2_cards = 0
c_at_least_1_ace_5_cards = 0
c_all_diamonds_5_cards = 0
c_full_5_cards = 0

al1a2c = []
ae2c   = []
al1a5c  = []
ad5c   = []
f5c    = []


def at_least_1_ace_2_cards(cards):
    return any(c.value == 'Ace' for c in cards[:2])


def all_equals_2_cards(cards):
    return cards[0].value == cards[1].value 


def at_least_1_ace_5_cards(cards):
    return any(c.value == 'Ace' for c in cards[:5])


def all_diamonds_5_cards(cards):
    return all(c.suit == 'Diamonds' for c in cards)


def full_5_cards(cards):
    cards.sort()
    return (cards[0].value != cards[3].value and cards[0].value == cards[1].value == cards[2].value and cards[3].value == cards[4].value) \
           or (cards[0].value != cards[2].value and cards[0].value == cards[1].value and cards[2].value == cards[3].value == cards[4].value)


def print_results():
    print ('##### Frequencies report for %d trials #####\n' % trials)
    print ('(a) At least 1 Ace in first 2 cards:\t\t' + FORMAT.format(c_at_least_1_ace_2_cards / trials))
    print ('(b) At least 1 Ace in first 5 cards:\t\t' + FORMAT.format(c_at_least_1_ace_5_cards / trials))
    print ('(c) First 2 cards all equals:\t\t\t' + FORMAT.format(c_all_equals_2_cards / trials))
    print ('(d) All Diamonds in first 5 cards:\t\t' + FORMAT.format(c_all_diamonds_5_cards / trials))
    print ('(e) Full house in first 5 cards:\t\t' + FORMAT.format(c_full_5_cards / trials))


start_time = time.time()

for i in range(0, trials):
    print(str("{:.2f}".format(i/trials *100)) + "%",end="\r")
    deck = pydealer.Deck()
    deck.shuffle()
    hand = deck.deal(5)
    if at_least_1_ace_2_cards(hand):
        c_at_least_1_ace_2_cards += 1
    if all_equals_2_cards(hand):
        c_all_equals_2_cards += 1
    if at_least_1_ace_5_cards(hand):
        c_at_least_1_ace_5_cards += 1
    if all_diamonds_5_cards(hand):
        c_all_diamonds_5_cards += 1
    if full_5_cards(hand):
        c_full_5_cards += 1
    al1a2c.append(c_at_least_1_ace_2_cards/(i+1))
    ae2c.append(c_all_equals_2_cards/(i+1))
    al1a5c.append(c_at_least_1_ace_5_cards/(i+1))
    ad5c.append(c_all_diamonds_5_cards/(i+1))
    f5c.append(c_full_5_cards/(i+1))
    
print_results()
diff = time.time() - start_time
print("\n--- %s seconds elapsed---" % (diff))
print("\n--- %s seconds per trial ---" % (diff/trials))

fig = plt.figure()
gs = fig.add_gridspec(5, hspace=0.5)
axs = gs.subplots(sharex=True)

axs[0].plot(np.arange(trials),al1a2c )  # Plot some data on the axes.
axs[0].set_title("At least one ace in 2 cards ")

axs[1].plot(np.arange(trials),ae2c) 
axs[1].set_title("First 2 cards are the same")

axs[2].plot(np.arange(trials),al1a5c ) 
axs[2].set_title("At least one ace in 5 cards ")

axs[3].plot(np.arange(trials),ad5c ) 
axs[3].set_title("All diamond in 5 cards ")

axs[4].plot(np.arange(trials),f5c ) 
axs[4].set_title("Full in 5 cards")

plt.show()
