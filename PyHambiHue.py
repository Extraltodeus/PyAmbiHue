import threading
from time import sleep
import mss
from qhue import Bridge
from PIL import Image
from qhue import create_new_username
import json

def init_config():
    IP = str(input("Please enter your hue bridge IP address: "))
    if IP == "":
        print('Visit https://huetips.com/help/how-to-find-my-bridge-ip-address/ to know how to get your bridge IP address')
        sleep(300)
    username = create_new_username(IP)
    config={
    'IP':IP,
    'username':username
    }

    b = Bridge(config['IP'], config['username'])
    print('Please enter the number beside the lamp that you want to use :')
    for lamp in b.lights():
        print(lamp,b.lights()[lamp]['name'])
    print()
    chosen_light = input()
    if chosen_light == "":
        print()
        print()
        print("------- Please enter a number correspond to the desired bulb : -------")
        print()
        chosen_light = input()
        print()
        print()

    config['chosen_light'] = int(chosen_light)

    with open('./config.json', 'w') as fp:
        json.dump(config, fp)

def readUsername():
    try:
        with open('./config.json') as data_file:
            config = json.load(data_file)
        return config
    except Exception as e:
        init_config()
        return readUsername()

config = readUsername()

b = Bridge(config['IP'], config['username'])

lights = b.lights
sct = mss.mss()

# Tweakable variable below. r_ and m_ variable must have a sum of max 255
monitor_number=1
chosen_light = config['chosen_light']
t_sleep = 0.1

r_sat = 0
r_bri = 55
m_sat = 255
m_bri = 200

def daemonizer(fName):
    try:
        daemon = threading.Thread(target=fName)
        daemon.daemon = True
        daemon.start()
    except Exception as e:
        print(e)

def average_colour(image):
    divider=5
    w, h = image.size
    image = image.resize((int(w/divider),int(h/divider)), Image.ANTIALIAS)
    w, h = image.size

    r=g=b=0
    for haut in range(0,h):
        for large in range(0,w):
            pix = image.getpixel((large,haut))
            r+=pix[0]
            g+=pix[1]
            b+=pix[2]
    r=int(r/(w*h))
    g=int(g/(w*h))
    b=int(b/(w*h))
    return (r,g,b)

def rgb2hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df/mx
    v = mx
    return h, s, v

def send_hue(hue,sat,bri):
    lights[chosen_light].state(transitiontime=1,hue=hue,sat=sat,bri=bri)

if __name__ == '__main__':
    print("")
    print("- PyAmbiHue initialised -")
    print("")
    
    while True:
        sct_img = sct.grab(sct.monitors[monitor_number])

        im = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        main_pixel = average_colour(im)
        r = main_pixel[0]
        g = main_pixel[1]
        b = main_pixel[2]

        HSB = rgb2hsv(r, g, b)

        H = int(65535/360*HSB[0])
        S = int(r_sat*HSB[1])+m_sat
        B = int(r_bri*HSB[2])+m_bri

        daemonizer(send_hue(H,S,B))

        sleep(t_sleep)

