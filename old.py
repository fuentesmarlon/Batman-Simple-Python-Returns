from bmpGenerator import *
import math
import re
monitor=None
window={}
vertexBuffer=[]
light=[0,0,-1]
activeTexture=None
#Starts any object, doesn't do anything at the moment
def glInit():
    pass
#Initializes the framebuffer of the size that it was set, creates a Bitmap with the dimensions given.
def glCreateWindow(width,height,texture):
    global monitor,activeTexture
    monitor=Bitmap(width,height)
    activeTexture=Texture(texture)
#Area available where it's going to draw
def glViewPort(x,y,width,height):
    window['x']= x
    window['y']= y
    window['width']=int(width)
    window['height']=int(height)
#creates a map of bits made of the same color
def glClear():
    monitor.clear()
#chooses the color which is going to be use by glClear. All parameters are nombers between 0 to 1
def glClearColor(r,g,b):
    global monitor
    r=round(r*255)
    g=round(g*255)
    b=round(b*255)
    monitor.clearColor = color(r,g,b)
#Creates a pixel where it's position is defined
def glVertex(x,y):
    global monitor
    xND=window['x']
    yND=window['y']
    height=window['height']
    width=window['width']
    xC = round((x + 1)*(width*0.5)+xND)
    yC = round((y +1)*(height*0.5)+yND)
    print("x es",xC,"a y",yC)
    monitor.point(xC,yC)
def glColor(r,g,b):
    global monitor
    r=int(round(r*255))
    g=int(round(g*255))
    b=int(round(b*255))
    monitor.vertexColor = color(r,g,b)

def glFinish(name):
    monitor.write(str(name))

def magnitude(v):
    return math.sqrt(sum(v[i]*v[i] for i in range(len(v))))

def normalize(v):
    vmag = magnitude(v)
    if vmag==0:
        return [0 for i in range(len(v))]
    else:
        return [ v[i]/vmag  for i in range(len(v)) ]

#draws a line in the coordinates given to it.
def glLine(x0,y0,x1,y1):
    global monitor
    xND=window['x']
    yND=window['y']
    height=window['height']
    width=window['width']
    xi = round((x0 + 1)*(width*0.5)+xND)
    xf = round((x1 + 1)*(width*0.5)+xND)
    yi = round((y0+ 1)*(height*0.5)+yND)
    yf = round((y1+ 1)*(height*0.5)+yND)
    dy=abs(yf-yi)
    dx=abs(xf-xi)
    steep =dy>dx
    if steep:
        xi,yi=yi,xi
        xf,yf=yf,xf
    if(xi>xf):
        xi,xf = xf,xi
        yi,yf=yf,yi


    dy =abs( yf - yi)
    dx = abs(xf - xi)

    offset = 0
    threshold = dx
    y = yi
    inc = 1 if yf > yi else -1
    for x in range(xi,xf+1):
        if steep:
            monitor.point(y,x)
        else:
            monitor.point(x,y)

        offset += dy *2
        if offset >=threshold:
            y +=inc
            threshold += 2*dx


def gload(file):
    global vertexBuffer
    v=[]
    fa=[]
    vt=[]
    vertexBufferArray=[]
    with open(file) as f:
        for line in f:
            if line.startswith('v'):
                conv = []
                for i in line.split(' ')[1:]:
                    conv.append(float(i))
                v.append(conv)
            if line.startswith('vt'):
                conv3=[]
                for i in line.split(' ')[1:]:
                    conv3.append(float(i))
                vt.append(conv3)
            if line.startswith('f'):
                conv2=[]
                for i in line.split(' ')[1:]:
                    conv = []
                    for j in i.split('/'):
                        conv.append(int(j)-1)
                    conv2.append(conv)
                fa.append(conv2)
    for faces in fa:
        for face in faces:
            index=face[0]
            index2=face[1]
            vertexBufferArray.append(v[index])
            vertexBufferArray.append(vt[index2])
    vertexBuffer = iter(vertexBufferArray)
def gltrianglewire():
    global monitor
    a = next(vertexBuffer)
    ta = next(vertexBuffer)
    b = next(vertexBuffer)
    tb=next(vertexBuffer)
    c = next(vertexBuffer)
    tc=next(vertexBuffer)
    a= transform(a,(10,5,0),(100,100,100))
    b=transform(b,(10,5,0),(100,100,100))
    c=transform(c,(10,5,0),(100,100,100))
    xlist=[int(a[0]),int(b[0]),int(c[0])]
    ylist=[int(a[1]),int(b[1]),int(c[1])]
    xlist.sort()
    ylist.sort()
    xMin = xlist[0]
    yMin = ylist[0]
    xMax = xlist[-1]+1
    yMax = ylist[-1]+1
    n1=sub(c,a)
    n2=sub(b,a)
    normal=cross(n1,n2)
    normal = normalize(normal)
    intensity=dot(normal,light)
    if intensity<0:
        return

    for x in range(xMin,xMax):
        for y in range(yMin,yMax):
            p=(x,y)
            val1,val2,val3=bayi(a,b,c,p)
            if val1<0 or val2<0 or val3<0:
                pass
            else:
                tx=ta[0]*val1+tb[0]*val2+tc[0]*val3
                ty=ta[1]*val1+tb[1]*val2+tc[1]*val3
                r,g,tercer=activeTexture.getColor(tx,ty)
                r = min(1, r * intensity)
                g = min(1, g * intensity)
                tercer = min(1, tercer * intensity)
                glColor(r, g, tercer)
                z=a[2]*val1+b[2]*val2+c[2]*val3
                if (monitor.zbuffer[x][y]<z):
                    monitor.point(x,y)
                    monitor.zbuffer[x][y]=z


def transform(vertex,translate=(0,0,0),scale=(1,1,1)):
    x = round((vertex[0] + translate[0]) * scale[0])
    y= round((vertex[1] + translate[1]) * scale[1])
    z=round((vertex[2] + translate[2]) * scale[2])
    return [x,y,z]
def gldraw(tipo):
    if tipo =='wireframe':
        try:
            while True:
                gltrianglewire()
        except StopIteration:
            print("done")


#SR4, suma entre vectores

def cross(v0,v1):
    v3 = [v0[1]*v1[2]-v0[2]*v1[1],v0[2]*v1[0]-v0[0]*v1[2],v0[0]*v1[1]-v0[1]*v1[0]]
    return v3
def dot(v0,v1):
    esc=v0[0]*v1[0]+v0[1]*v1[1]+v0[2]*v1[2]
    return esc
a=[4,6]
b=[2,1]
c=[6,3]
point=[4,4]
def bayi(a,b,c,point):
    v0=[c[0]-a[0],b[0]-a[0],a[0]-point[0]]
    v1=[c[1]-a[1],b[1]-a[1],a[1]-point[1]]
    obama=cross(v0,v1)
    comp=obama[2]
    print("barack",obama)
    if abs(comp)<1:
        return -1,-1,-1
    val1=1-(obama[0]+obama[1])/obama[2]
    val2=obama[1]/obama[2]
    val3=obama[0]/obama[2]
    return val1,val2,val3

def sub(vec1, vec2):
       if len(vec1) != len(vec2):
           raise ValueError
       return [a1 - b1 for a1, b1 in zip(vec1, vec2)]


texture='texture.bmp'
glInit()
glCreateWindow(2000,2000,texture=texture)
glViewPort(0,0,2000,2000)
glClearColor(0,0,0)
glColor(1,1,1)
glClear()

gload(file='batman2.obj')
gldraw(tipo='wireframe')
name="medium_shot.bmp"
glFinish(name)

