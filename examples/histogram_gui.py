from Tkinter import Tk, BOTH

class Example(Frame):
  
    def __init__(self):
        super().__init__()
         
        self.initUI()
        
    
    def initUI(self):
      
        self.master.title("Simple")
        self.pack(fill=BOTH, expand=1)
        

def main():
  
    root = Tk()
    root.geometry("250x150+300+300")
    app = Example()
    root.mainloop()  


if __name__ == '__main__':
    main()  
