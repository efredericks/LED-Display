import tkinter as tk

class GUIController:
    def __init__(self, q):
        self.queue = q
        self.window = tk.Tk()
        self.window.title("LED dev controller")

        self.window.rowconfigure(0,minsize=800, weight=1)
        self.window.columnconfigure(1,minsize=800, weight=1)

        self.btnFrame = tk.Frame(self.window, relief=tk.RAISED, bd=2)
        self.btnFrame.pack()

        self.btnTL = tk.Button(self.btnFrame, text="Y", command=lambda: self.handleGUIButton("Y"))
        self.btnT = tk.Button(self.btnFrame, text="K", command=lambda: self.handleGUIButton("K"))
        self.btnTR = tk.Button(self.btnFrame, text="U", command=lambda: self.handleGUIButton("U"))
        self.btnL = tk.Button(self.btnFrame, text="H", command=lambda: self.handleGUIButton("H"))
        self.btnW = tk.Button(self.btnFrame, text=".", command=lambda: self.handleGUIButton("."))
        self.btnR = tk.Button(self.btnFrame, text="L", command=lambda: self.handleGUIButton("L"))
        self.btnBL = tk.Button(self.btnFrame, text="B", command=lambda: self.handleGUIButton("B"))
        self.btnB = tk.Button(self.btnFrame, text="J", command=lambda: self.handleGUIButton("J"))
        self.btnBR = tk.Button(self.btnFrame, text="N", command=lambda: self.handleGUIButton("N"))

        self.btn_KA = tk.Button(self.btnFrame, text="A", command=lambda: self.handleGUIButton("K_A"))
        self.btn_KB = tk.Button(self.btnFrame, text="B", command=lambda: self.handleGUIButton("K_B"))
        self.btn_KX = tk.Button(self.btnFrame, text="X", command=lambda: self.handleGUIButton("K_X"))
        self.btn_KY = tk.Button(self.btnFrame, text="Y", command=lambda: self.handleGUIButton("K_Y"))
        self.btn_KL = tk.Button(self.btnFrame, text="L", command=lambda: self.handleGUIButton("K_L"))
        self.btn_KR = tk.Button(self.btnFrame, text="R", command=lambda: self.handleGUIButton("K_R"))
        self.btn_START = tk.Button(self.btnFrame, text="START", command=lambda: self.handleGUIButton("START"))
        self.btn_SELECT = tk.Button(self.btnFrame, text="SELECT", command=lambda: self.handleGUIButton("SELECT"))

        self.btn_LR = tk.Button(self.btnFrame, text="L+R", command=lambda: self.handleGUIButton("L+R"))

        # arrow keys
        self.btnTL.grid(row=0,column=0,sticky="ew", padx=5, pady=5)
        self.btnT.grid(row=0,column=1,sticky="ew", padx=5, pady=5)
        self.btnTR.grid(row=0,column=2,sticky="ew", padx=5, pady=5)
        self.btnL.grid(row=1,column=0,sticky="ew", padx=5, pady=5)
        self.btnW.grid(row=1,column=1,sticky="ew", padx=5, pady=5)
        self.btnR.grid(row=1,column=2,sticky="ew", padx=5, pady=5)
        self.btnBL.grid(row=2,column=0,sticky="ew", padx=5, pady=5)
        self.btnB.grid(row=2,column=1,sticky="ew", padx=5, pady=5)
        self.btnBR.grid(row=2,column=2,sticky="ew", padx=5, pady=5)

        # buttons
        self.btn_KA.grid(row=2,column=5,sticky="ew",padx=5,pady=5)
        self.btn_KB.grid(row=2,column=4,sticky="ew",padx=5,pady=5)
        self.btn_KX.grid(row=1,column=4,sticky="ew",padx=5,pady=5)
        self.btn_KY.grid(row=1,column=5,sticky="ew",padx=5,pady=5)
        self.btn_KL .grid(row=0,column=4,sticky="ew",padx=5,pady=5)
        self.btn_KR .grid(row=0,column=5,sticky="ew",padx=5,pady=5)
        self.btn_START.grid(row=1,column=6,sticky="ew",padx=5,pady=5)
        self.btn_SELECT.grid(row=0,column=6,sticky="ew",padx=5,pady=5)
        self.btn_LR.grid(row=2,column=6,sticky="ew",padx=5,pady=5)


        self.window.mainloop()

    def handleGUIButton(self, arg):
        self.queue.put(arg)

        if arg == "L+R":
            self.window.quit()
        #print(arg)
