import struct

def char(c):
    return struct.pack("=c",c.encode('ascii'))
def word(w):
    return struct.pack("=h",w)
def dword(d):
    return struct.pack("=l",d)
def color(r,g,b):
    return bytes([b,g,r])


class Bitmap(object):
    def __init__(self,width,height):
        self.width = width
        self.height=height
        self.pixels=[]
        self.zbuffer=[]
        self.clearColor = color(0,0,0)
        self.vertexColor = color(0,0,0)
        self.clear()

    def clear(self):
        self.pixels=[
            [self.clearColor for x in range(self.width)]
            for y in range (self.height)
        ]
        self.zbuffer = [
            [-9999999 for x in range(self.width)]
            for y in range(self.height)
        ]
    def write(self,filename):
        f = open(filename,'bw')

        #file header (14)
        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(14 + 40))

        #image header (40)
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))

        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))

        # pixel data
        for x in range(self.height):
            for y in range(self.width):
                f.write(self.pixels[x][y])
        f.close()

    def point(self,x,y):

        if(x>=100):
            x=x-1
        if(y>=100):
            y=y-1
        try:
            self.pixels[y][x]= self.vertexColor
        except:
            pass


class Texture(object):
    def __init__(self,archivo):
        self.archivo=archivo
        self.read()

    def read(self):
        image = open(self.archivo, "rb")
        # we ignore all the header stuff
        image.seek(2 + 4 + 4)  # skip BM, skip bmp size, skip zeros
        header_size = struct.unpack("=l", image.read(4))[0]  # read header size
        image.seek(2 + 4 + 4 + 4 + 4)

        self.width = struct.unpack("=l", image.read(4))[0]  # read width
        self.height = struct.unpack("=l", image.read(4))[0]  # read width
        self.pixels = []
        image.seek(header_size)
        for y in range(self.height):
            self.pixels.append([])
            for x in range(self.width):
                b = ord(image.read(1))
                g = ord(image.read(1))
                r = ord(image.read(1))
                self.pixels[y].append((r/255, g/255, b/255))

        image.close()


    def getColor(self,tx,ty):
        newX = round(tx*self.width)
        newY = round(ty*self.height)
        r,g,b=self.pixels[newX][newY]
        return r,g,b
