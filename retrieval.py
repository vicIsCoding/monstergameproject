import random; from random import randrange
from classes import *
import pandas as pd
from items import itemList

def retrieve_Monster(monsterID):
    '''
    Essa função lê o ID de um monstro num dataframe gerado a partir
    de uma tabela CSV e copia os valores para um objeto instanciado
    da classe Monster.
    Ela também pré-seleciona 4 ataques dentro de todos os possíveis
    ataques listados para aquele monstro na tabela.
    '''
    df = pd.read_csv(r'C:\Users\Victor\Documents\Python Projects\CLUTTER\Monster Game\monsters.csv')
    getRow = (df.iloc[monsterID])
    name, type, attack, defense, speed, health, energy = getRow.values[0], getRow.values[1], int(getRow.values[3]), int(getRow.values[4]), int(getRow.values[5]), int(getRow.values[6]), int(getRow.values[7])
    moves = []
    df = pd.read_csv(r'C:\Users\Victor\Documents\Python Projects\CLUTTER\Monster Game\moves.csv')
    moveList = df.values.tolist()
    for move in moveList:
        if move[1] == type or move[1] == 'Normal':
            moves.append(Moves(move[0], move[1], move[2], move[3], move[4], move[5]))    
    cooldown = {}
    monster = Monster(name, type, moves, attack, defense, speed, health, health, energy, energy, cooldown, None, None)
    monster.moves = random.sample(moves, 4)
    
    monster.cooldown = {monster.moves[0].name : 0, \
                    monster.moves[1].name : 0, \
                    monster.moves[2].name : 0, \
                    monster.moves[3].name : 0}
    
    return monster

def randomize_Stats(monster):
    '''
    Essa função altera os valores dos atributos de um Monstro de maneira
    aleatória dentro dum intervalo pré determinado.
    '''
    monster.attack = round(monster.attack * (randrange(9, 11, 1) / 10))
    monster.defense = round(monster.defense * (randrange(9, 11, 1) / 10))
    monster.totalHealth = monster.currentHealth = round(monster.totalHealth * (randrange(8, 12, 1) / 10))
    monster.totalEnergy = monster.currentEnergy = round(monster.totalEnergy * (randrange(8, 12, 1) / 10))
    monster.speed = round(monster.speed * (randrange(9, 11, 1) / 10))

def teamGen(size):
    counter = 0
    team = []
    while counter < size:
        team.append(retrieve_Monster(randrange(0, 33, 1)))
        randomize_Stats(team[counter])
        counter += 1
    return team

def initInventories():
    playerItems = []
    aiItems = []
    
    for eachInv in [playerItems, aiItems]:
        counter = 0
        itemNmbr = randrange(1, 10, 1)
        while counter < itemNmbr:
            item = itemList[randrange(0, (len(itemList) - 1), 1)]
            if item in eachInv:
                item.qt += 1
            else:
                eachInv.append(item)
            counter += 1
        
    playerInventory = Inventory(playerItems)
    aiInventory = Inventory(aiItems)
    
    return playerInventory, aiInventory