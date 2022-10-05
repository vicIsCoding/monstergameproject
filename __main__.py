from random import randrange
from retrieval import initInventories, teamGen
from attack import battleStage, checkParty, aiCheckParty
from misc import print_slow, calcPoison

# Implementar balanceamento de times
# Implementar interface TKinter
# implementar debug (status change, hp change, sp change, etc)

def fight(playerTeam, playerInventory, aiTeam, aiInventory):
    '''
    Loop de batalha principal
    '''
    activePlayerMonster, activeAiMonster = playerTeam[0], aiTeam[0]
    print_slow(f'''You're sending out a {activePlayerMonster.name}! It has {activePlayerMonster.currentHealth}HP and {activePlayerMonster.currentEnergy}SP.''')
    print_slow(f'''Your opponent is sending out a {activeAiMonster.name}! It has {activeAiMonster.currentHealth}HP.''')
    while any(monster.currentHealth > 0 for monster in playerTeam) \
      and any(monster.currentHealth > 0 for monster in aiTeam):
        
        result = battleStage(activePlayerMonster, playerTeam, playerInventory, activeAiMonster, aiTeam, aiInventory)
        if result == False:
            break
        else:
            activePlayerMonster, activeAiMonster = result[0], result[1]
                
        for monster in [activePlayerMonster, activeAiMonster]:
            if monster.status == 'Poisoned' and monster.currentHealth > 0:
                calcPoison(monster)
            elif monster.status not in ['Poisoned', 'Paralyzed'] and monster.status != None:
                monster.statusCounter -= 1
        
        if activePlayerMonster.currentHealth <= 0:
            activePlayerMonster.status = 'Fainted'
            print_slow(f'''{activePlayerMonster.name} has fainted!''')
            activePlayerMonster = checkParty(playerTeam, 1)
            
        if activeAiMonster.currentHealth <= 0:
            activeAiMonster.status = 'Fainted'
            print_slow(f'''{activeAiMonster.name} has fainted!''')
            activeAiMonster = aiCheckParty(activePlayerMonster, activeAiMonster, aiTeam)
            if activeAiMonster == False:
                print_slow('''The opponent is out of monster to use. You've won!''')
                break

        for monster in [activePlayerMonster, activeAiMonster]:
            for i in monster.cooldown:
                if monster.cooldown[i] > 0:
                    monster.cooldown[i] -= 1
        
        for inventory in [playerInventory, aiInventory]:
            inventory.updateList
        
        print_slow(f'''Your {activePlayerMonster.name} has {activePlayerMonster.currentHealth}HP.''')
        print_slow(f'''The opponent's {activeAiMonster.name} has {activeAiMonster.currentHealth}HP.''')
    
    
if __name__ == '__main__':
    inventories = initInventories()
    fight(teamGen(6), inventories[0], teamGen(6), inventories[1])
    pass