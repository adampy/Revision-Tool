from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import colorchooser
from tkinter import filedialog
import tkinter.font as tkfont
import csv
import random
import os
import sqlite3

#allows the use of toplevel windows - dont close program when window is closed unlike Tk() window
root = Tk()
root.withdraw()

###----------------------------------------------------------Variables----------------------------------------------------###

#all fonts supported in tkinter from tk.font.fontfamilies()
supported = list(tkfont.families())

supportedSizes = ['640x480', '700x350', '800x450',
                  '800x600', '800x600', '960x720',
                  '1024x576', '1024x768', '1152x648',
                  '1280x720', '1280x720', '1280x800',
                  '1280x960', '1366x768', '1400x1050',
                  '1440x1080', '1440x900', '1600x900',
                  '1680x1050', '1920x1080', '1920x1080']

supported.sort()

globalfont = None #set to None so there isnt an error when selecting the default font if the optionFile doesn't exist
fontRatio = 1 #default value

#--Editable Variables--
dataFile = 'database.db'

#these are default if not found in the optionFile
mainguiSize = '700x350'
mainguiBackground = 'SystemButtonFace'
notifyWhenCorrect = 'False'

#fonts need to be lists so they can be edited
bfont35 = ['Calibri', '35', 'bold']
font24 = ['Calibri', '24']
font20 = ['Calibri', '20']
font12 = ['Calibri', '12']
font12Underlined = ['Calibri', '12', 'underline']

#getting icon path
icon = os.path.dirname(os.path.realpath(__file__)) + '\icon.ico'

#images
tick = 'tick.png'
tickGIF = 'tick2.gif'

#---------------------------------------------------------------Classes------------------------------------------------------

def Questions(event=None):
    '''Gives a matrix of questions in seperate lists
    with the category name as the index 0'''

    c.execute('SELECT subject, answer, question, rowid FROM questions')
    questionList = [list(x) for x in c.fetchall()]

    c.execute('SELECT DISTINCT subject FROM questions')
    category = [x[0] for x in c.fetchall()]

    return [questionList, category] #can use return instead of a global :)


class Welcome:
    def __init__(self, maintext, image=True):
        '''Class used for changing categories as well as the first welcome page'''

        self.maintext = maintext


        #only save images if they are all in the directory
        if useImages:
            try:
                self.tick = PhotoImage(file=tick)
            except:
                self.tick = PhotoImage(file=tickGIF)

        self.window = Toplevel()
        self.window.title(maintext)
        #self.window.geometry('450x500')
        self.window.protocol("WM_DELETE_WINDOW", self.quitprogram)

        if useIcon:
            self.window.iconbitmap(icon)

        Label(self.window, text=self.maintext, font=bfont35).pack()

        if self.maintext == 'Welcome':
            Label(self.window, text='Made by Adam', font=font24).pack()


        if CheckFile(dataFile) and image:
            self.frame1 = Frame(self.window)

            Label(self.frame1, text='Question File - ', font=font20).pack(side=LEFT)
            Label(self.frame1, image=self.tick).pack(side=LEFT)

            self.frame1.pack(pady=50)

        self.frame2 = Frame(self.window)
        Label(self.frame2, text='Category - ', font=font20).pack(side=LEFT)
        category.sort()
        self.combo = ttk.Combobox(self.frame2, font=font20, values=category, state='readonly')
        self.combo.pack(side=LEFT)
        self.frame2.pack(padx=10)

        #changing the button commands to destroy the last question window if self.maintext of the Welcome page is 'Change Category'
        if maintext == 'Change Category':
            button = Button(self.window, text='START', font=bfont35, width=15, fg='white', bg='green', command=lambda: self.controller(self.combo.get(), destroymain=True))
            #self.window.geometry('450x250')
        elif maintext == 'Welcome' and not image: #has to be when there isnt any images
            #self.window.geometry('450x250')
            button = Button(self.window, text='START', font=bfont35, width=15, fg='white', bg='green', command=lambda: self.controller(self.combo.get()))
        else:
            button = Button(self.window, text='START', font=bfont35, width=15, fg='white', bg='green', command=lambda: self.controller(self.combo.get()))
        button.pack(pady=10)


        if not questionList:
            self.window.destroy()
            createquestions = NoQuestions()
            return

    def controller(self, start, destroymain=False):
        '''Checks the category and makes sure that questions are in questionList
            Can destory the last window if passed destroymain=True'''
        global main #has to be global to be used in other classes

        if questionList and start in category: #checking that there are questions and the category given is valid
            if destroymain:
                main.window.destroy()

            self.window.destroy()
            main = MainGUI(start)

        elif start not in category:
            messagebox.showinfo(message='Please select a category')

    def quitprogram(self, event=None):
        '''Closes the window before ending the application'''
        self.window.destroy()
        sys.exit()


class MainGUI:
    def __init__(self, startcategory):
        ''' self.questions = list of questions
            self.categories = list of catagories
            self.category = the catagory chosen
            self.window = the toplevel window
            self.string = string var - question on screen
            self.question = question on screen
            self.answer = answer to question on screen
            self.questionrow = row of the question'''

        self.questions = questionList
        self.categories = category
        self.category = startcategory

        if self.category == None:
            return

        self.window = Toplevel(bg=mainguiBackground)
        self.window.geometry(mainguiSize)
        self.window.title(self.category)
        self.window.protocol("WM_DELETE_WINDOW", self.quitprogram)

        if useIcon:
            self.window.iconbitmap(icon)

        #finding the colour
        c.execute('SELECT colour FROM subjects WHERE subject = (?)',(self.category,))
        self.colour = c.fetchone()[0]

        self.string = StringVar()

        self.titleLabel = Label(self.window, text=self.category, font=bfont35, fg=self.colour, bg=mainguiBackground)
        self.questionLabel = Label(self.window, textvariable=self.string, font=font24, fg=self.colour, wraplength=700, bg=mainguiBackground)

        self.titleLabel.pack()
        self.questionLabel.pack()

        self.question = ''
        self.answer = ''
        self.rowid = 0
        self.randomquestion()

        self.frame1 = Frame(self.window, bg=mainguiBackground)
        self.entry = Entry(self.frame1, font=font24, width=30) #focusin & focusout binding
        self.entry.bind('<FocusIn>', lambda event: FocusIn(self.entry, 'Answer... Egypt'))
        self.entry.bind('<FocusOut>', lambda event: FocusOut(self.entry, 'Answer... Egypt'))
        self.entry.insert(0,'Answer... Egypt')
        self.entry['fg'] = 'grey'
        self.entry.focus_set()
        self.entry.bind('<Return>',self.checkanswer)
        self.entry.pack()

        self.newbutton = Button(self.frame1, font=font20, fg='white', bg=self.colour, text='Change Question', command=self.randomquestion)
        self.newbutton.pack(side=LEFT, pady=10)

        self.checkbutton = Button(self.frame1, font=font20, fg='white', bg=self.colour, text='Check Answer!', width=20, command=self.checkanswer)
        self.checkbutton.pack(side=RIGHT, pady=10)

        self.frame1.pack(side=BOTTOM, pady=10)

        #making the menubar
        self.menubar = Menu(self.window)
        #file menu
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='Different Question', command=self.randomquestion)
        self.filemenu.add_command(label='Different Category', command=self.changecategory)
        self.filemenu.add_separator()
        self.filemenu.add_command(label='Quit', command=self.quitprogram)
        self.menubar.add_cascade(label='File', menu=self.filemenu)
        #edit menu
        self.editmenu = Menu(self.menubar, tearoff=0)
        self.editmenu.add_command(label='Edit Question', command=self.editquestion)
        self.editmenu.add_command(label='Edit Category', command=self.editcategory)
        self.menubar.add_cascade(label='Edit', menu=self.editmenu)
        #new menu
        self.newmenu = Menu(self.menubar, tearoff=0)
        self.newmenu.add_command(label='New Question', command=self.newquestion, accelerator='Ctrl+N')
        root.bind_all('<Control-N>', self.newquestion)
        root.bind_all('<Control-n>', self.newquestion)
        self.newmenu.add_command(label='New Category', command=self.newcategory)
        self.menubar.add_cascade(label='New', menu=self.newmenu)
        #delete menu
        self.deletemenu = Menu(self.menubar, tearoff=0)
        self.deletemenu.add_command(label='Delete Question', command=self.deletequestion)
        self.deletemenu.add_command(label='Delete Category', command=self.deletecategory)
        self.menubar.add_cascade(label='Delete', menu=self.deletemenu)
        #configure menu
        self.configuremenu = Menu(self.menubar, tearoff=0)
        self.configuremenu.add_command(label='MainGUI Background Colour', command=self.changebackground)
        self.configuremenu.add_command(label='MainGUI Size', command=self.changesize)
        self.configuremenu.add_command(label='Font', command=self.changefont)
        self.configuremenu.add_command(label='Notify When Correct', command=self.notify)
        self.menubar.add_cascade(label='Configure', menu=self.configuremenu)
        #help menu
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label='Answer', command=self.showanswer, accelerator='Ctrl+A')
        root.bind_all('<Control-A>', self.showanswer)
        root.bind_all('<Control-a>', self.showanswer)
        self.helpmenu.add_command(label='Tutorial', command=self.tutorial)
        self.helpmenu.add_command(label='Search Questions', command=self.searchquestions)
        self.helpmenu.add_command(label='Refresh Questions', command=lambda: self.refreshlist(notify=True))
        self.menubar.add_cascade(label='Help', menu=self.helpmenu)

        self.window.config(menu=self.menubar)

    def quitprogram(self, event=None):
        '''Closes the window before ending the application'''
        self.window.destroy()
        sys.exit()

    def checkanswer(self, event=None):
        '''Checks the answer against the current question'''
        if self.entry.get().lower() == self.answer.lower():
            if notifyWhenCorrect == 'True':
                messagebox.showinfo(message='Correct!')
            self.entry.delete(0,END)
            self.randomquestion(self)

    def randomquestion(self, event=None, bruteforce=False):
        '''Changes self.string into a different question from the category passed'''

        #forcing any question in the category to be set
        if bruteforce:
            for item in questionList:
                if item != self.questionrow and item[0] == self.category:
                    self.question = item[2]
                    self.answer = item[1]
                    self.questionrow = item
                    self.rowid = item[3]
                    self.string.set(self.question)
                    return

        #counter measure making sure not infinitely looping
        count = 0
        for question in questionList:
            if question[0] == self.category:
                count += 1
        if count <= 1 and self.question != '':
            return

        while True:
            choice = random.choice(questionList)
            if choice[0] == self.category and choice[2] != self.question: #makes sure not repeated after eachother
                self.question = choice[2]
                self.answer = choice[1]
                self.questionrow = choice
                self.rowid = choice[3]
                self.string.set(self.question)
                break

    def changecategory(self, event=None):
        '''Changes the category'''
        welcome = Welcome('Change Category', image=False)

    def editquestion(self, event=None):
        '''Edit question window controller'''
        edit = NewOrEditQuestion(self, edit=True)

    def newquestion(self, event=None):
        '''Create new question window controller'''
        new = NewOrEditQuestion(self, new=True)

    def refreshlist(self, event=None, notify=False):
        '''Refreshes the questions and resets the class variables'''
        GetQuestions()
        self.questions = questionList
        self.categories = category

        if notify:
            messagebox.showinfo(message='The questions have been refreshed!')

    def newcategory(self, event=None):
        '''Create new category window controller'''
        ncat = NewOrEditQuestion(self, new=True, category=True)

    def editcategory(self, event=None):
        '''Edit category window controller'''
        editcat = EditCategory(self)

    def deletequestion(self, event=None):
        '''Deletes the question that is currently selected'''
        message = messagebox.askyesno(message='Are you sure you want to delete this question?')
        if not message:
            return

        c.execute('DELETE FROM questions WHERE rowid = (?)', (self.rowid,))
        conn.commit()

        messagebox.showinfo(message='Question deleted successfully!')

        self.refreshlist()

        if self.category not in category:
            messagebox.showinfo(message='There are no questions in this current category')

            c.execute('DELETE FROM subjects WHERE subject = (?)', (self.category,))
            conn.commit()

            self.window.destroy()
            self.changecategory()
            return
        else:
            self.randomquestion(bruteforce=True)


    def deletecategory(self, event=None):
        '''Deletes the category that is currently selected'''
        message = messagebox.askyesno(message='Are you sure you want to delete the category')
        if not message:
            return

        c.execute('DELETE FROM questions WHERE subject = (?)', (self.category,))
        c.execute('DELETE FROM subjects WHERE subject = (?)', (self.category,))
        conn.commit()

        messagebox.showinfo(message='Category deleted successfully! Choose another category!')

        self.refreshlist()

        self.window.destroy()
        self.changecategory()


    def changefont(self, event=None):
        '''Changing font controller'''
        editfont = EditFont()

    def showanswer(self, event=None):
        '''Is the controller for when the user chooses to show the current answer'''
        line = 'The answer is: ' + self.answer
        messagebox.showinfo('Cheating now are we?',line)
        self.entry.delete(0,END)
        self.entry['fg'] = 'black'
        self.entry.insert(0,self.answer)

    def tutorial(self, event=None):
        '''Tutorial that shows the user how to control thr program'''
        messagebox.showerror(message='Currently still in development :(')

    def changesize(self, event=None):
        '''Changesize controller'''
        editsize = MainGUISize()

    def changebackground(self, event=None):
        '''Controller that creates an instance of MainGUIBackground class'''
        changebackground = MainGUIBackground()

    def searchquestions(self, event=None):
        '''Controller that creates an instance of SearchQuestions class'''
        searcher = SearchQuestions(self)

    def override(self, question, event=None):
        '''Overrides the current question - used in SearchQuestions class'''
        self.category = question[0]
        self.answer = question[1]
        self.question = question[2]
        self.questionrow = question
        self.string.set(question[2])

        c.execute('SELECT colour FROM subjects WHERE subject = (?)', (question[0],))
        self.colour = c.fetchone()[0]
        self.rowid = question[3]

        self.titleLabel['fg'] = self.colour
        self.titleLabel['text'] = self.category

        self.questionLabel['fg'] = self.colour
        self.newbutton['bg'] = self.colour
        self.checkbutton['bg'] = self.colour

        self.window.title(self.category)

    def notify(self, event=None):
        '''Creates instance of NotifyCorrect class'''
        notifywindow = NotifyCorrect()

class NewOrEditQuestion:
    def __init__(self, main, edit=False, new=False, category=False):
        '''main parameter is the main window in order to get the variables such as .answer'''

        self.window = Toplevel()
        #self.window.geometry('580x380')
        #self.window.resizable(0,0)

        if useIcon:
            self.window.iconbitmap(icon)

        self.colour = 'red'

        ##---TITLE AND LABEL---
        if edit == True:
            self.window.title('Edit')
            Label(self.window, text='Edit Question', font=bfont35, fg=main.colour).pack(padx=10)
        elif new == True and category == False:
            self.window.title('New')
            Label(self.window, text='New Question', font=bfont35, fg=main.colour).pack(padx=10)
        elif category == True:
            self.window.title('Category')
            Label(self.window, text='New Question for Category', font=bfont35).pack(padx=10)

        #-----------------------------------------


        ##---DROPDOWN OR ENTRY---
        self.frame1 = Frame(self.window)
        if category == True: #changing dropdown into entry if category
            Label(self.frame1, text='Category name', font=font20).pack(side=LEFT, padx=10)

            self.categoryentry = Entry(self.frame1, font=font20)
            self.categoryentry.bind('<FocusIn>', lambda event: FocusIn(self.categoryentry, 'Category... Animals'))
            self.categoryentry.bind('<FocusOut>', lambda event: FocusOut(self.categoryentry, 'Category... Animals'))
            self.categoryentry.insert(0,'Category... Animals')
            self.categoryentry['fg'] = 'grey'

            self.categoryentry.pack(side=LEFT, padx=10)
        else:
            Label(self.frame1, text='Choose a category', font=font20, fg=main.colour).pack(side=LEFT, padx=10)
            self.dropdown = ttk.Combobox(self.frame1, font=font20, values=main.categories, state='disabled')
            self.dropdown.pack(side=LEFT, padx=10)

        if edit == True or (new == True and category == False):
            self.dropdown.current(main.categories.index(main.category)) #finding the index of the current category

        self.frame1.pack()

        self.scrolledtext = ScrolledText(self.window, font=font20, width=35, height=5, wrap=WORD)
        self.scrolledtext.bind('<FocusIn>', lambda event: ScrolledFocusIn(self.scrolledtext))
        self.scrolledtext.bind('<FocusOut>', lambda event: ScrolledFocusOut(self.scrolledtext))
        self.scrolledtext.focus_set()
        self.scrolledtext.pack(pady=10)

        def focus_next_window(event):
            event.widget.tk_focusNext().focus()
            return 'break'

        self.scrolledtext.bind("<Tab>", focus_next_window)

        self.frame2 = Frame(self.window)
        self.ansentry = Entry(self.frame2, font=font20, width=30)
        self.ansentry.bind('<FocusIn>', lambda event: FocusIn(self.ansentry, 'Answer... Egypt'))
        self.ansentry.bind('<FocusOut>', lambda event: FocusOut(self.ansentry, 'Answer... Egypt'))
        self.ansentry.pack(side=LEFT)

        ##---ADDING COLOUR BUTTON---
        if category == True:
            self.b = Button(self.window, text='Click to change category colour', bg='deep sky blue', fg='white', font=font20, command=self.getcolour).pack(pady=5, padx=5)
            #self.window.geometry('550x450')
            self.button = Button(self.frame2, text='Create', bg='deep sky blue', fg='white' ,font=font20, command=self.newcategory)

        if edit == True: #edit question
            self.button = Button(self.frame2, text='Save', bg=main.colour, fg='white', font=font20, command=self.editquestion)
            self.scrolledtext.insert(END,main.question)
            self.ansentry.insert(0,main.answer)
            self.ansentry.bind('<Return>', self.editquestion)

        elif new == True and category == False: #new question
            self.button = Button(self.frame2, text='Create', bg=main.colour, fg='white', font=font20, command=self.newquestion)
            self.scrolledtext.insert(0.0, 'Question... Where do cats originate from?')
            self.ansentry.insert(0, 'Answer... Egypt')

            self.scrolledtext['fg'] = 'grey'
            self.ansentry['fg'] = 'grey'
            self.ansentry.bind('<Return>', self.newquestion)

        self.button.pack(side=LEFT, padx=10)
        self.frame2.pack(pady=10, padx=10)

        if new and category: #window size was too small so added this to compensate as well as text not inserting
            #self.window.geometry('600x450')
            self.scrolledtext.insert(0.0, 'Question... Where do cats originate from?')
            self.ansentry.insert(0, 'Answer... Egypt')

            self.scrolledtext['fg'] = 'grey'
            self.ansentry['fg'] = 'grey'


    def getcolour(self, event=None):
        '''Gets the colour that the user enters when making a category'''
        self.colour = colorchooser.askcolor()[1]


    def editquestion(self, event=None):
        '''Edits the question using a temporary file'''
        global questionList

        category = self.dropdown.get()
        question = self.scrolledtext.get(0.0,'end-1c')
        answer = self.ansentry.get()
        colour = main.colour
        itemindex = 0

        if category == main.category and question == main.question and answer == main.answer: #no changes made
            messagebox.showinfo(message='You have made no changes!')
            return

        if answer == '' or question == '' or category == '' or answer == 'Answer... Egypt' or question == 'Question... Where do cats originate from?' or category == 'Category Name':
            messagebox.showinfo(message='Make sure all entries aren\'t empty or have the default text inside them')
            return

        elif category in main.categories: #valid category
            c.execute('UPDATE questions SET question = (?), answer = (?) WHERE rowid = (?)', (question, answer, main.rowid))
            conn.commit()

        main.refreshlist()
        main.randomquestion()
        self.window.destroy()

    def newquestion(self, event=None):
        '''Adds a new question to the dataFile'''
        category = self.dropdown.get()
        question = self.scrolledtext.get(0.0,'end-1c')
        answer = self.ansentry.get()

        if answer == '' or question == '' or category == '' or answer == 'Answer... Egypt' or question == 'Question... Where do cats originate from?' or category == 'Category Name':
            messagebox.showinfo(message='Make sure all entries aren\'t empty or have the default text inside them')
            return

        c.execute('INSERT INTO questions VALUES (?,?,?)', (category, answer, question))
        conn.commit()
        messagebox.showinfo(message='New Question created!')

        self.window.destroy()
        main.refreshlist()


    def newcategory(self, event=None):
        '''Creates a question for a new category'''

        funccategory = self.categoryentry.get()
        question = self.scrolledtext.get(0.0,'end-1c')
        answer = self.ansentry.get()
        colour = self.colour

        if answer == '' or question == '' or funccategory == '' or answer == 'Answer... Egypt' or question == 'Question... Where do cats originate from?' or funccategory == 'Category Name':
            messagebox.showinfo(message='Make sure all entries aren\'t empty or have the default text inside them')
            return

        if colour == 'red':
            messagebox.showinfo(message='Please select a category colour')
            return

        if funccategory in category or funccategory.lower() in category or funccategory.title() in category or funccategory.upper() in category:
            messagebox.showwarning(message='Category name already in use!')
            return

        c.execute('INSERT INTO subjects VALUES (?, ?)', (funccategory, colour))
        c.execute('INSERT INTO questions VALUES (?, ?, ?)', (funccategory, answer, question))
        conn.commit()

        messagebox.showinfo(message='New category made!')
        main.refreshlist()
        self.window.destroy()

class EditCategory:
    def __init__(self, main):
        self.window = Toplevel()
        self.window.title('Edit Category')
        #self.window.geometry('450x300')

        if useIcon:
            self.window.iconbitmap(icon)

        self.buttoncolour = main.colour #setting the colour of the button

        Label(self.window, text='Edit Category', font=bfont35, fg=main.colour).pack()

        self.frame1 = Frame(self.window)
        Label(self.frame1, text='Name', font=font20, fg=main.colour).pack(side=LEFT, padx=5)
        self.categoryname = Entry(self.frame1, font=font20)
        self.categoryname.bind('<FocusIn>', lambda event: FocusIn(self.categoryname, 'Category... Animals'))
        self.categoryname.bind('<FocusOut>', lambda event: FocusOut(self.categoryname, 'Category... Animals'))
        self.categoryname.insert(0, main.category)
        self.categoryname.pack(side=LEFT, padx=5)
        self.frame1.pack(pady=10, padx=10)

        self.frame2 = Frame(self.window)
        Label(self.frame2, text='Colour', font=font20, fg=main.colour).pack(side=LEFT, padx=5)
        self.button = Button(self.frame2, font=font20, bg=self.buttoncolour, width=3, command=self.getcolour)
        self.button.pack(side=LEFT, padx=5)
        self.frame2.pack(pady=10, padx=10)

        self.updatebutton = Button(self.window, font=font20, text='Save', bg=self.buttoncolour, fg='white' , width=20, command=self.update)
        self.updatebutton.pack(pady=5, padx=5)


    def getcolour(self, event=None):
        '''Updates self.buttoncolour to chosen colour'''
        self.buttoncolour = colorchooser.askcolor(initialcolor=main.colour)[1]
        self.button['bg'] = self.buttoncolour

    def update(self, event=None):
        global questionList
        '''Updates the file to apply changes made by the user'''

        newcolour = self.buttoncolour
        newname = self.categoryname.get()

        if newcolour == '' or newcolour is None:
            newcolour = main.colour

        if newname == '' or newname == 'Category... Animals':
            messagebox.showinfo(message='Make sure all entries aren\'t empty or have the default text inside them')
            return

        if newname in category and newname != main.category:
            if not messagebox.askyesno(message='There are categories/is a category with this chosen name, would you like to join them together?'):
                return

        c.execute('DELETE FROM subjects WHERE subject = (?)', (main.category,))
        c.execute('INSERT INTO subjects VALUES (?, ?)', (newname, newcolour))
        c.execute('UPDATE questions SET subject = (?) WHERE subject = (?)', (newname, main.category))
        conn.commit()

        messagebox.showinfo(message='Category Updated! The app will now restart :)')

        self.window.destroy()
        main.refreshlist()
        main.window.destroy()
        main.changecategory() #restarting the app



class NoQuestions:
    def __init__(self):
        self.window = Toplevel()
        self.window.title('No Questions')
        #self.window.geometry('525x350')
        Label(self.window, text='Make your first question!',font=bfont35, fg='green').pack(padx=10)

        if useIcon:
            self.window.iconbitmap(icon)

        self.frame1 = Frame(self.window)
        Label(self.frame1, text='Category Name', font=font20).pack(pady=10, padx=10, side=LEFT)

        #creating the category entry and adding binding focusin and focus out functions
        self.category = Entry(self.frame1, font=font20)
        self.category.bind('<FocusIn>', lambda event: FocusIn(self.category, 'Category... Animals'))
        self.category.bind('<FocusOut>', lambda event: FocusOut(self.category, 'Category... Animals'))
        self.category.insert(0,'Category... Animals')
        self.category['fg'] = 'grey'
        self.category.pack(pady=10, padx=10, side=LEFT)

        self.frame1.pack()

        self.scrolledtext = ScrolledText(self.window, font=font20, width=33, height=5, wrap=WORD)
        self.scrolledtext.bind('<FocusIn>', lambda event: ScrolledFocusIn(self.scrolledtext))
        self.scrolledtext.bind('<FocusOut>', lambda event: ScrolledFocusOut(self.scrolledtext))
        self.scrolledtext.insert(0.0, 'Question... Where do cats originate from?')
        self.scrolledtext['fg'] = 'grey'
        self.scrolledtext.pack()

        self.frame2 = Frame(self.window)

        #ans entry with focusin and focusout functions
        self.ansentry = Entry(self.frame2, font=font20, width=27)
        self.ansentry.bind('<FocusIn>', lambda event: FocusIn(self.ansentry, 'Answer... Egypt'))
        self.ansentry.bind('<FocusOut>', lambda event: FocusOut(self.ansentry, 'Answer... Egypt'))
        self.ansentry.insert(0,'Answer... Egypt')
        self.ansentry['fg'] = 'grey'
        self.ansentry.pack(padx=5,side=LEFT)

        self.button = Button(self.frame2, text='Create', bg='green', fg='white' ,font=font20, command=self.add)
        self.button.pack(padx=5, side=LEFT)

        self.frame2.pack(pady=5)

    def add(self, event=None):
        '''Adds a new question to the dataFile when there is no questions'''

        question = self.scrolledtext.get(0.0,'end-1c')
        answer = self.ansentry.get()
        category = self.category.get()

        if answer == '' or question == '' or category == '' or answer == 'Answer... Egypt' or question == 'Question... Where do cats originate from?' or category == 'Category Name':
            messagebox.showinfo(message='Make sure all entries aren\'t empty or have the default text inside them')
            return

        c.execute('INSERT INTO subjects VALUES (?, ?)', (category, '#ff0000'))
        c.execute('INSERT INTO questions VALUES (?, ?, ?)', (category, answer, question))
        conn.commit()

        GetQuestions()
        self.window.destroy()
        Start()

class EditFont:
    def __init__(self):
        self.window = Toplevel()
        self.window.title('Change Font')

        if useIcon:
            self.window.iconbitmap(icon)

        Label(self.window, text='Change Font', font=bfont35).pack(pady=5, padx=5)

        Label(self.window, text='Changing the font might change the spacings of the GUI', font=font20).pack(padx=5)

        self.frame = Frame(self.window)
        Label(self.frame, text='Select Font -', font=font24).pack(side=LEFT)
        self.dropdown = ttk.Combobox(self.frame, values=supported, font=font20)

        if globalfont:
            self.dropdown.current(supported.index(globalfont))
        else:
            self.dropdown.current(supported.index('Calibri'))

        self.dropdown.pack(side=LEFT)
        self.frame.pack(pady=5, padx=5)

        #-------------------------

        self.frame2 = Frame(self.window)


        self.link = Label(self.frame2, text='Edit Font Ratio/Size -', font=font24 + ['underline'], cursor='hand2', fg='blue')

        self.link.bind('<Button-1>', self.fontratiohelp)
        self.link.pack(side=LEFT)

        self.fontratioentry = Entry(self.frame2, font=font24, width=2)
        self.fontratioentry.insert(0, fontRatio)
        self.fontratioentry.pack(side=LEFT)

        self.frame2.pack(pady=5, padx=5)

        #-------------------------

        self.frame3 = Frame(self.window)

        self.button = Button(self.frame3, text='Save Option', font=font24, bg='deep sky blue', fg='white', command=self.edit, width=20)
        self.button.pack(side=LEFT, pady=5, padx=5)

        self.default = Button(self.frame3, text='Default', font=font24, bg='deep sky blue', fg='white', command=lambda: self.edit(default=True))
        self.default.pack(side=LEFT, pady=5, padx=5)

        self.frame3.pack()

    def fontratiohelp(self, event=None):
        '''Is run when the user clicks link on font ratio'''
        messagebox.showinfo(message='Anything from 0 and below or 2.5 and above wont work correctly')

    def edit(self, event=None, default=False):
        '''Edits the font in the optionFile defined at the very top of the program'''

        chosen = self.dropdown.get()
        ratio = self.fontratioentry.get()
        optionlist = GetOptions()
        foundFont, foundRatio = False, False

        if default:
            chosen = 'Calibri'
            ratio = '1'
        if not ratio:
            ratio = '1'

        #checking if in options
        for option in optionlist:
            if option[0] == 'font':
                option[1] = chosen
                foundFont = True
            elif option[0] == 'fontRatio':
                option[1] = ratio
                foundRatio = True

        #adding to options if not already in
        if not foundFont:
            optionlist.append(['font', chosen])
        if not foundRatio:
            optionlist.append(['fontRatio',fontRatio])

        #writing to optionFile
        c.execute('DELETE FROM options')
        c.executemany('INSERT INTO options VALUES (?, ?)', optionlist)
        conn.commit()

        messagebox.showinfo(message='Please restart the app to see the changes take effect :)')

        self.window.destroy()


class MainGUISize:
    def __init__(self):

        self.window = Toplevel()
        self.window.title('MainGUI Size')

        if useIcon:
            self.window.iconbitmap(icon)

        Label(self.window, text='Change MainGUI size', font=bfont35).pack(pady=5, padx=5)

        self.frame1 = Frame(self.window)
        Label(self.frame1, text='Size', font=font24).pack(side=LEFT)

        self.dropdown = ttk.Combobox(self.frame1, values=supportedSizes, font=font24)
        self.dropdown.current(supportedSizes.index(mainguiSize))
        self.dropdown.pack(side=LEFT)

        self.frame1.pack(pady=10, padx=10)

        self.frame2 = Frame(self.window)

        self.savebutton = Button(self.frame2, text='Save Option', font=font24, bg='deep sky blue', fg='white', command=self.edit, width=20)
        self.savebutton.pack(side=LEFT, pady=5, padx=5)

        self.default = Button(self.frame2, text='Default', font=font24, bg='deep sky blue', fg='white', command=lambda: self.edit(default=True))
        self.default.pack(side=LEFT, pady=5, padx=5)

        self.frame2.pack()

    def getcolour(self, event=None):
        '''Updates self.mainback to chosen colour'''
        self.new = colorchooser.askcolor(initialcolor=self.button['bg'])[1]
        self.button['bg'] = self.new


    def edit(self, event=None, default=False):
        '''Saves the mainguiSize option in the optionFile'''
        found = False
        optionlist = GetOptions()

        if default:
            chosen = '700x350'
        else:
            chosen = self.dropdown.get()

        #add to list
        for option in optionlist:
            if option[0] == 'mainguiSize':
                option[1] = chosen
                found = True
        if not found:
            optionlist.append(['mainguiSize',self.dropdown.get()])

        #write to file
        c.execute('DELETE FROM options')
        c.executemany('INSERT INTO options VALUES (?, ?)', optionlist)
        conn.commit()

        messagebox.showinfo(message='Please restart the app to see the changes take effect :)')
        self.window.destroy()


class MainGUIBackground:
    def __init__(self):
        self.window = Toplevel()
        self.window.title('MainGUI Background')

        if useIcon:
            self.window.iconbitmap(icon)

        self.mainback = mainguiBackground #setting the colour of the button

        self.frame1 = Frame(self.window)
        Label(self.frame1, text='Background Colour', font=font20).pack(side=LEFT, padx=5)
        self.button = Button(self.frame1, font=font20, bg=self.mainback, width=3, command=self.getcolour)
        self.button.pack(side=LEFT, padx=5)
        self.defaultbutton = Button(self.frame1, text='Default', font=font20, bg='deep sky blue', fg='white', command=lambda: self.edit(default=True), width=10)
        self.defaultbutton.pack(side=LEFT, padx=5)
        self.frame1.pack(pady=10, padx=10)

        self.savebutton = Button(self.window, text='Save Option', font=font24, bg='deep sky blue', fg='white', command=self.edit, width=20)
        self.savebutton.pack(pady=5, padx=5)

    def getcolour(self, event=None):
        '''Updates self.mainback to chosen colour'''
        self.new = colorchooser.askcolor(initialcolor=self.button['bg'])[1]
        self.button['bg'] = self.new

    def edit(self, event=None, default=False):
        '''Edits the mainguiBackground optionFile'''
        optionlist = GetOptions()
        found = False

        if default:
            self.new = 'SystemButtonFace'

        for option in optionlist:
            if option[0] == 'mainguiBackground':
                option[1] = self.new
                found = True
        if not found:
            optionlist.append(['mainguiBackground',self.new])

        c.execute('DELETE FROM options')
        c.executemany('INSERT INTO options VALUES (?, ?)', optionlist)
        conn.commit()

        messagebox.showinfo(message='Please restart the app to see the changes take effect :)')
        self.window.destroy()


class VerticalScrolledFrame(Frame): #credit to - https://gist.github.com/EugeneBakin/76c8f9bcec5b390e45df
   def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)


class SearchQuestions:
    def __init__(self, main):
        self.window = Toplevel()
        self.window.title('Search')
        #self.window.geometry('750x350')

        if useIcon:
            self.window.iconbitmap(icon)

        self.string = StringVar()
        self.string.set('You can enter part of a question or answer to see if that question already exists. Then choose either to search all questions or just the current category. You can also just press any button to get the full list.')

        Label(self.window, text='Search for a Question', fg='deep sky blue', font=bfont35).pack(pady=5, padx=5)
        Label(self.window, text='Caution! Searching all questions can be buggy if you have a lot of them', fg='red', font=font20, wraplength=650).pack()
        self.label = Label(self.window, textvariable=self.string, font=font20, wraplength=650)
        self.label.pack(padx=5)

        self.entry = Entry(self.window, font=font24, justify='center')
        self.entry.pack(pady=5, padx=5)

        self.frame1 = Frame(self.window)
        self.buttonall = Button(self.frame1, text='All Questions', bg='deep sky blue', font=font24, fg='white', command=lambda: self.search('all'))
        self.buttonall.pack(side=LEFT, padx=5)
        self.buttoncategory = Button(self.frame1, text='Category Only', bg=main.colour, font=font24, fg='white', command=lambda: self.search('category'))
        self.buttoncategory.pack(side=LEFT, padx=5)
        self.frame1.pack(pady=5, padx=5)

    def search(self, typeofsearch, event=None):
        '''Process to add the questions to a new frame, typeofsearch can be either 'all' or 'category' '''
        self.string.set('') #deleting big text
        self.label.pack_forget()
        #self.window.geometry('750x500')

        foundquestions = []

        #creating a list if clicked on one label (self because used in other methods)
        self.labelList = []

        if typeofsearch == 'all':
            for question in questionList:
                for query in [question[0],question[1],question[2]]:
                    if ((self.entry.get().lower() in query.lower()) or self.entry.get().lower() == query.lower()) and (question not in foundquestions): #if entry in question or answer and not found already
                        if typeofsearch == 'category' and question[0] == main.category: #if type is category then only add if category is same as category selected
                            foundquestions.append(question)
                        elif typeofsearch == 'all':
                            foundquestions.append(question)

        if typeofsearch == 'category':
            for question in questionList:
                for query in [question[0],question[1],question[2]]:
                    if ((self.entry.get().lower() in query.lower()) or self.entry.get().lower() == query.lower()) and (question not in foundquestions) and (question[0] == main.category): #if type is category then only add if category is same as category selected
                        foundquestions.append(question)

        #if there is already searched frames
        try:
            self.grandframe.pack_forget()
        except AttributeError:
            pass

        foundquestions.sort(key=lambda x: x[0]) #sorts the list so subjects are joined together

        self.grandframe = VerticalScrolledFrame(self.window)
        self.grandframe.pack(expand=True)

        c.execute('SELECT * FROM subjects')
        colours = {}
        for x in c.fetchall():
            colours[x[0]] = x[1]

        #creating frames for them all
        for question in foundquestions:
            frame = Frame(self.grandframe.interior)
            frame2 = Frame(frame)

            each = Label(frame2, text=question[0], fg=colours[question[0]], font=font12Underlined, cursor='hand2')
            each.bind('<Button-1>',self.eventhandler)
            each.pack(side=LEFT)

            self.labelList.append([each,question]) #adds all questions to a list with widget no. and question

            frame2.pack(anchor='w')

            string = question[2] + ' -> ' + question[1]
            Label(frame, text=string, font=font12, wraplength=700, anchor='w', justify='left').pack(side=LEFT)

            frame.pack(pady=5, padx=10, anchor='w')

    def eventhandler(self, event=None):
        '''Is ran when a link/question is pressed'''
        widget = event.widget
        question = [x for x in self.labelList if x[0] == widget][0][1] #index-ed to only get the question part

        yesno = messagebox.askyesno(message='Are you sure you want to change the current question to the one you clicked? It will also change the category currently selected.')
        if yesno:
            self.window.destroy()
            main.override(question) #changes stuff in MainGUI

class NotifyCorrect:
    def __init__(self):
        self.window = Toplevel()
        self.window.title('Notify Settings')

        if useIcon:
            self.window.iconbitmap(icon)

        Label(self.window, text='Notify Settings', font=bfont35).pack(pady=5, padx=5)
        Label(self.window, text="By default, the app doesn't notify the user when they are correct, instead it just moves to the next question", font=font20, wraplength=600).pack(padx=5)

        self.checkint = IntVar()

        if notifyWhenCorrect == 'True': #setting if toggled or not
            self.checkint.set(1)
        else:
            self.checkint.set(0)

        self.checkbutton = Checkbutton(self.window, text='Notify me when correct?', font=font20, variable=self.checkint, onvalue=1, offvalue=0)
        self.checkbutton.pack(pady=5, padx=5)

        self.button = Button(self.window, text='Save Option', font=font24, bg='deep sky blue', fg='white', command=self.edit)
        self.button.pack(pady=5, padx=5)

    def edit(self, event=None):
        '''Edits the option from the checkbutton'''
        global notifyWhenCorrect
        result = self.checkint.get()
        found = False

        if result == 1:
            notifyWhenCorrect = 'True'
        elif result == 0:
            notifyWhenCorrect = 'False'
        else:
            messagebox.showerror(message='Unexpected Error in edit setting - notifyWhenCorrect')
            self.window.destroy()
            return

        for option in globalOptions:
            if option[0] == 'notifyWhenCorrect':
                option[1] = notifyWhenCorrect
                found = True
        if not found:
            globalOptions.append(['notifyWhenCorrect',notifyWhenCorrect])

        c.execute('DELETE FROM options WHERE option = (?)', ('notifyWhenCorrect',))
        c.execute('INSERT INTO options VALUES (?, ?)', ('notifyWhenCorrect',notifyWhenCorrect))
        conn.commit()

        messagebox.showinfo(message='You should start to see the effects of this change now :)')
        self.window.destroy()

def GetQuestions():
    '''Changes the global questionList and category lists'''
    global category, questionList
    questionList, category = Questions()

def GetOptions():
    '''Returns a list of the options inside optionFile'''
    c.execute('SELECT * FROM options')
    return [list(x) for x in c.fetchall()]

def CheckFile(file):
    '''Returns True if the file is there, and False if not'''
    try:
        open(file,'r').close()
        return True
    except FileNotFoundError:
        return False

def Start():
    '''Starts the program'''
    if useImages:
        welcomePage = Welcome('Welcome')
    else:
        welcomePage = Welcome('Welcome', image=False)
    root.mainloop()


#----------These are global so they can be used by all classes----------
def FocusIn(entry, insert_text, event=None):
    '''These add the grey text'''
    if entry.get() == insert_text:
        entry.delete(0,END)
        entry.insert(0,'')
        entry.config(fg='black')

def FocusOut(entry, insert_text, event=None):
    '''These add the grey text'''
    if entry.get() == '':
        entry.insert(0,str(insert_text))
        entry.config(fg='grey')


def ScrolledFocusIn(entry, event=None):
    '''Add the grey text to the scrolledtext widgets'''
    if entry.get(0.0, 'end-1c') == 'Question... Where do cats originate from?':
        entry.delete(0.0,END)
        entry.insert(0.0,'')
        entry.config(fg='black')

def ScrolledFocusOut(entry, event=None):
    '''Add the grey text to the scrolledtext widgets'''
    if entry.get(0.0, 'end-1c') == '':
        entry.insert(0.0, 'Question... Where do cats originate from?')
        entry.config(fg='grey')
#-----------------------------------------------------------------------

create = True if not CheckFile(dataFile) else False
conn = sqlite3.connect(dataFile)
c = sqlite3.Cursor(conn)
if create:
    c.execute('CREATE TABLE questions (subject varchar(255), answer varchar(255), question varchar(255))')
    c.execute('CREATE TABLE subjects (subject varchar(255), colour varchar(255))')
    c.execute('CREATE TABLE options (option varchar(255), parameter varchar(255))')
    conn.commit()

#checking all the images and icons are there
if not CheckFile(icon):
    useIcon = False
else:
    useIcon = True

if CheckFile(tick) or CheckFile(tickGIF):
    useImages = True
else:
    useImages = False


#getting the options as a global list and changing the font variables accordingly

globalOptions = GetOptions()
for option in globalOptions:

    if option[0] == 'font':
        globalfont = option[1]
        for font in [bfont35, font24, font20]:
            font[0] = option[1]

    if option[0] == 'fontRatio':
        fontRatio = option[1]
        for font in [bfont35, font24, font20, font12, font12, font12Underlined]:
            font[1] = str(round(int(font[1]) * float(fontRatio)))

    if option[0] == 'mainguiSize':
        mainguiSize = option[1]

    if option[0] == 'mainguiBackground':
        mainguiBackground = option[1]

    if option[0] == 'questionLocation':
        customQuestionLocation = option[1]
        dataFile = customQuestionLocation

    if option[0] == 'notifyWhenCorrect':
        notifyWhenCorrect = option[1]

GetQuestions()
Start()
