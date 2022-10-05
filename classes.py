from misc import print_slow

class Monster:
    '''
    Essa classe estrutura as características de um monstro
    '''
    def __init__(self, name, type, moves, attack, defense, speed, \
                totalHealth, currentHealth, currentEnergy, totalEnergy, cooldown, status, statusCounter):
        self.name = name
        self.type = type
        self.moves = moves
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.totalHealth = totalHealth
        self.currentHealth = currentHealth
        self.currentEnergy = currentEnergy
        self.totalEnergy = totalEnergy
        self.cooldown = cooldown
        self.status = status
        self.statusCounter = statusCounter      
               
class Moves:
    '''
    Essa classe estrutura ataques que um monstro pode usar
    '''
    def __init__(self, name, type, dmg, cooldown, cost, speed):
        self.name = name
        self.type = type
        self.dmg = dmg
        self.cooldown = cooldown
        self.cost = cost
        self.speed = speed
        
class Item:
    '''
    Essa classe estrutura itens consumíveis
    '''
    def __init__(self, name, qt, effect):
        self.name = name
        self.qt = qt
        self.effect = effect
        
    def useItem(self, target):
        if self.effect[0] == 1: # health potion
            if target.currentHealth < target.totalHealth:
                target.currentHealth += self.effect[1]
                if target.currentHealth > target.totalHealth:
                    target.currentHealth = target.totalHealth
                print_slow(f'''{target.name}'s HP has been restored by {self.effect[1]} points!''')
                return True
            else:
                print_slow(f'''{target.name}'s health is full!''')
                return False
        elif self.effect[0] == 2: # energy potion
            if target.currentEnergy < target.totalEnergy:
                target.currentEnergy += self.effect[1]
                if target.currentEnergy > target.totalEnergy:
                    target.currentEnergy = target.totalEnergy
                return True
            else:
                print_slow(f'''{target.name} is full of energy!''')
                return False
        elif self.effect[0] == 3: # status heal
            if target.status != None:
                target.status, target.statusCounter = None, None
                return True
            else:
                print_slow(f'''{target.name} doesn't neeed that!''')
                return False
        elif self.effect[0] == 4: # revive
            if target.currentHealth <= 0:
                target.status = None
                target.currentHealth = round(target.totalHealth / 2)
                return True
            else:
                print_slow(f'''{target.name} is still awake!''')
                return False
        elif self.effect[0] == 5: # full heal
            if target.currentHealth < target.totalHealth or target.status != None:
                target.currentHealth = target.totalHealth
                target.status, target.statusCounter = None, None
                return True
            else:
                print_slow(f'''{target.name} doesn't need that!''')
                return False
            
class Inventory:
 
    def __init__(self, itemList):
        self.itemList = itemList
        
    def updateList(self):
        for item in self.itemList:
            if item.qt == 0:
                self.itemList.pop(item)