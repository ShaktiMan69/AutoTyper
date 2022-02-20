#!/bin/python3

import tkinter as tk
import tkinter.scrolledtext
import tkinter.filedialog
import tkinter.messagebox
from tkinter import messagebox
import time
import multiprocessing
import sys
import pyautogui
from pynput.mouse import Listener
import csv
import ast
import queue
import ctypes

class TopGUI(tk.Toplevel):
    def __init__(self, master, title, eventType, infoText, eventName, mainList, id=None, edit=False):
        super().__init__(master, takefocus = True)
        self.title(title)
        self.output = {}
        self.grab_set()
        self.eventType = eventType
        self.mainList = mainList
        self.edit = edit
        self.id = id
        self.resizable(width=0, height=0)
        
        # Row 0
        eventNameText = tk.Label(text="Name the Event : ", master=self)
        eventNameText.grid(row=0,column=0, padx=10, pady=10)
        self.eventName =  tk.Entry(justify='center', master=self, width=40)
        self.eventName.insert(0, eventName)
        self.eventName.grid(row=0,column=1, padx=10, pady=10)

        # Row 1
        doneButton = tk.Button(text="Done", master=self, command=self.done)
        doneButton.grid(row=1,column=0, padx=10, pady=10)
        resetButton = tk.Button(text="Reset", master=self, command=self.reset)
        resetButton.grid(row=1,column=1, padx=10, pady=10)
        cancelButton = tk.Button(text="Cancel", master=self, command=self.destroy)
        cancelButton.grid(row=1,column=2, padx=25, pady=10)

        # Row 2
        info = tk.Label(self, justify='left', text=infoText, font='Helvetica 12')
        info.grid(row=2,column=1, padx=10, pady=10)
        
    def destroy(self):
        self.output = {}
        super().destroy()

    def done(self):
        if self.edit == True:
            self.mainList.reWrite(self.id, self.output)
        else:
            self.mainList.append(self.output)
        super().destroy()
        
    def onClick(self):
        self.output['name'] = self.eventName.get()
        self.output['type'] = self.eventType

    def setOutput(self, key, value):
        self.output[key] = value
    
    def getOutput(self, key):
        return self.output[key]

    def reset(self):
        self.output = {}
        
    def getData(self):
        return self.output

class ClickGUIX(TopGUI):
    def __init__(self, master, mainList, id=None, edit=False, data='',infoText='[*] Left Mouse to set a Position \n[*] Middle Mouse to Select it \n[*] Right Mouse to Reset Everthing.', eventType = 'Click', title = 'Set a Mouse Event', eventName='Mouse Event Name'):
        super().__init__(master, title, eventType, infoText, eventName, mainList, id, edit)

        if type(data) == str and data != '':
            data = ast.literal_eval(data)
        elif type(data) == dict:
            pass
        else:
            data = dict(x='', y='', button='Left')

        # Row 3
        label = tk.Label(self, text='Mouse Position : ')
        label.grid(row=3,column=0, padx=10, pady=10)
        self.position = tk.Label(self)
        self.position['text'] = f'{data["x"]} : {data["y"]}'
        self.position.grid(row=3,column=1, padx=10, pady=10)
        
        # Row 4
        label = tk.Label(self, text='Mouse Button : ')
        label.grid(row=4,column=0, padx=10, pady=10)
        types = ['Left','Middle','Right']
        self.mouseType = tk.ttk.Combobox(self, values = types, state='readonly')
        self.mouseType.set(data['button'])
        self.mouseType.grid(row=4,column=1, padx=10, pady=10)

        
        self.listener = Listener(on_click=self.onClick)
        self.listener.start()

        self.done = False
        
    def destroy(self):
        self.listener.stop()
        super().destroy()

    def done(self):
        self.listener.stop()
        super().done()
        
    def onClick(self, x, y, button, pressed):
        super().onClick()
        if button.name == 'left' and self.done == False:
            self.output['data'] = dict(x=x,y=y, button=self.mouseType.get())
            try:
                self.position['text'] = f'{x} : {y}'
            except:
                pass
            
            
        elif button.name == 'middle':
            self.done = True

        elif button.name == 'right':
            self.reset()

    def reset(self):
        super().reset()
        self.position['text'] = ''
        self.done = False
        
    def getData(self):
        return super().getData()
    

class KeyGUIX(TopGUI):
    def __init__(self, master, mainList, id=None, edit=False, data = '', infoText='[*] Select to Enter a KEY or a LINE \n[*] Keys are given to select non typable chatacters \n[*] There a lot of Keys. Some may give weird results as per the System.\n', eventType = 'Line', title = 'Set a Key | Line Event', eventName = 'Line Event Name'):
        super().__init__(master, title, eventType, infoText, eventName, mainList, id, edit)

        if type(data) == str and data != '':
            data = ast.literal_eval(data)
        elif type(data) == dict:
            pass
        else:
            data = dict(line='', key='', intervalCharacter='1', intervalWord='1')
            
        typesDict = {'Line':'0','Key':'1'}
        self.keyType = tk.IntVar()
        self.keyType.set(int(typesDict[eventType]))
        
        # Row 3
        aline = tk.Radiobutton(self, text = "Enter a Line : ", variable = self.keyType, value = 0, command=self.onClick)
        aline.grid(row=3,column=0, padx=10, pady=10)


        # Row 4
        # Interval Per Character
        paramFrame = tk.Frame(self)
        paramFrame.grid(row=4,column=1)
        intervalCharacterText = tk.Label(text="Interval Per Character (In Sec)", master=paramFrame)
        intervalCharacterText.grid(row=0,column=1, padx=10, pady=10)
        self.intervalCharacter =  tk.Entry(justify='center', master=paramFrame)
        self.intervalCharacter.insert(0, data['intervalCharacter'])
        self.intervalCharacter.grid(row=1,column=1, padx=10, pady=10)

        # Interval Per Word
        intervalWordText = tk.Label(text="Interval Per Word (In Sec)", master=paramFrame)
        intervalWordText.grid(row=0,column=0, padx=10, pady=10)
        self.intervalWord =  tk.Entry(justify='center', master=paramFrame)
        self.intervalWord.insert(0, data['intervalWord'])
        self.intervalWord.grid(row=1,column=0, padx=10, pady=10)

        # Row 5
        labelEntryText = tk.Label(self, text='Enter the Sentance/Word/Typable Key: ')
        labelEntryText.grid(row=5,column=0, padx=10, pady=10)
        self.lineEntry = tk.Entry(self, width=50, text='')
        self.lineEntry.grid(row=5,column=1, padx=10, pady=10)

        
        # Row 6
        akey = tk.Radiobutton(self, text = "Enter a Single Character : ", variable = self.keyType, value = 1, command=self.onClick)
        akey.grid(row=6,column=0, padx=10, pady=10)

        # Row 7
        label = tk.Label(self, text='Key : ')
        label.grid(row=7,column=0, padx=10, pady=10)
        types = ['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(',
                ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
                '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
                'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
                'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
                'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
                'browserback', 'browserfavorites', 'browserforward', 'browserhome',
                'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
                'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
                'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10',
                'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20',
                'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
                'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
                'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
                'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
                'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
                'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
                'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
                'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
                'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab',
                'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen',
                'command', 'option', 'optionleft', 'optionright']
        self.mouseType = tk.ttk.Combobox(self, values = types, state='readonly', width=50)
        self.mouseType.grid(row=7,column=1, padx=10, pady=10)

        if eventType == 'Line':
            self.lineEntry.insert(0, data['line'])
        else:
            self.mouseType.set(data['key'])


        self.onClick()
        
    def destroy(self):
        super().destroy()

    def done(self):
        self.onClick()
        super().done()
        
    def onClick(self):
        super().onClick()
        if self.keyType.get() == 1:
            self.lineEntry['state'] = 'disabled'
            self.mouseType['state'] = 'readonly'
            self.output['data'] = dict(key=self.mouseType.get(), intervalWord='', intervalCharacter='')
            self.output['type'] = 'Key'
            
        else:
            self.lineEntry['state'] = 'normal'
            self.mouseType['state'] = 'disabled'
            self.output['type'] = 'Line'
            self.output['data'] = dict(line=self.lineEntry.get(), intervalWord=self.intervalWord.get(), intervalCharacter=self.intervalCharacter.get())
            
            
    def reset(self):
        super().reset()
        self.mouseType.set('')
        self.lineEntry.delete(0, tk.END)
        
    def getData(self):
        return super().getData()


class TextGUIX(TopGUI):
    def __init__(self, master, mainList, id=None, edit=False, data = '', infoText='[*] Enter or Paste a block of Text \n[*] "\\n" is aslo considered as the Enter Key \n[*] Can be used to add Wordlist, Just Paste it.\n', eventType = 'Text', title = 'Set a Multi Line Event', eventName='Multi Line Event Name'):
        super().__init__(master, title, eventType, infoText, eventName, mainList, id, edit)

        if type(data) == str and data != '':
            data = ast.literal_eval(data)
        elif type(data) == dict:
            pass
        else:
            data = dict(intervalWord='1', intervalCharacter='0.07', intervalLine = '1', text='', lineFix=0)

        self.lineFix = tk.IntVar()
        # Row 3
        # Interval Per Character
        paramFrame = tk.Frame(self)
        paramFrame.grid(row=3,column=1)
        intervalCharacterText = tk.Label(text="Interval Per Character (In Sec)", master=paramFrame)
        intervalCharacterText.grid(row=0,column=1, padx=10, pady=10)
        self.intervalCharacter =  tk.Entry(justify='center', master=paramFrame)
        self.intervalCharacter.insert(0, data['intervalCharacter'])
        self.intervalCharacter.grid(row=1,column=1, padx=10, pady=10)

        # Interval Per Word
        intervalWordText = tk.Label(text="Interval Per Word (In Sec)", master=paramFrame)
        intervalWordText.grid(row=0,column=0, padx=10, pady=10)
        self.intervalWord =  tk.Entry(justify='center', master=paramFrame)
        self.intervalWord.insert(0, data['intervalWord'])
        self.intervalWord.grid(row=1,column=0, padx=10, pady=10)

        # Interval Per Line
        intervalLineText = tk.Label(text="Interval Per Line (In Sec)", master=paramFrame)
        intervalLineText.grid(row=0,column=1, padx=10, pady=10)
        self.intervalLine =  tk.Entry(justify='center', master=paramFrame)
        self.intervalLine.insert(0, data['intervalLine'])
        self.intervalLine.grid(row=1,column=1, padx=10, pady=10)

        self.lineFixButton = tk.Checkbutton(text="New Line Fix", master=paramFrame, variable=self.lineFix)
        if data['lineFix'] == 1:
            self.lineFixButton.toggle()
        self.lineFixButton.grid(row=1,column=2, padx=10, pady=10)
        
        # Row 4
        dataLabel = tk.Label(self, text="Enter Text Here", font='Helvetica 18 bold' )
        dataLabel.grid(row=4,column=1, pady=(10,2))

        # Row 5
        self.multiText = tk.scrolledtext.ScrolledText(self, undo=True)
        self.multiText.insert('1.0', data['text'])
        self.multiText.grid(row=5,column=1)
        
    def destroy(self):
        super().destroy()

    def done(self):
        self.onClick()
        super().done()
        
    def onClick(self):
        super().onClick()
        self.output['data'] = dict(text=self.multiText.get('1.0', tk.END), intervalWord=self.intervalWord.get(), intervalCharacter=self.intervalCharacter.get(), intervalLine=self.intervalLine.get(), lineFix=self.lineFix.get())

    def reset(self):
        super().reset()
        self.intervalWord.delete(0, tk.END)
        self.intervalWord.insert(0,'1')
        
        self.intervalCharacter.delete(0, tk.END)
        self.intervalCharacter.insert(0,'0.07')
        
        self.multiText.delete('1.0', tk.END)
        self.lineFixButton.deselect()
        
    def getData(self):
        return super().getData()

class DelayGUIX(TopGUI):
    def __init__(self, master, mainList, id=None, edit=False, data = '', infoText='[*] Add a delay between two Inputs/Events', eventType = 'Delay', title = 'Set a Delay between Events', eventName='Delay Event Name'):
        super().__init__(master, title, eventType, infoText, eventName, mainList, id, edit)

        if type(data) == str and data != '':
            data = ast.literal_eval(data)
        elif type(data) == dict:
            pass
        else:
            data = dict(delay='1')
            
        # Row 3
        # Interval Between Two Events
        paramFrame = tk.Frame(self)
        paramFrame.grid(row=3,column=1)
        label_interval = tk.Label(text="Interval Between Two Events (In Sec)", master=paramFrame)
        label_interval.grid(row=0,column=1, padx=10, pady=10)
        self.intervalCharacter =  tk.Entry(justify='center', master=paramFrame)
        self.intervalCharacter.insert(0, data['delay'])
        self.intervalCharacter.grid(row=1,column=1, padx=10, pady=10)

        
    def destroy(self):
        super().destroy()

    def done(self):
        self.onClick()
        super().done()
        
    def onClick(self):
        super().onClick()
        self.output['data'] = dict(delay=self.intervalCharacter.get())

    def reset(self):
        super().reset()
        self.intervalWord.delete(0, tk.END)
        self.intervalWord.insert(0,'1')
        
        self.intervalCharacter.delete(0, tk.END)
        self.intervalCharacter.insert(0,'0.07')
        
        self.multiText.delete('1.0', tk.END)
        
    def getData(self):
        return super().getData()

class DragDropListbox(tk.Listbox):
    """ A Tkinter listbox with drag'n'drop reordering of entries. """
    def __init__(self, master, **kw):
        super().__init__(master, kw)
        kw['selectmode'] = tk.SINGLE
        self.bind('<Button-1>', self.setCurrent)
        self.bind('<Double-1>', self.edit)
        self.bind('<B1-Motion>', self.shiftSelection)
        self.bind('<Button-3>', self.DeleteEvent)
        self.curIndex = None
        self.window = master

        self.eventsList = []
        self.index = 0

    def setCurrent(self, event):
        self.curIndex = self.nearest(event.y)

    def shiftSelection(self, event):
        if self.len() == 0: return
        id = self.nearest(event.y)
        x = self.getDatafromId(id)
        
        if id < self.curIndex:
            self.delete(id)
            self.insert(id+1, x)
            self.curIndex = id
        elif id > self.curIndex:
            self.delete(id)
            self.insert(id-1, x)
            self.curIndex = id
        
    def save(self, fileName):
        with open(fileName, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['name','data','type'])
            writer.writeheader()
            for event in self.eventsList:
                writer.writerow(event)

    def getIdFromName(self, name):
        return [x['name'] for x in self.eventsList].index(name)

    def getDatafromId(self, id):
        return self.eventsList[id]
    
    def edit(self, event):
        id = self.curIndex
        eventData = self.getDatafromId(id)
        print(eventData)
        if eventData['type'] == 'Click':
            self.editGUI(id, ClickGUIX, eventData)
            
        elif eventData['type'] in ['Key','Line']:
            self.editGUI(id, KeyGUIX, eventData)
            
        elif eventData['type'] == 'Text':
            self.editGUI(id, TextGUIX, eventData)
            
        elif eventData['type'] == 'Delay':
            self.editGUI(id, DelayGUIX, eventData)
            
    def append(self, data):
        print(data)
        self.index += 1
        self.insert(self.index, data)

    def load(self, fileName):
        with open(fileName, 'r') as csvfile:
            writer = csv.DictReader(csvfile)
            for event in writer:
                self.append(event)
                
    def len(self):
        return len(self.eventsList)

    def reWrite(self, id, data):
        if data == {}:
            return
        self.eventsList[id] = data
        self.delete(id)
        self.insert(id, data)

    def editGUI(self, id, gui, eventData):
        eventTop = gui(master=self.window, eventName = eventData['name'], data = eventData['data'], eventType = eventData['type'], mainList=self, id=id, edit=True)
        eventTop.wait_window()
        editedData = eventTop.getData()
        self.reWrite(id, editedData)
            
    def deleteAll(self):
        self.eventsList = []
        super().delete(0,self.size())

    def insert(self, id, data):
        super().insert(id, data['name'])
        self.eventsList.insert(id, data)
        
    def delete(self, id):
        super().delete(id)
        self.eventsList.pop(id)

    def TypeAll(self, initialDelay):
        for event in self.eventsList:
            intervalPerSentance = 0
            intervalPerWord = 0
            intervalPerChar = 0
            print(event['data'], type(event['data']))
            if event['type'] == 'Line':
                data = ast.literal_eval(event['data'])
                intervalPerWord = data['intervalWord']
                intervalPerChar = data['intervalCharacter']
            elif event['type'] == 'Text':
                data = ast.literal_eval(event['data'])
                intervalPerWord = data['intervalWord']
                intervalPerChar = data['intervalCharacter']
                intervalPerLine = data['intervalLine']
                
            start_typing(event['type'], event, int(initialDelay), int(intervalPerSentance), int(intervalPerWord), int(intervalPerChar))
        
    def loadDialog(self):
        if self.len() != 0:
            result = tk.messagebox.askyesnocancel("Overwrite", "Are You Sure? 'No' will Append", icon='warning')
            if result == True:
                self.deleteAll()
            elif result == None:
                return
        fileName = tk.filedialog.askopenfilename(title="Open the Main List from...", defaultextension=[("*.csv")], filetypes=[("CSV files", "*.csv")])
        if fileName == '':
            return

        self.load(fileName)

    def saveDialog(self):
        fileName = tk.filedialog.asksaveasfilename(title="Save the Main List to...", defaultextension=[("*.csv")], filetypes=[("CSV files", "*.csv")])
        if fileName == '':
            return
        self.save(fileName)

    def getList(self):
        return self.eventsList

    def DeleteEvent(self, event):
        id = self.nearest(event.y)
        self.delete(id)
        
class Worker(object):
    def __init__(self, queue, mainList, initialDelay, loop):
        self._is_alive = multiprocessing.Value(ctypes.c_bool, True)
        self.queue     = queue
        self.mainList = mainList
        self.loop = loop
        self.initialDelay = int(initialDelay)
        
        pyautogui.FAILSAFE = False
        
    def get_is_alive(self):
        with self._is_alive.get_lock():
            return self._is_alive.value
        
    def set_is_alive(self, value):
        with self._is_alive.get_lock():
            self._is_alive.value = value
            
    is_alive = property(get_is_alive, set_is_alive)

    def run(self):
        self.delayEvent(self.initialDelay)
        
        while True:
            for event in self.mainList:
                print(event)
                data = ast.literal_eval(str(event['data']))
                    
                eventType = event['type']
                if self._is_alive:
                    if eventType == 'Click':
                        self.clickEvent(data)

                    elif eventType == 'Key':
                        self.keyPress(data)

                    elif eventType in ['Line','Text']:
                        self.textTyping(data)

                    elif eventType == 'Delay':
                        self.delayEvent(int(data['delay']))

##            self.is_alive = False
            print(self.loop)
            
            if self.loop == False:
                return
        
    def textTyping(self, data):
        intervalPerWord = data['intervalWord']
        intervalPerChar = data['intervalCharacter']

        try:
            text = data['text']
            intervalPerLine = data['intervalLine']
        except:
            text = data['line']
            intervalPerLine = 0
            
        sentances = text.split('\n')
        for sentance in sentances:
            words = sentance.split(' ')
            for word in words:
                pyautogui.write(word, interval=intervalPerChar)
                pyautogui.write(' ')
                for i in range(0,int(intervalPerWord),1):
                    self.isAlive()
                    time.sleep(i)

            if 'lineFix' in data and data['lineFix'] == 1:
                pyautogui.press('enter')
            else:
                pyautogui.write('\n')
                
            for i in range(0,int(intervalPerLine),1):
                self.isAlive()
                time.sleep(i)

    def keyPress(self, key):
        self.isAlive()
        pyautogui.press(key['key'])

    def clickEvent(self, pos):
        self.isAlive()
        pyautogui.click(x = int(pos['x']), y = int(pos['y']), button = pos['button'])

    def delayEvent(self, sec):
        for i in range(0,sec,1):
            self.isAlive()
            time.sleep(sec)

    def isAlive(self):
        if not self.is_alive:
            sys.exit()

        
class Process(object):
    def __init__(self, queue):
        self.worker  = None
        self.process = None
        self.queue   = queue
        
    def __delete__(self):
        self.stop()

    def start(self, mainList, initialDelay, loop):
        self.stop()
        self.worker  = Worker(self.queue, mainList, initialDelay, loop)
        self.process = multiprocessing.Process(target=self.worker.run)
        self.process.start()

    def stop(self):
        if self.is_alive:
            self.worker.is_alive = False
            self.process.join()
            sys.stdout.flush()
            self.worker  = None
            self.process = None
            
    def get_is_alive(self):
        return bool(self.worker and self.process)
    is_alive = property(get_is_alive)

    
class MainApp():
    def __init__(self, title="Auto Typer | JN"):
        super().__init__()
        self.process = None
        self.queue   = multiprocessing.Queue(100)
        self.root = tk.Tk()
        self.root.title(title)
        self.root.resizable(width=0, height=0)
        self.loop = tk.IntVar()
        
        # Row 0
        frm_params = tk.Frame(self.root)
        frm_params.grid(row=0,column=0)
        
        lbl_delay = tk.Label(text="Inital Delay (In Sec) : ", master=frm_params)
        lbl_delay.grid(row=0,column=0, padx=10, pady=10)
        self.InitalDelay =  tk.Entry(justify='center', master=frm_params, width=30)
        self.InitalDelay.insert(0, "4")
        self.InitalDelay.grid(row=0,column=2, padx=10, pady=10)
        
        infiniteLoop = tk.Checkbutton(text="Infinite Loop", master=frm_params, variable=self.loop)
        infiniteLoop.grid(row=0,column=3, padx=10, pady=10)


        # Row 1
        self.status = tk.Label(self.root, text="Welcome", font='Helvetica 18 bold' )
        self.status.grid(row=1,column=0, pady=(10,2))

        # Row 2
        self.mainList = DragDropListbox(self.root, width=50, selectmode='browse', relief='raised', font='Times 14')
        self.mainList.grid(row=2,column=0, padx=10, pady=10)


        # Row 3
        listButtons = tk.Frame(self.root, highlightbackground="blue", highlightthickness=2)
        listButtons.grid(row=3,column=0)
        addEventLabel = tk.Label(listButtons, text="Controls : ")
        addEventLabel.grid(row=0,column=0, pady=(10,2))
        start = tk.Button(text="Start", master=listButtons, command=self.start)
        start.grid(row=0,column=1, padx=10, pady=10)
        start = tk.Button(text="Stop", master=listButtons, command=self.stop)
        start.grid(row=0,column=2, padx=10, pady=10)
        
        # Buttons Frame
        addEvents = tk.Frame(self.root, highlightbackground="red", highlightthickness=2)
        addEvents.grid(row=2,column=1)
        addEventLabel = tk.Label(addEvents, text="Add a Event : ")
        addEventLabel.grid(row=0,column=0, pady=(10,2))
        start = tk.Button(text="Click", master=addEvents, command=lambda:ClickGUIX(self.root, self.mainList))
        start.grid(row=1,column=0, padx=10, pady=10)
        start = tk.Button(text="Key",master=addEvents, command=lambda:KeyGUIX(self.root, self.mainList))
        start.grid(row=2,column=0, padx=10, pady=10)
        start = tk.Button(text="Text",master=addEvents, command=lambda:TextGUIX(self.root, self.mainList))
        start.grid(row=3,column=0, padx=10, pady=10)
        start = tk.Button(text="Delay",master=addEvents, command=lambda:DelayGUIX(self.root, self.mainList))
        start.grid(row=4,column=0, padx=10, pady=10)
        

        menubar = tk.Menu(frm_params)
        
        file = tk.Menu(frm_params, tearoff=False)
        file.add_command(label="Load", command=self.mainList.loadDialog)
        file.add_command(label="Save", command=self.mainList.saveDialog)
        file.add_command(label="Exit", command=self.exitApp)
        menubar.add_cascade(label='File', menu=file)
        
        events = tk.Menu(frm_params, tearoff=False)
        events.add_command(label="Click", command=lambda:ClickGUIX(self.root, self.mainList))
        events.add_command(label="Key", command=lambda:KeyGUIX(self.root, self.mainList))
        events.add_command(label="Text", command=lambda:TextGUIX(self.root, self.mainList))
        events.add_command(label="Delay", command=lambda:DelayGUIX(self.root, self.mainList))
        menubar.add_cascade(label='Add a Event', menu=events)
        
        menubar.add_command(label="About", command=self.createAboutWindow)
        

        self.root.config(menu = menubar)
        
        # End process on exit
        self.root.protocol("WM_DELETE_WINDOW", self.exitApp)

##        self.root.after_idle(self.process_queue)
        
    def __delete__(self):
        self.stop()
        self.process = None

        
    def createAboutWindow(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.resizable(width=0, height=0)
        about_window.grab_set()
        lbl_name = tk.Label(text="Auto Typer v1.1", master=about_window, font='Helvetica 15')
        lbl_name.grid(row=0, column=0, pady=(15,5), padx=10)

        lbl_developer = tk.Label(text="Jugal Naik", master=about_window, font='Helvetica 12')
        lbl_developer.grid(row=1, column=0,  pady=5, padx=10)

        text ='''
        This app gives the user the freedom. You can custom build the path which the app should follow\n
        \n
        Input Event Types Supported:\n
        Mouse - Left, Right,Middle - Click Position\n
        Keys - Up,Down,Right,Home,Start....The Entire Keyboard and may more secrete ones.\n
        Line - a single line - That's it. - There is word and character delay\n
        Text - multi-line - This can be used to add word list or line list. Basically anything. - There is word and character and Line/sentence delay\n
        Delay - This is added between the above events as per the need.\n
        And there is an initial delay before the start of the list to help you place the cursor.\n
        \n
        Events List:\n
        One can edit a event by double clicking it.\n
        Delete a Event by right clicking.\n
        Drag a event to move its position.\n
        '''
        lbl_info = tk.Label(text=text, master=about_window)
        lbl_info.grid(row=2, column=0,  pady=5, padx=10)


        about_window.mainloop()

    def exitApp(self):
        self.stop()
        self.root.destroy()

    def selectAll(self, event):
        txt_box.tag_add(tk.SEL, "1.0", tk.END)
        txt_box.mark_set(tk.INSERT, "1.0")
        txt_box.see(tk.INSERT)
        return 'break'

    def openUrl(self, url):
        webbrowser.open_new(url)

    def start(self, *args):
        if self.mainList.len() > 0:
            self.stop()
            self.status['text'] = 'Running...'
            self.process = Process(self.queue)
            self.process.start(self.mainList.getList(), self.InitalDelay.get(), bool(self.loop.get()))
            self.update()

    def stopGuiWrapper(self):
        self.status['text'] = 'Stopping...'
        self.stop()
        
    def stop(self):
        if not self.process:
            return
        self.status['text'] = 'Stopped'
        self.process.stop()

    def update(self):
        # process queue asynchronously
        # when gui is idle
        
        if self.process.is_alive == False:
            self.status['text'] = 'Stopped'
        self.root.after(1000, self.update) # 100 ms

    def mainloop(self, *args):
        return self.root.mainloop(*args)
    
if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = MainApp()
    app.mainloop()
