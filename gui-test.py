import tkinter as tk

def handleGUIButton(arg):
    pass

window = tk.Tk()
window.title("LED dev controller")

window.rowconfigure(0,minsize=800, weight=1)
window.columnconfigure(1,minsize=800, weight=1)

btnFrame = tk.Frame(window, relief=tk.RAISED, bd=2)

btnTL = tk.Button(btnFrame, text="Y", command=lambda: handleGUIButton("Y"))
btnT = tk.Button(btnFrame, text="K", command=lambda: handleGUIButton("K"))
btnTR = tk.Button(btnFrame, text="U", command=lambda: handleGUIButton("U"))
btnL = tk.Button(btnFrame, text="H", command=lambda: handleGUIButton("H"))
btnW = tk.Button(btnFrame, text=".", command=lambda: handleGUIButton("."))
btnR = tk.Button(btnFrame, text="L", command=lambda: handleGUIButton("L"))
btnBL = tk.Button(btnFrame, text="B", command=lambda: handleGUIButton("B"))
btnB = tk.Button(btnFrame, text="J", command=lambda: handleGUIButton("J"))
btnBR = tk.Button(btnFrame, text="N", command=lambda: handleGUIButton("N"))

btn_KA = tk.Button(btnFrame, text="A", command=lambda: handleGUIButton("K_A"))
btn_KB = tk.Button(btnFrame, text="B", command=lambda: handleGUIButton("K_B"))
btn_KX = tk.Button(btnFrame, text="X", command=lambda: handleGUIButton("K_X"))
btn_KY = tk.Button(btnFrame, text="Y", command=lambda: handleGUIButton("K_Y"))
btn_KL = tk.Button(btnFrame, text="L", command=lambda: handleGUIButton("K_L"))
btn_KR = tk.Button(btnFrame, text="R", command=lambda: handleGUIButton("K_R"))
btn_START = tk.Button(btnFrame, text="START", command=lambda: handleGUIButton("START"))
btn_SELECT = tk.Button(btnFrame, text="SELECT", command=lambda: handleGUIButton("SELECT"))

# arrow keys
btnTL.grid(row=0,column=0,sticky="ew", padx=5, pady=5)
btnT.grid(row=0,column=1,sticky="ew", padx=5, pady=5)
btnTR.grid(row=0,column=2,sticky="ew", padx=5, pady=5)
btnL.grid(row=1,column=0,sticky="ew", padx=5, pady=5)
btnW.grid(row=1,column=1,sticky="ew", padx=5, pady=5)
btnR.grid(row=1,column=2,sticky="ew", padx=5, pady=5)
btnBL.grid(row=2,column=0,sticky="ew", padx=5, pady=5)
btnB.grid(row=2,column=1,sticky="ew", padx=5, pady=5)
btnBR.grid(row=2,column=2,sticky="ew", padx=5, pady=5)

# buttons
btn_KA.grid(row=2,column=5,sticky="ew",padx=5,pady=5)
btn_KB.grid(row=2,column=4,sticky="ew",padx=5,pady=5)
btn_KX.grid(row=1,column=4,sticky="ew",padx=5,pady=5)
btn_KY.grid(row=1,column=5,sticky="ew",padx=5,pady=5)
btn_KL .grid(row=0,column=4,sticky="ew",padx=5,pady=5)
btn_KR .grid(row=0,column=5,sticky="ew",padx=5,pady=5)
btn_START.grid(row=1,column=6,sticky="ew",padx=5,pady=5)
btn_SELECT.grid.grid(row=0,column=6,sticky="ew",padx=5,pady=5)


window.mainloop()
