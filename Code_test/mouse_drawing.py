import tkinter

window = 0
canvas = 0

xList = []
yList = []

color = 'black'

def onClick(event):
    global xList, yList
    xList.append(event.x)
    yList.append(event.y)

def onMove(event):
    global xList, yList
    canvas.create_line(xList[-1], yList[-1], event.x, event.y, fill=color, width=3)
    xList.append(event.x)
    yList.append(event.y)

def initWindow():
    global window, canvas
    window = tkinter.Tk()
    window.title('Draw')
    canvas = tkinter.Canvas(window, width=800, height=600, bg='white')
    canvas.pack()
    canvas.bind('<Button-1>', onClick)
    canvas.bind('<B1-Motion>', onMove)
    window.mainloop()

# def listPoints():
#     for ()

initWindow()