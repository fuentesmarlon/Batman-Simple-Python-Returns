from bmpGenerator import *
import math
from glm import *
import glm
import re
monitor=None
window={}
vertexBuffer=[]
light=[0,0,-1]
activeTexture=None
Model=[]
View=[]
Projection=[]
Viewport=[]

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
    r=int(r*255)
    g=int(g*255)
    b=int(b*255)
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
    #print("x es",xC,"a y",yC)
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
    vn=[]
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
                    #print("i",i)
                    for j in i.split('/'):
                        conv.append(int(j)-1)
                    conv2.append(conv)
                fa.append(conv2)
            if line.startswith('vn'):
                conv4=[]
                for i in line.split(' ')[1:]:
                    conv4.append(float(i))
                vn.append(conv4)

    for faces in fa:
        for face in faces:
            index=face[0]
            index2=face[1]
            index3=face[2]
            vertex = transform(v[index])
            vertexBufferArray.append(vertex)
            vertexBufferArray.append(vt[index2])
            vertexBufferArray.append(vn[index3])
    vertexBuffer = iter(vertexBufferArray)
def gltrianglewire():
    global monitor

    a = next(vertexBuffer)
    ta = next(vertexBuffer)
    na = next(vertexBuffer)
    b = next(vertexBuffer)
    tb=next(vertexBuffer)
    nb=next(vertexBuffer)
    c = next(vertexBuffer)
    tc=next(vertexBuffer)
    nc=next(vertexBuffer)
    #a= transform(a,(0,0,0),(1,1,1))
    #b=transform(b,(0,0,0),(1,1,1))
    #c=transform(c,(0,0,0),(1,1,1))
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
                r,g,tercer = shader(
                    na,nb,nc,r,g,tercer,light,val1,val2,val3
                )
                glColor(r, g, tercer)
                z=a[2]*val1+b[2]*val2+c[2]*val3
                if (0 < x < 2000 and 0 < y < 2000 and monitor.zbuffer[x][y]<z):
                    #print("x",x,y)
                    monitor.point(x,y)
                    monitor.zbuffer[x][y]=z

def shader(na,nb,nc,r,g,tercer,light,val1,val2,val3):
    print(na)
    nx = na[0] * val1 + nb[0] * val2 + nc[0] * val3
    ny = na[1] * val1 + nb[1] * val2 + nc[1] * val3
    nz = na[2] * val1 + nb[2] * val2 + nc[2] * val3
    normal = [nx,ny,nz]
    normal = normalize(normal)
    intensity=dot(normal,light)
    r = max(min(r*intensity,1),0)
    g = max(min(g*intensity,1),0)
    b = max(min(tercer*intensity,1),0)
    return r,g,b
def shaderGreen(na,nb,nc,r,g,tercer,light,val1,val2,val3):
    print(na)
    nx = na[0] * val1 + nb[0] * val2 + nc[0] * val3
    ny = na[1] * val1 + nb[1] * val2 + nc[1] * val3
    nz = na[2] * val1 + nb[2] * val2 + nc[2] * val3
    normal = [nx,ny,nz]
    normal = normalize(normal)
    intensity=dot(normal,light)
    if 0<intensity<1:
        return r*intensity,g*intensity,tercer*intensity
    else:
        return 0,0.5,0
def vectormat(mat,vec):
    newMat=[
        mat[0][0]*vec[0]+mat[0][1]*vec[1]+mat[0][2]*vec[2]+mat[0][3]*vec[3],
        mat[1][0] * vec[0] + mat[1][1] * vec[1] + mat[1][2] * vec[2] + mat[1][3] * vec[3],
        mat[2][0] * vec[0] + mat[2][1] * vec[1] + mat[2][2] * vec[2] + mat[2][3] * vec[3],
        mat[3][0] * vec[0] + mat[3][1] * vec[1] + mat[3][2] * vec[2] + mat[3][3] * vec[3]
    ]
    return newMat
"""
def transform(vertex,translate=(0,0,0),scale=(1,1,1),rotate=(0,0,0)):
    x = round((vertex[0] + translate[0]) * scale[0])
    y= round((vertex[1] + translate[1]) * scale[1])
    z=round((vertex[2] + translate[2]) * scale[2])
    Model = loadModel(translate,scale,rotate)
    ModelView=matDot(View,Model)
    ModelViewProjection = matDot(Projection,ModelView)
    ModelViewProjectionPort = matDot(Viewport,ModelViewProjection)
    #print("model",Model)
    #print("view",View)
    #print("ModelView",len(ModelView))
    #print("vertex",vertex)
    vertex.append(1)
    ertexMatrix=[
        [vertex[0],0,0,0],
        [vertex[1],1,0,0],
        [vertex[2],0,1,0],
        [1,0,0,1]
    ]
    a = vectormat(ModelViewProjectionPort,vertex)
    #print(a)
    x = a[0]/a[3]
    y=a[1]/a[3]
    z=a[2]/a[3]"""
    #print("x",x,"Y",y,"z",z)
    #return [x,y,z]

def transform(vertex):
    vertex=glm.vec3(*vertex)
    i = glm.mat4(1)
    model = glm.translate(i,glm.vec3(300,0,0))*glm.rotate(i,glm.radians(90),glm.vec3(0,1,0)) *glm.scale(i,glm.vec3(100,100,100))
    view = glm.lookAt(glm.vec3(0,500,500),glm.vec3(0,0,0),glm.vec3(0,1,0))
    proyeccion = glm.mat4(
        1,0,0,0,
        0,1,0,0,
        0,0,1,-0.00069,
        0,0,0,1)
    viewport = glm.mat4(
        1,0,0,0,
        0,1,0,0,
        0,0,1,0,
        1000,1000,1000,1)

    vertex = glm.vec4(vertex,1)
    vertex =viewport*proyeccion*view*model*vertex
    vertex = glm.vec3(
        vertex/vertex.w
    )
    return vertex


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

def matDot(A,B):
    result = [[0 for i in range(len(B[0]))] for j in range(len(A))]
    #print(result)
    for i in range(len(A)):
        for j in range(len(B[0])):
            for k in range(len(B)):
                #print(i,j,k)
                result[i][j] += A[i][k] * B [k][j]
    return result


a=[4,6]
b=[2,1]
c=[6,3]
point=[4,4]
def bayi(a,b,c,point):
    v0=[c[0]-a[0],b[0]-a[0],a[0]-point[0]]
    v1=[c[1]-a[1],b[1]-a[1],a[1]-point[1]]
    obama=cross(v0,v1)
    comp=obama[2]
    #print("barack",obama)
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

def loadModel(translate,scale, rotate):
    translationMatrix=[
     [1,0,0,translate[0]],
     [0,1,0,translate[1]],
     [0,0,1,translate[2]],
     [0,0,0,1]]
    scaleMatrix=[
    [scale[0],0,0,0],
    [0,scale[1],0,0],
    [0,0,scale[2],0],
    [0,0,0,1],
    ]
    rotationMatrixX=[
        [1,0,0,0],
        [0,math.cos(rotate[0]),-math.sin(rotate[0]),0],
        [0,math.sin(rotate[0]),math.cos(rotate[0]),0],
        [0,0,0,1]
    ]
    rotationMatrixY=[
        [math.cos(rotate[1]),0,math.sin(rotate[1]),0],
        [0,1,0,0],
        [-math.sin(rotate[1]),0,math.cos(rotate[1]),0],
        [0,0,0,1]
    ]
    rotationMatrixZ=[
        [math.cos(rotate[2]),-math.sin(rotate[2]),0,0],
        [math.sin(rotate[2]),math.cos(rotate[2]),0,0],
        [0,0,1,0],
        [0,0,0,1]
    ]
    rotationPre = matDot(rotationMatrixX,rotationMatrixY)
    rotationMatrix = matDot(rotationPre,rotationMatrixZ)
    preModel=matDot(translationMatrix,scaleMatrix)
    Model = matDot(preModel,rotationMatrix)
    return Model

def loadViewMatrix(x,y,z,center):
    Mr=[
        [x[0],x[1],x[2],0],
        [y[0],y[1],y[2],0],
        [z[0],z[1],z[2],0],
        [0,0,0,1]
    ]
    Mt=[
        [1,0,0,-center[0]],
        [0,1,0,-center[1]],
        [0,0,1,-center[2]],
        [0,0,0,1]
    ]
    print("mt",Mt)
    Mview=matDot(Mr,Mt)
    print(Mview)
    return Mview

def lookAt(eye,center,up):
    global View, Projection, Viewport
    delta1 = sub(eye,center)
    z = normalize(delta1)
    cross1 = cross(up,z)
    x=normalize(cross1)
    cross2=cross(up,x)
    y=normalize(cross2)
    View = loadViewMatrix(x,y,z,center)
    print(View)
    #res = -1/magnitude(delta1)
    res=-0.0000017
    Projection=loadProjection(res)
    Viewport=loadViewport()

def loadProjection(res):

    projection = glm.mat4(
        1,0,0,0,
        0,1,0,0,
        0,0,1,0,
        0,0,res,1
    )
    return projection
def loadViewport():
    global monitor
    Sx=window['x']
    Sy=window['y']
    height=window['height']
    width=window['width']
    wHalf=width/2
    hHalf=height/2

    viewPort=glm.mat4(
        wHalf,0,0,Sx+wHalf,
        0,hHalf,0,Sy+hHalf,
        0,0,128,128,
        0,0,0,1
    )
    return viewPort



texture='texture.bmp'
glInit()
glCreateWindow(2000,2000,texture=texture)
glViewPort(0,0,2000,2000)
glClearColor(0,0,0)
glColor(1,1,1)
glClear()

#lookAt()
gload(file='batman2.obj')
gldraw(tipo='wireframe')
name="linea.bmp"
glFinish(name)

