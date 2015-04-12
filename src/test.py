import asyncio
import io
import os
import matplotlib.pylab as plt
from map import ip_map

@asyncio.coroutine
def read(tell,filename):
    with open(filename) as f:
        f.seek(tell,io.SEEK_SET)
        return f.read(),f.tell()


@asyncio.coroutine
def wait_input(map_handler,loop):
    locate_file_tell = 0
    old_size = os.stat("./ips.loc").st_size

    while 1:
        new_size = os.stat("./ips.loc").st_size
        if (old_size == new_size):
            yield from asyncio.sleep(1)
            continue
        else:
            print(old_size)
            content,locate_file_tell = yield from  read(locate_file_tell,"./ips.loc")
            datas = [ [float(i) for i in each.split(",")]  for each in  content.strip().split("\n")]
            print(datas)
            [map_handler.locate_ip(data[0],data[1]) for data in datas]
            old_size = new_size


        







#try:
#    loop = asyncio.get_event_loop()
#    loop.run_until_complete(wait_input())
# 
##except KeyboardInterrupt :
 #   with open("./ips.loc","w") as f:
 #       f.write("")
if __name__ == "__main__":
    print("ok")
    m = ip_map()
    m.map.bluemarble()

    input()
    plt.ion()
    try:
       loop = asyncio.get_event_loop()
       loop.run_until_complete(asyncio.async(wait_input(m,loop)))

    except KeyboardInterrupt:
         with open("./ips.loc","w") as f:  f.write("")
