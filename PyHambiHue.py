#!/usr/bin/python
import os
from time import sleep
import sys
import threading

try:
    import mss
    from qhue import Bridge
    from PIL import Image,ImageDraw
    from qhue import create_new_username
    import json
    from math import ceil
except ImportError:
    print("Requirements not satisfied, installing...")
    os.system('pip install pillow')
    os.system('pip install mss')
    os.system('pip install qhue')
    print("Please restart the script")
    sleep(300)
directory = os.path.dirname(os.path.realpath(__file__))+"/"

if len(sys.argv)>1 :
    choice = sys.argv[1]
else:
    choice = False

col_dom = False

def init_config():
    IP = str(input("Please enter your hue bridge IP address: "))
    if IP == "":
        print('Visit https://huetips.com/help/how-to-find-my-bridge-ip-address/ to know how to get your bridge IP address')
        sleep(300)

    username = create_new_username(IP)
    config={
    'IP':IP,
    'username':username,
    "loops_per_sec": 2.0,
    "m_sat": 185,
    "r_sat": 70,
    "m_bri": 70,
    "r_bri": 50,
    "divider": 5,
    "crop" : 1,
    "bezel": 1
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

    with open(directory+'config.json', 'w') as fp:
        json.dump(config, fp)

def readUsername():
    try:
        with open(directory+'config.json') as data_file:
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
print()

if not choice:
    answer = input("Select an option (leave blank for last settings)\n\n1 : Last settings\n2 : comfort mode\n3 : gaming mode\n4 : frame mode\n5 : full range mode\n6 : custom profile settings\n\n")
else:
    answer = choice
loops_per_sec=""
if answer == "6":
    print("\n! You can always press enter to validate the previous value !\n")
    loops_per_sec = input("How many loops per second? (0-10) (Last "+str(config['loops_per_sec'])+") : ")
    if loops_per_sec == "":
        loops_per_sec = config['loops_per_sec']
    else:
        loops_per_sec = float(loops_per_sec)
    m_sat = input("Minimum saturation. must be integer, 0-255 (Last "+str(config['m_sat'])+") : ")
    if m_sat == "":
        m_sat = config['m_sat']
        print(m_sat)
    else:
        m_sat = int(m_sat)
    r_sat = input("Saturation variation. must be integer, 0-255, variation + minimum value must not exceed 255 (max "+str(255-m_sat)+") (Last "+str(config['r_sat'])+") : ")
    if r_sat == "":
        r_sat = config['r_sat']
        print(r_sat)
    else:
        r_sat = int(r_sat)
    m_bri = input("Minimum luminosity. must be integer, 0-255 (Last "+str(config['m_bri'])+") : ")
    if m_bri == "":
        m_bri = config['m_bri']
        print(m_bri)
    else:
        m_bri = int(m_bri)
    r_bri = input("Luminosity variation. must be integer, 0-255, variation + minimum value must not exceed 255 (max "+str(255-m_bri)+") (Last "+str(config['r_bri'])+") : ")
    if r_bri == "":
        r_bri = config['r_bri']
        print(r_bri)
    else:
        r_bri = int(r_bri)
    divider = input("Performance level. From one to ten. One being a spare petacore on your spaceship and ten a potato with the flu : (Last "+str(config['divider'])+") : ")
    if divider == "":
        divider = config['divider']
        print(divider)
    else:
        divider = int(divider)

    crop  = input("Crop proportion from the center of the image. Must be minimum one (=no crop), can be float (Last "+str(config['crop'])+") : ")
    if crop != "":
        crop = float(crop)
    elif crop == "":
        crop = config['crop']
        print(crop)
    if crop != 1:
        bezel = input("From the crop, keep the frame(1) or keep the center image(2)? (Last "+str(config['bezel'])+") : ")
        if bezel == "":
            bezel = config['bezel']
            print(bezel)
        else:
            bezel = int(bezel)
    else:
        bezel = 2

elif answer == "2":
    loops_per_sec = 2
    m_sat = 70
    r_sat = 185
    m_bri = 80
    r_bri = 70
    divider = 4
    crop = 1
    bezel = 2
elif answer == "3":
    loops_per_sec = 12.5
    m_sat = 205
    r_sat = 50
    m_bri = 100
    r_bri = 155
    divider = 5
    crop = 1.5
    bezel = 2
elif answer == "4":
    loops_per_sec = 4
    m_sat = 205
    r_sat = 50
    m_bri = 120
    r_bri = 70
    divider = 4
    crop = 1.3
    bezel = 1
elif answer == "5":
    loops_per_sec = 10
    m_sat = 0
    r_sat = 255
    m_bri = 0
    r_bri = 255
    divider = 5
    crop = 1
    bezel = 2
else:
    loops_per_sec = config['loops_per_sec']
    divider = config['divider']
    m_sat = config['m_sat']
    m_bri = config['m_bri']
    r_sat = config['r_sat']
    r_bri = config['r_bri']
    crop  = config['crop']
    bezel = config['bezel']

config['loops_per_sec'] = loops_per_sec
config['divider'] = divider
config['m_sat'] = m_sat
config['m_bri'] = m_bri
config['r_sat'] = r_sat
config['r_bri'] = r_bri
config['crop']  = crop
config['bezel'] = bezel

with open(directory+'config.json', 'w') as fp:
    json.dump(config, fp)

t_sleep = 1/loops_per_sec
transitiontime = ceil(t_sleep*10)

def crop_dimensions(screen,factor):
    dimensions = {}
    dimensions['left']   = int(screen['width']/2-screen['width']/(2*factor)+screen['left'])
    dimensions['top']    = int(screen['height']/2-screen['height']/(2*factor)+screen['top'])
    dimensions['width']  = int(screen['width']/factor)
    dimensions['height'] = int(screen['height']/factor)

    return (dimensions)


def daemonizer(fName):
    try:
        daemon = threading.Thread(target=fName)
        daemon.daemon = True
        daemon.start()
    except Exception as e:
        print(e)

def most_frequent_colour(image):
    w, h = image.size
    pixels = image.getcolors(w * h)
    most_frequent_pixel = pixels[0]
    for count, colour in pixels:
        if count > most_frequent_pixel[0]:
            most_frequent_pixel = (count, colour)
    return most_frequent_pixel

def average_colour(image,bezel,screen,coord,scnst):
    w, h = image.size
    image = image.resize((int(w/divider),int(h/divider)), Image.ANTIALIAS)
    if scnst:
        im = image.load()
    w, h = image.size
    x1 = (screen['left']-coord['left'])/divider
    x2 = (screen['left']-coord['left']+screen['width'])/divider
    y1 = (screen['top']-coord['top'])/divider
    y2 = (screen['top']-coord['top']+screen['height'])/divider
    r=g=b=c=0
    for haut in range(0,h):
        for large in range(0,w):
            if scnst and bezel == 1 and not ((x1 > large or large > x2) or (y1 > haut or haut > y2)):
                im[large,haut] = (0,0,0)
            if bezel == 1 and ((x1 > large or large > x2) or (y1 > haut or haut > y2)):
                c+=1;
                pix = image.getpixel((large,haut))
                r+=pix[0]
                g+=pix[1]
                b+=pix[2]
            elif bezel == 2:
                c+=1;
                pix = image.getpixel((large,haut))
                r+=pix[0]
                g+=pix[1]
                b+=pix[2]
    r=int(r/c)
    g=int(g/c)
    b=int(b/c)

    if scnst:
        image.save('sc.png')

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
    try:
        lights[chosen_light].state(transitiontime=transitiontime,hue=hue,sat=sat,bri=bri)
    except Exception as e:
        pass

def loop_step(monitor,screen,scnst):
    if bezel == 2:
        sct_img = sct.grab(screen)
    else:
        sct_img = sct.grab(monitor)

    im = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    if col_dom:
        main_pixel = most_frequent_colour(im)
        r = main_pixel[1][0]
        g = main_pixel[1][1]
        b = main_pixel[1][2]
    else:
        main_pixel = average_colour(im,bezel,screen,sct.monitors[monitor_number],scnst)
        r = main_pixel[0]
        g = main_pixel[1]
        b = main_pixel[2]

    HSB = rgb2hsv(r, g, b)
    sat_exponential = 1-(1-HSB[1])*(1-HSB[1])

    H = int(65535/360*HSB[0])
    S = int(r_sat*sat_exponential)+m_sat
    B = int(r_bri*HSB[2])+m_bri

    daemonizer(send_hue(H,S,B))


if __name__ == '__main__':
    monitor = sct.monitors[monitor_number]
    screen  = crop_dimensions(monitor,crop)
    print("")
    print("- PyAmbiHue initialised -")
    print("")
    print("Time interval      :","%.2f" % t_sleep,"sec.")
    print("Refresh per second :",loops_per_sec)
    print("")
    print("Minimum saturation :",m_sat)
    print("Maximum saturation :",m_sat+r_sat)
    print("Minimum luminosity :",m_bri)
    print("Maximum luminosity :",m_bri+r_bri)
    print("Performance profile:",divider)
    print("")
    print("Crop factor :",crop)
    if bezel == 2:
        print("Crop method : keep center")
        print("Effort (pixels per second/1000) :", round(loops_per_sec/1000*(int(screen['width']/divider)*int(screen['height']/divider)),3))
    else:
        print("Crop method : keep frame")
        print("Effort (pixels per second/1000) :", round(loops_per_sec/1000*(int(monitor['width']/divider)*int(monitor['height']/divider)-int(screen['width']/divider)*int(screen['height']/divider)),3))
    print("")
    loop_step(monitor,screen,True)

    while True:
        loop_step(monitor,screen,False)
        sleep(t_sleep)
