from cards import cards
import random

class Deck:
    def __init__(self,cards):
        self.cards=cards[:]
    
    def shuffle(self):
        print("シャッフル前:", [card.name for card in self.cards])
        random.shuffle(self.cards)
        print("シャッフル後:", [card.name for card in self.cards])
    
    def draw(self):
        if self.cards:
            return self.cards.pop()
        return None

    def deal(self, num):
        """num枚カードを配る"""
        dealt = []
        for _ in range(num):
            if self.cards:
                dealt.append(self.cards.pop())
        return dealt



    def reset(self):
        pass        

if __name__ == "__main__":
    deck=Deck(cards)
    deck.shuffle()