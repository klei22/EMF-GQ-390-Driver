import time
from EMF390 import EMF390

emf = EMF390(port="/dev/gqemf390", baudrate=115200)

try:
    while True:
        print("EMF Value:", emf.get_emf())
        time.sleep(2)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    emf.close()

