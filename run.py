import random
import time
import os

randomSleep = random.randint(2,10)

print("Sleeping for: %ds" % randomSleep)

#time.sleep(randomSleep)

os.system('python genshin-os.py')

os.system('python honkai-os.py')