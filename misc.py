import sys; import time

def print_slow(str):
    '''
    Essa função imprime as frases letra por letra emulando o efeito de RPGs antigos.
    Retirada de https://stackoverflow.com/questions/4099422/printing-slowly-simulate-typing
    '''
    for letter in str:
        sys.stdout.write(letter)
        sys.stdout.flush()
        time.sleep(0.01)
    time.sleep(0.05)
    print('\n')
    
def calcPoison(monster):
    monster.currentHealth -= round(monster.totalHealth / monster.defense)
    print_slow(f'''{monster.name} is hurt by poison!''')