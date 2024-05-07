import socket, os
from re import match
import customtkinter as ctk
from tkinter import messagebox
from shared import getJsonData

from threading import Thread
from multiprocessing.pool import ThreadPool

class portScanner:
    def __init__(self):
        #scanner variables
        self.scanning = False
        self.openPorts = []
        self.portsDict = getJsonData()
        self.ports = self.portsDict.keys()
        self.numberOfPorts = len(self.ports)

        if os.path.exists("theme.json"):
            ctk.set_default_color_theme("theme.json")
        #gui variables
        self.winsize = 400, 400
        self.winsize_x = self.winsize[0]
        self.winsize_y = self.winsize[1]

        self.root = ctk.CTk()
        
        #self.mainframe = ctk.CTkFrame(self.root)
        #self.mainframe.place(x=self.winsize_x/2, y=self.winsize_y/2, anchor="center")

        self.frameTitle = ctk.CTkLabel(self.root, text="Port Scanner")
        self.frameTitle.pack(side="top", pady=12)

        self.hostEntry = ctk.CTkEntry(self.root, width=200, placeholder_text="Host")
        self.hostEntry.pack(padx=50)

        self.startButton = ctk.CTkButton(self.root, width=200, text="Start Scanning", command=Thread(target=self.startScanning).start)
        self.startButton.pack(pady=5)
        self.startButton.configure(state="disabled")

        self.textarea = ctk.CTkTextbox(self.root)
        self.textarea.configure(state="disabled")
        self.textarea.pack()

        global progressbarPercentage
        progressbarPercentage = 0
        self.progressbar = ctk.CTkProgressBar(self.root, orientation="horizontal", corner_radius=5)
        self.progressbar.set(progressbarPercentage)
        self.progressbar.pack()

        self.percentageLabel = ctk.CTkLabel(self.root, text=f"{progressbarPercentage}%")
        self.percentageLabel.pack()

        self.hostEntry.bind("<KeyRelease>", self.validateInput)

        self.root.resizable(0,0)
        self.root.geometry(f"{self.winsize_x}x{self.winsize_y}")
        self.root.title("Port Scanner by ~Zappitelli Riccardo github.com/Ricc4rdo0107")
        self.root.mainloop()


    def checkPort(self, port:int, host:str=None):
        if host is None:
            host = self.host
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res = s.connect_ex((host, int(port)))
        if res == 0:
            self.openPorts.append(port)
        s.close()
        return port

    def setProgressBarPercentage(self, percentage:int):
        global progressbarPercentage
        progressbarPercentage = percentage/100
        self.percentageLabel.configure(text=f"{round(progressbarPercentage*100)}%")
        self.progressbar.set(progressbarPercentage)
        
    def startScanning(self):
        self.scanning = True
        workers = os.cpu_count()
        host = self.hostEntry.get()
        self.host = host
        self.tPrint(f"Starting to scan {host}\n")
        with ThreadPool(workers) as pool:
            for index, port in enumerate(pool.imap(self.checkPort, self.ports), 1):
                progress = round(index / self.numberOfPorts * 100)
                self.setProgressBarPercentage(progress)
                #print(port)
        self.scanning = False
        #messagebox.showinfo("Done", "Scan completed successfully")
        for port in self.openPorts:
            self.tPrint(f"{port:<10} : {self.portsDict[str(port)]:<15}\n")
        self.tprint(f"\nScan completed successfully")
        
    """
    def testProgressbar(self):
        global progressbarPercentage
        if progressbarPercentage < 1:
            progressbarPercentage += 0.05
            self.progressbar.set(progressbarPercentage)
            self.progressbar.after(50, self.testProgressbar)
        else:
            progressbarPercentage = 0
            self.progressbar.set(progressbarPercentage)
    """

    def tPrint(self, text:str):
        self.textarea.configure(state="normal")
        self.textarea.insert("end", text)
        self.textarea.configure(state="disabled")

    def validateInput(self, event=None):
        host = self.hostEntry.get()
        check = self.checkAddrIsOk(host)
        if self.scanning or not(check):
            self.disableStartButton()
            return False
        self.enableStartButton()
        return True
    
    def enableStartButton(self):
        self.startButton.configure(state="enabled")
        
    def disableStartButton(self):
        self.startButton.configure(state="disabled")

    def checkAddrIsOk(self, addr:str):
        isValidIpAddress  = bool(match(r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$", addr))
        isValidHostName   = bool(match(r"^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*$", addr))
        return isValidIpAddress or isValidHostName


if __name__ == "__main__":
    assert os.path.exists("common_ports.json"), "Missing common_ports.json file"
    pscanner = portScanner()
