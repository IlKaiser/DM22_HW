import time
import pydealer

import matplotlib.pyplot as plt
import numpy as np

trials = 100000  # ~3 mins for a million trials
FORMAT = '{0:.5f}'

c_at_least_1_ace_3_cards = 0
c_all_equals_3_cards = 0
c_exactly_1_ace_5_cards = 0
c_all_diamonds_5_cards = 0
c_full_5_cards = 0

al1a3c = []


def at_least_1_ace_3_cards(cards):
    return any(c.value == 'Ace' for c in cards[:3])


def all_equals_3_cards(cards):
    return cards[0].value == cards[1].value == cards[2].value


def exactly_1_ace_5_cards(cards):
    ace_found = False
    for c in cards:
        if c.value == 'Ace' and not ace_found:
            ace_found = True
        elif c.value == 'Ace' and ace_found:
            return False
    return ace_found


def all_diamonds_5_cards(cards):
    return all(c.suit == 'Diamonds' for c in cards)


def full_5_cards(cards):
    cards.sort()
    return (cards[0].value != cards[3].value and cards[0].value == cards[1].value == cards[2].value and cards[3].value == cards[4].value) \
           or (cards[0].value != cards[2].value and cards[0].value == cards[1].value and cards[2].value == cards[3].value == cards[4].value)


def print_results():
    print ('##### Frequencies report for %d trials #####\n' % trials)
    print ('(a) At least 1 Ace in first 3 cards:\t\t' + FORMAT.format(c_at_least_1_ace_3_cards / trials))
    print ('(b) Exactly 1 Ace in first 5 cards:\t\t' + FORMAT.format(c_exactly_1_ace_5_cards / trials))
    print ('(c) First 3 cards all equals:\t\t\t' + FORMAT.format(c_all_equals_3_cards / trials))
    print ('(d) All Diamonds in first 5 cards:\t\t' + FORMAT.format(c_all_diamonds_5_cards / trials))
    print ('(e) Full house in first 5 cards:\t\t' + FORMAT.format(c_full_5_cards / trials))


start_time = time.time()

for i in range(0, trials):
    print(str("{:.2f}".format(i/trials *100)) + "%",end="\r")
    deck = pydealer.Deck()
    deck.shuffle()
    hand = deck.deal(5)
    if at_least_1_ace_3_cards(hand):
        c_at_least_1_ace_3_cards += 1
    if all_equals_3_cards(hand):
        c_all_equals_3_cards += 1
    if exactly_1_ace_5_cards(hand):
        c_exactly_1_ace_5_cards += 1
    if all_diamonds_5_cards(hand):
        c_all_diamonds_5_cards += 1
    if full_5_cards(hand):
        c_full_5_cards += 1
    al1a3c.append(c_at_least_1_ace_3_cards/(i+1))
    
print_results()
diff = time.time() - start_time
print("\n--- %s seconds elapsed---" % (diff))
print("\n--- %s seconds per trial ---" % (diff/trials))

fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.plot(np.arange(trials),al1a3c )  # Plot some data on the axes.
plt.show()
