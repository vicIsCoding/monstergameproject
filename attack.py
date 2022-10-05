from unittest import skip
from classes import *
from misc import print_slow
from random import randrange
from operator import attrgetter

'''
FUNCTIONS IN THIS FILE ARE RELATED TO ATTACKING AND COMBAT CALCULATION
'''
unableStats = ['Asleep', 'Paralyzed']
recoverStats= ['Asleep', 'Confused']

def usedAttack(monster, attack, damage, typecheck):
    '''
    Função simples para imprimir o ataque usado em 3 casos: normal, super efetivo ou pouco efetivo.
    '''
    if typecheck > 1:
        print_slow(f'''{monster.name} used {attack.name}! It's super effective! It did {damage} points of damage.''')
    elif typecheck < 1:
        print_slow(f'''{monster.name} used {attack.name}! It's not very effective... It did {damage} points of damage.''')
    else:
        print_slow(f'''{monster.name} used {attack.name}! It did {damage} points of damage.''')

def typeCheck(move, opponent):
    '''
    Essa função compara o tipo de um ataque ao tipo principal de um monstro e define se o ataque receberá
    um multiplicador especial de efetividade (para mais ou para menos)
    '''
    typeDict = {'Fire': ['Water', 'Ground'],
                'Water': ['Grass', 'Electric', 'Poison'],
                'Grass': ['Fire', 'Ice', 'Poison'],
                'Electric' : ['Ground'],
                'Ice' : ['Fire'],
                'Ground' : ['Water'],
                'Psychic': [],
                'Normal': [],
                'Poison': ['Psychic']}
    if move.type in typeDict[opponent.type]:
        return 1.75
    elif opponent.type in typeDict[move.type] or move.type == opponent.type:
        return 0.75
    else:
        return 1

def aiSelectAttack(monsterB, monsterA):
    '''
    Essa função recebe o objeto da classe monster correspondente à IA e o objeto da classe monster correspondente ao jogador e calcula qual o melhor ataque
    dentro dos atributos objeto.moves do monstro em batlha comparado ao monstro do jogador
    '''
    moveDict = {}
    parsedDict = {}
    movePool = []
    for i in monsterB.moves:
        if (i.cost <= monsterB.currentEnergy) and (monsterB.cooldown[i.name] == 0): # confere se o monstro tem condições de usar o ataque
            movePool.append(i)
    if not movePool and monsterB.currentEnergy <= 0:
        return False
    else:
        for j in movePool:                
            if typeCheck(j, monsterA) > 1:
                moveDict[j.name] = j.cost/monsterB.currentEnergy - j.dmg/monsterA.currentHealth # calcula fator de uso para ataques com vantagem de tipo conta o oponente
        if len(moveDict) > 1:
            for i in moveDict: # deixa apenas os ataques com mair coeficiente de dano por SP
                if moveDict[i] == max(moveDict.values()):
                    parsedDict[i] = moveDict[i]
            for i in parsedDict: 
                for j in monsterB.moves:
                    if i == j.name: # bate equivalencia dos ataques por nome
                        updatedDict = {i:j} # transforma o valor duma chave no dicionario em uma instancia do objeto 'Moves'
                        parsedDict.update(updatedDict) 
            move = max(parsedDict.values(), key=attrgetter('dmg')) # escolhe o ataque cujo atributo 'dmg' for maior
            return move
        elif len(moveDict) == 0 and len(movePool) > 0:
            move = max(movePool, key= attrgetter('dmg'))
            return move
        elif len(moveDict) == 1:
            for j in monsterB.moves:
                if moveDict.keys() == j.name:
                    move = j
                    return move
        elif len(movePool) >= 1:        
            move = movePool[randrange(0, len(movePool), 1)] # escolhe um ataque aleatorio
            return move
        else:
            return monsterB.moves[randrange(0, len(monsterB.moves), 1)]    

def aiCheckParty(activePlayerMonster, activeAiMonster, aiTeam):
    
    if any(monster.currentHealth > 0 for monster in aiTeam):
        teamPool = []
        #print(aiTeam) #DEBUG ONLY
        for aiMonster in aiTeam:
            #print(aiMonster) #DEBUG ONLY
            if aiMonster == activeAiMonster:
                pass
            elif any((typeCheck(x, activePlayerMonster)) > 1 for x in aiMonster.moves) \
            and aiMonster.currentHealth > round(aiMonster.totalHealth * 0.5): # DOES THIS WORK?
                teamPool.append(aiMonster)
        if len(teamPool) > 1:
            pick = max(teamPool, key=attrgetter('currentHealth'))   
            return pick
        elif len(teamPool) == 1:
            return teamPool[0]
        elif activeAiMonster.currentHealth <= 0:
            teamPool = []
            for aiMonster in aiTeam:
                if aiMonster.status != 'Fainted':
                    teamPool.append(aiMonster)
            return teamPool[randrange(0, len(teamPool), 1)]
        elif not teamPool:
                return False
    else:
        return False

def aiUseItem(activePlayerMonster, activeAiMonster, aiTeam, aiInventory):
    if activeAiMonster.status in unableStats:
        for item in aiInventory.itemList:
            if item.name == 'Status Heal':
                item.useItem(activeAiMonster)
                return item
            
    elif activeAiMonster.currentHealth < (activeAiMonster.totalHealth / 4) and any(monster.status == 'Fainted' for monster in aiTeam):
        for monster in aiTeam:
            if monster.status == 'Fainted':
                if any(typeCheck(monster.attack, activePlayerMonster) > 1) and any(item.name == 'Revive' and item.qt > 0 for item in aiInventory.itemList):
                    for item in aiInventory.itemList:
                        if item.name == 'Revive':
                            item.useItem(monster)
                            return item
    
    elif activeAiMonster.currentEnergy < min(move.cost for move in activeAiMonster.moves):
        for item in aiInventory.itemList:
            if item.name in ['SP Potion', 'Super SP Potion', 'Max SP Potion']:
                item.useItem(activeAiMonster)
                return item
            
    elif activeAiMonster.currentHealth < activeAiMonster.totalHealth / 6:
        for item in aiInventory.itemList:
            if item.name in ['Potion', 'Super Potion', 'Max Potion']:
                item.useItem(activeAiMonster)
                return item
    else:
        return False

def aiDecision(activePlayerMonster, activeAiMonster, aiTeam, aiInventory):
    if any(move.name == 'Hypnosis' for move in activeAiMonster.moves) and activeAiMonster.status == None:
        return [move.name == 'Hypnosis' for move in activeAiMonster.moves]
    else:
        item = aiUseItem(activePlayerMonster, activeAiMonster, aiTeam, aiInventory)
        if item:
            return item
        
        move = aiSelectAttack(activeAiMonster, activePlayerMonster) #ai selects its best attack
        if move == False:
            decision = aiCheckParty(activePlayerMonster, activeAiMonster, aiTeam)
            if decision == False:
                if all([monster.status == 'Fainted' for monster in aiTeam if monster != activeAiMonster]) \
                    and activeAiMonster.currentEnergy < all(move.cost for move in activeAiMonster.moves):
                        print_slow(f'''The opponent is out of moves and monsters to use. The battle is over!''')
                        return False
            else:
                return decision
        else:
            return move

def statusAlter(move, target):
    '''
    Essa função calcula se um monstro vai sofrer alguma alteração de status
    '''
    if move.type == 'Electric' and target.type != 'Electric':
        chance = randrange(0, 100, 1) * move.dmg / target.defense
        if chance > 50:
            print_slow(f'''{target.name} is now Paralyzed!''')
            return 'Paralyzed'
        else:
            return None
    elif move.type == 'Poison' and target.type != 'Poison':
        chance = randrange(0, 100, 1) * move.dmg / target.defense
        if chance > 50:
            print_slow(f'''{target.name} is now Poisoned!''')
            return 'Poisoned'
        else:
            return None
    elif move.type == 'Psychic':
        chance = randrange(0, 100, 1) * move.dmg / target.defense
        if chance > 50:
            print_slow(f'''{target.name} is now Confused!''')
            return 'Confused'
        else:
            return None
    else:
        return None

def combat(activePlayerMonster, playerMove, activeAiMonster, aiMove):
    '''
    Essa função recebe dois objetos da classe Monster e um numero inteiro de 0 a 2 para calcular a troca de golpes entre cada instancia Monster.
    '''
    
    if playerMove == None or activePlayerMonster.status in unableStats: # apenas monstro B ataca
        aiAttackSpeed = aiMove.speed * activeAiMonster.speed * (randrange(9, 11, 1)/10)
        
        if activePlayerMonster.status in unableStats:
            print_slow(f'''{activePlayerMonster.name} is {activePlayerMonster.status}!''')
        
        if aiAttackSpeed > round(activePlayerMonster.speed * (randrange(3, 15, 1) / 10)):    
            typeCheck2 = typeCheck(aiMove, activePlayerMonster)
            activeAiMonster.currentEnergy -= aiMove.cost
            damage = round(aiMove.dmg * typeCheck2 * (activeAiMonster.attack / activePlayerMonster.defense))
            activePlayerMonster.currentHealth -= damage
            usedAttack(activeAiMonster, aiMove, damage, typeCheck2)
            if activePlayerMonster.status == None and activePlayerMonster.currentHealth > 0:
                activePlayerMonster.status = statusAlter(aiMove, activePlayerMonster)
        else:
            print(f'''{activeAiMonster.name}'s attack missed!''') 
                    
    elif aiMove == None or activeAiMonster.status in unableStats: # apenas monstro A ataca
        playerAttackSpeed = playerMove.speed * activePlayerMonster.speed * (randrange(9, 11, 1)/10)
        
        if activeAiMonster.status in unableStats:
            print_slow(f'''{activeAiMonster.name} is {activeAiMonster.status}!''')
        if playerAttackSpeed > round(activeAiMonster.speed * (randrange(3, 15, 1) / 10)):
            typeCheck1 = typeCheck(playerMove, activeAiMonster)
            activePlayerMonster.currentEnergy -= playerMove.cost
            damage = round(playerMove.dmg * typeCheck1 * (activePlayerMonster.attack / activeAiMonster.defense))
            activeAiMonster.currentHealth -= damage
            usedAttack(activePlayerMonster, playerMove, damage, typeCheck1)
            if activeAiMonster.status == None and activeAiMonster.currentHealth > 0:
                activeAiMonster.status = statusAlter(playerMove, activeAiMonster)
        else:
            print(f'''{activePlayerMonster.name}'s attack missed!''') 
                
    elif activePlayerMonster.status == 'Confused':        
        aiAttackSpeed = aiMove.speed * activeAiMonster.speed * (randrange(9, 11, 1)/10)
        playerAttackSpeed = playerMove.speed * activePlayerMonster.speed * (randrange(9, 11, 1)/10)
        
        if aiAttackSpeed > round(activePlayerMonster.speed * (randrange(3, 15, 1) / 10)):    
            typeCheck2 = typeCheck(aiMove, activePlayerMonster)
            activeAiMonster.currentEnergy -= aiMove.cost
            damage = round(aiMove.dmg * typeCheck2 * (activeAiMonster.attack / activePlayerMonster.defense))
            activePlayerMonster.currentHealth -= damage
            usedAttack(activeAiMonster, aiMove, damage, typeCheck2)
            if activePlayerMonster.status == None and activePlayerMonster.currentHealth > 0:
                activePlayerMonster.status = statusAlter(aiMove, activePlayerMonster)
        else:
            print(f'''{activeAiMonster.name}'s attack missed!''') 
        if activePlayerMonster.currentHealth > 0:
            damage = round(playerMove.dmg * typeCheck1 * (activePlayerMonster.attack / activeAiMonster.defense))
            if randrange(0, 1, 1) > 0:
                activePlayerMonster.currentHealth -= damage
                print(f'''{activePlayerMonster.name}'s hurt itself in it's confusion!''')
            else:
                if playerAttackSpeed > round(activeAiMonster.speed * (randrange(3, 15, 1) / 10)):
                    activeAiMonster.currentHealth -= damage
                    usedAttack(activePlayerMonster, playerMove, damage, typeCheck1)
                    if activeAiMonster.status == None:
                        activeAiMonster.status = statusAlter(playerMove, activeAiMonster)
                else:
                    print(f'''{activeAiMonster.name}'s attack missed!''')
    
    elif activeAiMonster.status == 'Confused':        
        playerAttackSpeed = playerMove.speed * activePlayerMonster.speed * (randrange(9, 11, 1)/10)
        aiAttackSpeed = aiMove.speed * activeAiMonster.speed * (randrange(9, 11, 1)/10)
        
        if playerAttackSpeed > round(activeAiMonster.speed * (randrange(3, 15, 1) / 10)):
            typeCheck1 = typeCheck(playerMove, activeAiMonster)
            activePlayerMonster.currentEnergy -= playerMove.cost
            damage = round(playerMove.dmg * typeCheck1 * (activePlayerMonster.attack / activeAiMonster.defense))
            activeAiMonster.currentHealth -= damage
            usedAttack(activePlayerMonster, playerMove, damage, typeCheck1)
            if activeAiMonster.status == None and activeAiMonster.currentHealth > 0:
                activeAiMonster.status = statusAlter(playerMove, activeAiMonster)
        else:
            print(f'''{activeAiMonster.name}'s attack missed!''') 
        if activeAiMonster.currentHealth > 0:
            damage = round(playerMove.dmg * typeCheck1 * (activePlayerMonster.attack / activeAiMonster.defense))
            if randrange(0, 1, 1) > 0:
                activeAiMonster.currentHealth -= damage
                print(f'''{activeAiMonster.name}'s hurt itself in it's confusion!''')
            else:
                if aiAttackSpeed > round(activePlayerMonster.speed * (randrange(3, 15, 1) / 10)):
                    activePlayerMonster.currentHealth -= damage
                    usedAttack(activeAiMonster, aiMove, damage, typeCheck2)
                    if activePlayerMonster.status == None and activePlayerMonster.currentHealth > 0:
                        activePlayerMonster.status = statusAlter(aiMove, activePlayerMonster)
                else:
                    print(f'''{activeAiMonster.name}'s attack missed!''')
    else:
        playerAttackSpeed = playerMove.speed * activePlayerMonster.speed * (randrange(9, 11, 1)/10)
        aiAttackSpeed = aiMove.speed * activeAiMonster.speed * (randrange(9, 11, 1)/10)
        typeCheck1= typeCheck(playerMove, activeAiMonster)
        typeCheck2 = typeCheck(aiMove, activePlayerMonster)
        activePlayerMonster.currentEnergy -= playerMove.cost
        activeAiMonster.currentEnergy -= aiMove.cost
        
        if playerAttackSpeed > aiAttackSpeed:
            if playerAttackSpeed > round(activeAiMonster.speed * (randrange(3, 15, 1) / 10)):
                damage = round(playerMove.dmg * typeCheck1 * (activePlayerMonster.attack / activeAiMonster.defense))
                activeAiMonster.currentHealth = activeAiMonster.currentHealth - damage
                usedAttack(activePlayerMonster, playerMove, damage, typeCheck1)
                if activeAiMonster.status == None and activeAiMonster.currentHealth > 0:
                    activeAiMonster.status = statusAlter(playerMove, activeAiMonster)
            else:
                print_slow(f'''{activePlayerMonster.name}'s attack missed!''')    
            if activeAiMonster.currentHealth > 0:
                if aiAttackSpeed > round(activePlayerMonster.speed * (randrange(3, 15, 1) / 10)):
                    damage = round(aiMove.dmg * typeCheck2 * (activeAiMonster.attack / activePlayerMonster.defense))
                    activePlayerMonster.currentHealth -= damage
                    usedAttack(activeAiMonster, aiMove, damage, typeCheck2)
                    if activePlayerMonster.status == None and activePlayerMonster.currentHealth > 0:
                        activePlayerMonster.status = statusAlter(aiMove, activePlayerMonster)
                else:
                    print_slow(f'''{activeAiMonster.name}'s attack missed!''')
        elif playerAttackSpeed < aiAttackSpeed:
            if aiAttackSpeed > round(activePlayerMonster.speed * (randrange(3, 15, 1) / 10)):
                damage = round(aiMove.dmg * typeCheck2 * (activeAiMonster.attack / activePlayerMonster.defense))
                activePlayerMonster.currentHealth -= damage
                usedAttack(activeAiMonster, aiMove, damage, typeCheck2)
                if activePlayerMonster.status == None and activePlayerMonster.currentHealth > 0:
                   activePlayerMonster.status = statusAlter(aiMove, activePlayerMonster)
            else:
                print(f'''{activeAiMonster.name}'s attack missed!''')       
            if activePlayerMonster.currentHealth > 0:
                if playerAttackSpeed > round(activeAiMonster.speed * (randrange(3, 15, 1) / 10)):
                    damage = round(playerMove.dmg * typeCheck1 * (activePlayerMonster.attack / activeAiMonster.defense))
                    activeAiMonster.currentHealth -= damage
                    usedAttack(activePlayerMonster, playerMove, damage, typeCheck1)
                    if activeAiMonster.status == None and activePlayerMonster.currentHealth > 0:
                        activeAiMonster.status = statusAlter(playerMove, activeAiMonster)
                else:
                    print(f'''{activePlayerMonster.name}'s attack missed!''')   
        else:
            if playerAttackSpeed > round(activeAiMonster.speed * (randrange(3, 15, 1) / 10)):
                damage = round(playerMove.dmg * typeCheck1 * (activePlayerMonster.attack / activeAiMonster.defense))
                activeAiMonster.currentHealth -= damage
                usedAttack(activePlayerMonster, playerMove, damage, typeCheck1)
                if activeAiMonster.status == None and activeAiMonster.currentHealth > 0:
                    activeAiMonster.status = statusAlter(playerMove, activeAiMonster)
            else:
                print(f'''{activePlayerMonster.name}'s attack missed!''')      
            if activeAiMonster.currentHealth > 0:
                if aiAttackSpeed > round(activePlayerMonster.speed * (randrange(3, 15, 1) / 10)):
                    damage = round(aiMove.dmg * typeCheck2 * (activeAiMonster.attack / activePlayerMonster.defense))
                    activePlayerMonster.currentHealth -= damage
                    usedAttack(activeAiMonster, aiMove, damage, typeCheck2)
                    if activePlayerMonster.status == None and activePlayerMonster.currentHealth > 0:
                        activePlayerMonster.status = statusAlter(aiMove, activePlayerMonster)
                else:
                    print(f'''{activeAiMonster.name}'s attack missed!''')

def checkParty(team, arg):
    '''
    Essa função calcula se o jogador tem opções de monstros para lutar no seu time
    '''    
    usable_monsters = []
    validSelection = False
    if arg == 1:
        for item in team:
            if item.currentHealth > 0:
                usable_monsters.append(item)
                
        if len(usable_monsters) > 1:
            while validSelection == False:
                print_slow(f'''You have {len(usable_monsters)} monsters able to fight!''')
                print_slow(f'''Which one would you like to choose?''')
                for i, j in enumerate(usable_monsters):
                    print_slow(f'''{i + 1} - {j.name}''')
                chosen_monster = int(input())
                if chosen_monster > 0 and chosen_monster <= len(usable_monsters): 
                    validSelection == True
                    return usable_monsters[chosen_monster - 1]
                elif chosen_monster > len(usable_monsters) or chosen_monster == 0:
                    print_slow(f'''Invalid selection!''')
                    continue
            
        elif len(usable_monsters) == 1:
            return usable_monsters[0]
        else:
            print_slow(f'''Your monsters can't fight anymore. You lost!''')
    else:
        for item in team:
            if item.currentHealth > 0:
                usable_monsters.append(item)
        if len(usable_monsters) > 1:
            while validSelection == False:
                print_slow(f'''You have {len(usable_monsters)} monsters able to fight!''')
                print_slow(f'''Which one would you like to choose?''')
                for i, j in enumerate(usable_monsters):
                    print_slow(f'''{i + 1} - {j.name}''')
                print_slow(f'''{len(usable_monsters) + 1} - Cancel''')
                chosen_monster = int(input()) # needs safeguard
                if chosen_monster > 0 and chosen_monster < (len(usable_monsters) + 1): 
                    validSelection = True
                    return usable_monsters[chosen_monster - 1]
                elif chosen_monster == len(usable_monsters) + 1:
                    validSelection = True
                    return False
                else:
                    print_slow(f'''Invalid selection!''')
                    continue
        elif len(usable_monsters) == 1:   
            while validSelection == False:
                print_slow(f'''There's only {usable_monsters[0].name} avaliable. Do you want to switch? Y/N''')
                playerChoice = int(input()) # needs safeguard
                if playerChoice == 'Y':
                    validSelection = True
                    return usable_monsters[0]
                elif playerChoice == 'N':
                    validSelection = True
                    return False
                else:
                    continue

def selectItem(inventory):
    '''
    Essa função exibe os itens no inventário do jogador e retorna a escolha do mesmo
    '''
    validSelection = False
    while validSelection == False:
        print_slow(f'''Which item do you wanna use?''')
        for nmbr, item in enumerate(inventory.itemList):
            print_slow(f'''{nmbr + 1} - {item.name}''')
        print_slow(f'''{len(inventory.itemList) + 1} - Cancel''')
        playerChoice = int(input())
        if playerChoice > 0 and playerChoice <= len(inventory.itemList):
            validSelection == True
            item = inventory.itemList[playerChoice - 1]
            return item
        elif playerChoice == len(inventory.itemList) + 1:
            validSelection == True
            return False
        else:
            print_slow(f'''That's not a valid entry!''')
            continue
    
    pass  

def select_Attack(monsterA):
    '''
    Essa função recebe um objeto da classe Monster como atributo, exibe os objetos da classe Moves pertencentes ao atributo objeto.moves, determina quais
    podem ser usados e retorna o objeto equivalente ao ataque escolhido
    '''
    selection = False
    while selection == False:
        print_slow(f'''You have {monsterA.currentEnergy}SP left.''')
        print(f'''{monsterA.moves[0].name} | {monsterA.moves[0].dmg} dmg | {monsterA.moves[0].cost} energy | {monsterA.cooldown[monsterA.moves[0].name]} cooldown''')
        print(f'''{monsterA.moves[1].name} | {monsterA.moves[1].dmg} dmg | {monsterA.moves[1].cost} energy | {monsterA.cooldown[monsterA.moves[1].name]} cooldown''')
        print(f'''{monsterA.moves[2].name} | {monsterA.moves[2].dmg} dmg | {monsterA.moves[2].cost} energy | {monsterA.cooldown[monsterA.moves[2].name]} cooldown''')
        print(f'''{monsterA.moves[3].name} | {monsterA.moves[3].dmg} dmg | {monsterA.moves[3].cost} energy | {monsterA.cooldown[monsterA.moves[3].name]} cooldown''')
        move = input('''\nChoose which move to use: 1, 2, 3 or 4 - or use 5 to return.\n''')
        if move not in ['1', '2', '3', '4', '5']:
            print_slow('''Only 1, 2, 3, 4 or 5 for accepted!''')
        elif move == '5':
            selection = True
            return False
        else:
            move = monsterA.moves[int(move) - 1]
            if (move.cost <= monsterA.currentEnergy) and (monsterA.cooldown[move.name] == 0):
                selection == True
                if move.cooldown > 0:
                    monsterA.cooldown[move.name] = move.cooldown        
                return move
            elif monsterA.cooldown[move.name] > 0:
                print_slow('''You need to wait before using that again.''')
            else:
                print_slow('''You don't have enough energy for that!''')

def playerChoice(activePlayerMonster, playerTeam, playerInventory):
    '''
    Essa função exibe as opções do jogador e retorna a escolha do mesmo
    '''
    validSelection = False 
    while validSelection == False:
        print_slow('''What do you wanna do?\n1 - Attack\n2 - Change monster\n3 - Use item\n4 - Stop fighting?''')
        playerChoice = int(input())
        print('\n')
        if playerChoice == 1:
            move = select_Attack(activePlayerMonster)
            if move == False:
                continue
            else:
                validSelection = True
                return move
        
        elif playerChoice == 2:
            newmon = checkParty(playerTeam, 0)
            if newmon == False:
                continue
            elif newmon == activePlayerMonster:
                print_slow(f'''{activePlayerMonster.name} is already in battle!''')
                continue
            else:
                print_slow(f'''{activePlayerMonster.name}, come back! {newmon.name} it's your turn!''')
                activePlayerMonster = newmon
                validSelection = True
                return activePlayerMonster
        
        elif playerChoice == 3:
            item = selectItem(playerInventory)
            if item == False:
                continue
            else:
                print(f'''Who do you want to use it on?''')
                for i, j in enumerate(playerTeam):
                        print_slow(f'''{i + 1} - {j.name}''')
                chosen_monster = int(input())
                if chosen_monster > 0 and chosen_monster <= len(playerTeam):
                    if item.useItem(playerTeam[chosen_monster - 1]) == False:
                        continue
                    else:
                        validSelection = True
                        return item
        
        elif playerChoice == 4:
            validSelection = True
            return False    
        else:
            print_slow('Invalid input, try again.\n')

def battleStage(activePlayerMonster, playerTeam, playerInventory, activeAiMonster, aiTeam, aiInventory):
    
    '''
    This function defines what happens based on the choice of the player and the AI
    '''
    ### add text for sending out monster or using item
    
    aiReturn = aiDecision(activePlayerMonster, activeAiMonster, aiTeam, aiInventory)
    playerReturn = playerChoice(activePlayerMonster, playerTeam, playerInventory)
    
    
    for monster in [activePlayerMonster, activePlayerMonster]:
        if monster.status != None and monster.statusCounter == 0:
            if monster.status == 'Asleep':
                print_slow('''{monster.name} woke up!''')
                monster.status = None
                monster.statusCounter = None
            elif monster.status == 'Confused':
                print_slow(f'''{monster.name} snapped out of confusion!''')
                monster.status = None
                monster.statusCounter = None
    
    if type(playerReturn) in [Monster, Item] or playerReturn == False and type(aiReturn) == Moves: #check if player used item, changed monster or quit
        if playerReturn == False or aiReturn == False: # PLAYER QUITS
            return False
        
        elif type(playerReturn) == Monster:
            activePlayerMonster = playerReturn
            combat(activePlayerMonster, None, activeAiMonster, aiReturn)
            if aiReturn.name == 'Hypnosis':
                activePlayerMonster.status == 'Asleep'
            return activePlayerMonster, activeAiMonster
        
        elif type(playerReturn) == Item:
            playerReturn.qt -= 1
            combat(activePlayerMonster, None, activeAiMonster, aiReturn)
            if aiReturn.name == 'Hypnosis':
                activePlayerMonster.status == 'Asleep'
            return activePlayerMonster, activeAiMonster
        
    elif type(aiReturn) in [Monster, Item] and type(playerReturn) == Moves: #if player choose attack but AI didn't:
        if type(aiReturn) == Monster:
            print_slow(f'''The opponent's {activeAiMonster.name} is leaving.''')
            activeAiMonster = aiReturn
            print_slow(f'''{activeAiMonster.name} is coming out to fight!''')
            combat(activePlayerMonster, playerReturn, activeAiMonster, None)
            if playerReturn.name == 'Hypnosis':
                activeAiMonster.status == 'Asleep'
            return activePlayerMonster, activeAiMonster
        
        elif type(aiReturn) == Item:
            aiReturn.qt -=1
            combat(activePlayerMonster, playerReturn, activeAiMonster, None)
            if playerReturn.name == 'Hypnosis':
                activeAiMonster.status == 'Asleep'
            return activePlayerMonster, activeAiMonster
               
    elif type(playerReturn) in [Monster, Item] and type(aiReturn) in [Monster, Item]:
        if type(playerReturn) == Monster and type(aiReturn) == Monster:
            activePlayerMonster = playerReturn
            print_slow(f'''The opponent's {activeAiMonster.name} is leaving.''')
            activeAiMonster = aiReturn
            print_slow(f'''{activeAiMonster.name} is coming out to fight!''')
            return activePlayerMonster, activeAiMonster
        
        elif type(playerReturn) == Item and type(aiReturn) == Monster:
            playerReturn.qt -=1
            print_slow(f'''The opponent's {activeAiMonster.name} is leaving.''')
            activeAiMonster = aiReturn
            print_slow(f'''{activeAiMonster.name} is coming out to fight!''')
            return activePlayerMonster, activeAiMonster
        
        elif type(playerReturn) == Monster and type(aiReturn) == Item:
            print_slow(f'''{activePlayerMonster.name} is coming out to fight!''')
            print_slow(f'''The opponent has used a {aiReturn.name}!''')
            activePlayerMonster = playerReturn
            aiReturn.qt -= 1
            return activePlayerMonster, activeAiMonster
        
        elif type(playerReturn) == Item and type(aiReturn) == Item:
            print_slow(f'''The opponent has used a {aiReturn.name}!''')
            playerReturn.qt -= 1
            aiReturn.qt -= 1
            return activePlayerMonster, activeAiMonster
                
    else:   #combat with both monster's moves
        combat(activePlayerMonster, playerReturn, activeAiMonster, aiReturn)
        if playerReturn.name == 'Hypnosis':
                activeAiMonster.status == 'Asleep'
        if aiReturn.name == 'Hypnosis':
                activePlayerMonster.status == 'Asleep'
        return activePlayerMonster, activeAiMonster