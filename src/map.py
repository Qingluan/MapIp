#!/usr/bin/env python3
import sys
import re
import os
import io
from functools import reduce
import argparse
import time
import asyncio
import urllib.request as ur
import aiohttp
import matplotlib.pylab as plt 
from matplotlib.lines import Line2D
import numpy as np
import threading 
from mpl_toolkits.basemap import Basemap
from concurrent.futures import ProcessPoolExecutor

basic_ip = "http://ipinfo.io"
file_path = os.environ["HOME"]
plt.ion()
locate_file_tell = 0
old_size = os.stat("./ips.loc").st_size

@asyncio.coroutine
def _single_ip_deal_with(*args):
        print("create : %s"%(time.asctime()))
        real_url = basic_ip+"/" +"/".join(args)
        resp = yield from aiohttp.request("GET",real_url)
        data =  yield from resp.read()
        print(data.decode().strip())
        return data.decode()
@asyncio.coroutine 
def get_loc(ips,search_option="loc"):
    res = []
    for ip in ips:
        ip_loc = yield from _single_ip_deal_with(ip,search_option)
        res.append(ip_loc)
    return res

def get_locations(*args):
    print("create : %s"%(time.asctime()))
    real_url = basic_ip+"/" +"/".join(args)
    res = ur.urlopen(real_url)
    return res.read()

def cal_point(map,lat,lon):
    xmin = map.xmin
    xmax = map.xmax
    ymin = map.ymin
    ymax = map.ymax
    lat_min = map.latmin
    lat_max = map.latmax
    lon_min = map.lonmin
    lon_max = map.lonmax
    x = (lon - lon_min)/(lon_max -lon_min) * (xmax - xmin)  + xmin
    y = (lat - lat_min)/(lat_max - lat_min)* (ymax - ymin)  + ymin
    return (x,y)



class ip_map(object):

    def __init__(self,*map_args,**map_kargs):
        #plt.ion()
        self.fig,self.ax = plt.subplots(figsize=(8,12))
        kargs = self.defaut_map_properties(**map_kargs)
        print(kargs)
        self.map = Basemap(*map_args,**kargs)
        
        self.ax.set_title("lat : %s | lon : %s "%(kargs["lat_0"],kargs["lon_0"]))
    
        self.x_point_data = [0]
        self.y_point_data = [0]
        self.next_map = None
        #plt.ion()
    def draw_init(self,**kargs):
        self.fig,self.ax = plt.subplots(**kargs)

    def defaut_map_properties(self,**kargs):
        if "projection" not in kargs:
            kargs["projection"] = "ortho"
        if "lat_0" and "lon_0" not in kargs:
            kargs["lat_0"] = 30
            kargs["lon_0"] = 120
             
        if "lat_0" in kargs:
            kargs["lat_0"] = float(kargs["lat_0"])
        
        return kargs

    def translate(self,data_x,data_y):
        location_x , location_y = self.map(data_x,data_y)
        return location_x , location_y


    
    def over_map_handler(self,func_str,*args,**kargs):
        """
            this is a good abstract method .. may be will been some bug
        """

        if self.next_map:
            print("draw in sub map ",end="")
            func = getattr(self.next_map,func_str)
            func(*args,**kargs)
        else:
            print("this point is over .. draw another ... ",end="")
            self.next_map = ip_map(lat_0=args[0],lon_0=args[1])
            self.next_map.default_draw()
            self.over_map_handler(func_str,*args,**kargs)
            print("ok")


    def locate_ip(self,lat,lon,marker="v",color="red"):
        x,y = self.map(lon,lat)
        if x == 1e+30:  
            print("over ip ")
            self.over_map_handler("locate_ip",lat,lon,marker,color)
        else:
            try:
                print(marker,color,"\nlatitude:%8s\nlongitude:%8s"%(lat,lon)  )
                res = self.ax.plot(x,y,marker=marker,color=color)
                self.fig.canvas.draw()
                print(self.ax.title)
                return True
            except ValueError:
                print("error in draw options")
    
    def locate_ips(self,datas,marker="v",color="red"):
        [self.locate_ip(data[0],data[1],marker,color) for data in datas ]
    
    def default_draw(self,**kargs):
        """
            should extend !!
        """
        self.map.fillcontinents(color="gray",lake_color="darkblue")
        self.map.drawcoastlines(color="gray",linewidth=0.25)
        self.map.drawcountries()


def init_map(args):
    print("load map data : %s "%args,end="...")
    list_args = args.split()
    args = [(list_args[i],list_args[i+1]) for i in range(0,len(list_args),2) ]
    properties = dict(args)
    m = ip_map(**properties) 
    return m

#@asyncio.coroutine
#def read(tell,filename):
#    with open(filename) as f:
#        f.seek(tell,io.SEEK_SET)
#        return f.read(),f.tell()





#@asyncio.coroutine
#def wait_input(args):
#    global locate_file_tell 
#    global old_size 
    
    #map = yield from asyncio.async(load_map(args))
#    while 1:
#           new_size = os.stat("./ips.loc").st_size
#            if (old_size == new_size):
                #yield from asyncio.sleep(1)
#                time.sleep(1)
 #               continue
#            else:
#                print(old_size)
#                content,locate_file_tell = read(locate_file_tell,"./ips.loc")
#                datas = [[float(i) for i in  each.split(",")] for each in  content.strip().split("\n")]
#                print(datas)
#                [map.locate_ip(data[0],data[1]) for data in datas]
#                old_size = new_size

                 

#@asyncio.coroutine
#def load_map(args):
#    map =  init_map(args)
#    map.map.bluemarble()
#    return map

#def process_input():
#    text = sys.stdin.readline()
#    with open("./ips.loc","a+") as  f:
#        print(text,file=f)


def para_command_line(content):
    content = content.replace(","," ")
    color = ["#FF6666"]
    ip_c = re.compile(r'((?:\d+?\.){3}\d)')  
    color_c = re.compile(r'(\#[0-9a-fA-F]{6})|([a-zA-Z]{3,20})')
    op_c = re.compile(r'[xodD\:v\<\>sp\*hH\+\|\_]{1,2}')
    ips = ip_c.findall(content)
    ops = op_c.findall(content)
    colors = color_c.findall(content)
    content = color_c.sub("",content)
    content = op_c.sub("",content)

    if colors : color = [i2 for i2 in colors[0] if i2]
    if not ops : ops = [":"]
    if ips:
        loc = loop.run_until_complete(get_loc(ips,"loc"))
        loc_l = [[float(i) for i in loc_single.split(",")] for loc_single in loc]
        print(loc_l)
    else:
        pri_content = content.strip().split()
        loc_s = [[float(pri_content[i]),float(pri_content[i+1])] for i in range(0,len(pri_content),2)  ]
        loc_l = loc_s
    return loc_l ,ops,color       #map_

def get_para():
    desc = """
        a interesting software
    """
    parser = argparse.ArgumentParser(usage="see follow ",description=desc)
    parser.add_argument("-l","--locate-ip",default=None)
    parser.add_argument("-o","--option",default=None)
    parser.add_argument("-d","--draw-map",default=True,action="store_true")

    return parser.parse_args()


def main(args):
     print(args.option)
     map = init_map(args.option) # asyncio.async(load_map(args.option))
     print("ok")
     print("draw map ... wait ...",end="")
     print("load input engine ...",end="")
     print("ok")
     map.map.bluemarble()
     return map
     #tasks = [asyncio.Task(wait_input())]
     #try:
     #    loop.run_in_executor(None ,asyncio.wait(tasks))
     #    print("ok")
     #except KeyboardInterrupt:
     #    with open("./ips.loc","w") as f: f.write("")
      #   loop.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    #loop.add_reader(sys.stdin,process_input)
    args = get_para()
    plt.ion()
    maps = None 
    if args.locate_ip :
        if args.option:
            loop.run_until_complete(get_loc([args.locate_ip],args.option) )
        else:
            print("need options args")
    elif args.draw_map :
      #  loop.add_reader()
        if args.option:  
            map = main(args)

            while 1:
                content = input(">ip | loc ")
                datas,ops,color = para_command_line(content)
                print (datas,ops,color)
                map.locate_ips(datas,marker=ops[0],color=color[0])
            #map_handler = asyncio.async( loop.run_in_executor(executor,main,args))
            #asyncio.async(wait_input(args.option))
            #asyncio.async(loop.run_in_executor(executor,wait_input,args) )
           


