#!/usr/bin/env python3
import os,json,threading,subprocess,tkinter as tk
from tkinter import filedialog,messagebox
from urllib.request import Request,urlopen

MODEL="qwen2.5:0.5b"; R=os.path.expanduser("~/Rune"); D=os.path.join(R,"data")
F=os.path.join(R,"files"); P=os.path.join(R,"projects"); M=os.path.join(D,"memory.txt"); H=os.path.join(D,"history.txt")
for x in (D,F,P): os.makedirs(x,exist_ok=True)
for x in (M,H):
    if not os.path.exists(x): open(x,"a").close()

BG="#080a0f"; SIDE="#0d1118"; PANEL="#111722"; TEXT="#e9eef7"; MUTED="#7f8b9d"; CYAN="#55dfff"; PURPLE="#9587ff"; GREEN="#4de18a"; RED="#ff6262"
root=box=entry=status=content=None
busy=False; voice=True

def speak(s):
    if voice and s.strip(): threading.Thread(target=lambda:subprocess.run(["say","-r","185",s],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL),daemon=True).start()

def read(p):
    try:
        with open(p,encoding="utf8") as f:return f.read()
    except:return ""

def online():
    try:
        with urlopen("http://127.0.0.1:11434/api/tags",timeout=1) as r:return r.status==200
    except:return False

def status_update():
    if status: status.config(text="● AI THINKING" if busy else ("● AI READY" if online() else "● AI OFFLINE"),fg=PURPLE if busy else (GREEN if online() else RED))

def add(w,t):
    box.config(state="normal")
    box.insert("end","\n"+w.upper()+"\n","ul" if w=="You" else "rl")
    if t: box.insert("end",t+"\n","u" if w=="You" else "r")
    box.config(state="disabled"); box.see("end")

def token(t):
    box.config(state="normal"); box.insert("end",t,"r"); box.config(state="disabled"); box.see("end")

def ask(q):
    global busy
    try:
        if not online(): root.after(0,add,"Rune","Ollama is not running. Start it with: ollama serve"); return
        prompt=f"""You are Rune, a local AI assistant created by Allen. Be concise, direct, helpful and slightly witty. Help with programming, C, C++, Python, Shell, HTML, macOS, Linux and game development.
Memory:
{read(M)}
Recent chat:
{read(H)[-5000:]}
User: {q}
Rune:"""
        data=json.dumps({"model":MODEL,"prompt":prompt,"stream":True,"options":{"temperature":.7,"num_ctx":2048}}).encode()
        req=Request("http://127.0.0.1:11434/api/generate",data=data,headers={"Content-Type":"application/json"})
        full=""
        with urlopen(req,timeout=300) as res:
            for line in res:
                try:
                    t=json.loads(line.decode()).get("response","")
                    if t: full+=t; root.after(0,token,t)
                except: pass
        with open(H,"a",encoding="utf8") as f:f.write(f"\nYou: {q}\nRune: {full}\n")
        speak(full)
    except Exception as e: root.after(0,add,"Rune","AI error: "+str(e))
    finally:
        busy=False; root.after(0,status_update)

def send():
    global busy
    if busy:return
    q=entry.get().strip()
    if not q:return
    entry.delete(0,"end"); add("You",q); l=q.lower()
    if l in ("hi","hello","hey"):
        r="Hello. I'm Rune. What are we building?"; add("Rune",r); speak(r); return
    if l=="status":
        r="Rune is online. Ollama is %s. Model: %s."%("connected" if online() else "offline",MODEL); add("Rune",r); speak(r); return
    if l=="about":
        r="I'm Rune, a local AI assistant created by Allen."; add("Rune",r); speak(r); return
    if l.startswith("remember "):
        with open(M,"a",encoding="utf8") as f:f.write(q[9:].strip()+"\n")
        add("Rune","Memory saved."); speak("Memory saved."); return
    busy=True; add("Rune",""); status_update(); threading.Thread(target=ask,args=(q,),daemon=True).start()

def clear():
    for w in content.winfo_children():w.destroy()

def header(a,b):
    f=tk.Frame(content,bg=BG);f.pack(fill="x",padx=30,pady=(25,15))
    tk.Label(f,text=a,bg=BG,fg=TEXT,font=("Helvetica",22,"bold")).pack(anchor="w")
    tk.Label(f,text=b,bg=BG,fg=MUTED,font=("Helvetica",11)).pack(anchor="w")

T={"C":"""#include <stdio.h>

int main(void)
{
    int example = 0;
    printf("Hello from Rune!\\n");
    return 0;
}
""","Python":"""#!/usr/bin/env python3

name = "Rune"

def hello():
    print("Hello from Rune!")

if __name__ == "__main__":
    hello()
""","Shell":"""#!/bin/sh

NAME="Rune"

echo "Hello from Rune!"
""","HTML":"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Rune Project</title></head>
<body><h1>Hello from Rune!</h1></body>
</html>
"""}

def chat():
    global box,entry,status
    header("Chat","Talk to Rune.")
    status=tk.Label(content,text="● CHECKING AI",bg=BG,fg=MUTED,font=("Helvetica",9));status.pack(anchor="e",padx=30)
    box=tk.Text(content,bg=PANEL,fg=TEXT,insertbackground=TEXT,relief="flat",bd=0,wrap="word",font=("Helvetica",11),padx=20,pady=15)
    box.pack(fill="both",expand=True,padx=30);box.tag_config("ul",foreground=CYAN,font=("Helvetica",11,"bold"));box.tag_config("rl",foreground=PURPLE,font=("Helvetica",11,"bold"));box.tag_config("u",foreground=TEXT);box.tag_config("r",foreground=TEXT);box.config(state="disabled")
    f=tk.Frame(content,bg=BG);f.pack(fill="x",padx=30,pady=20)
    entry=tk.Entry(f,bg="#171e2a",fg=TEXT,insertbackground=TEXT,relief="flat",bd=0,font=("Helvetica",11));entry.pack(side="left",fill="x",expand=True,ipady=11,padx=(0,10))
    tk.Button(f,text="SEND",bg=CYAN,fg="#061016",relief="flat",bd=0,font=("Helvetica",11,"bold"),command=send).pack(side="right")
    entry.bind("<Return>",lambda e:send());add("Rune","Hello. I'm Rune. What are we building?");status_update()

def files():
    header("Files","Files created by Rune.")
    lb=tk.Listbox(content,bg=PANEL,fg=TEXT,relief="flat",bd=0);lb.pack(fill="both",expand=True,padx=30)
    for x in sorted(os.listdir(F)):lb.insert("end",x)
    def make():
        p=filedialog.asksaveasfilename(initialdir=F)
        if p:open(p,"a").close();show("Files")
    tk.Button(content,text="+ CREATE FILE",bg=CYAN,fg="#061016",command=make).pack(anchor="e",padx=30,pady=20)

def mem():
    header("Memory","Rune's persistent memory.")
    t=tk.Text(content,bg=PANEL,fg=TEXT,insertbackground=TEXT,relief="flat",bd=0);t.pack(fill="both",expand=True,padx=30);t.insert("1.0",read(M))
    def save():open(M,"w",encoding="utf8").write(t.get("1.0","end").strip());messagebox.showinfo("Rune","Memory saved.")
    tk.Button(content,text="SAVE",bg=CYAN,fg="#061016",command=save).pack(anchor="e",padx=30,pady=20)

def code():
    header("Code","Generate starter templates.")
    for lang,val in T.items():
        f=tk.Frame(content,bg=PANEL);f.pack(fill="x",padx=30,pady=5)
        tk.Label(f,text=lang,bg=PANEL,fg=TEXT,font=("Helvetica",11,"bold")).pack(side="left",padx=20,pady=15)
        tk.Button(f,text="CREATE TEMPLATE",bg=CYAN,fg="#061016",command=lambda l=lang:save_template(l)).pack(side="right",padx=20)

def save_template(lang):
    ext={"C":".c","Python":".py","Shell":".sh","HTML":".html"}[lang]
    p=filedialog.asksaveasfilename(initialdir=F,defaultextension=ext)
    if p:open(p,"w",encoding="utf8").write(T[lang]);messagebox.showinfo("Rune","Template created.")

def projects():
    header("Projects","Your Rune projects.")
    lb=tk.Listbox(content,bg=PANEL,fg=TEXT,relief="flat",bd=0);lb.pack(fill="both",expand=True,padx=30)
    for x in sorted(os.listdir(P)):lb.insert("end",x)
    tk.Button(content,text="+ CREATE PROJECT",bg=CYAN,fg="#061016",command=new_project).pack(anchor="e",padx=30,pady=20)

def new_project():
    w=tk.Toplevel(root);w.title("New Rune Project");w.geometry("400x250");w.configure(bg=BG)
    tk.Label(w,text="PROJECT NAME",bg=BG,fg=TEXT).pack(anchor="w",padx=25,pady=(25,5))
    n=tk.Entry(w,bg=PANEL2,fg=TEXT);n.pack(fill="x",padx=25)
    lang=tk.StringVar(value="Python");tk.OptionMenu(w,lang,"C","Python","Shell","HTML").pack(fill="x",padx=25,pady=20)
    def build():
        name=n.get().strip()
        if not name:return
        p=os.path.join(P,name);os.makedirs(os.path.join(p,"src"));os.makedirs(os.path.join(p,"assets"));os.makedirs(os.path.join(p,"build"))
        l=lang.get();ext={"C":".c","Python":".py","Shell":".sh","HTML":".html"}[l];folder=p if l=="HTML" else os.path.join(p,"src")
        open(os.path.join(folder,("index" if l=="HTML" else "main")+ext),"w",encoding="utf8").write(T[l])
        open(os.path.join(p,"README.md"),"w").write("# "+name+"\n\nCreated with Rune.\nMade by Allen.\n");w.destroy();show("Projects")
    tk.Button(w,text="CREATE PROJECT",bg=CYAN,fg="#061016",command=build).pack()

def settings():
    header("Settings","Rune configuration.")
    v=tk.BooleanVar(value=voice)
    def toggle():
        global voice;voice=v.get()
    tk.Checkbutton(content,text="Enable Rune Voice",variable=v,command=toggle,bg=BG,fg=TEXT,selectcolor=PANEL2).pack(anchor="w",padx=30,pady=20)
    tk.Label(content,text=f"Model: {MODEL}\nBackend: Ollama\nVoice: macOS Speech\nDirectory: {RUNE}",bg=BG,fg=MUTED,justify="left").pack(anchor="w",padx=30)

def show(page):
    clear();{"Chat":chat,"Files":files,"Memory":mem,"Code":code,"Projects":projects,"Settings":settings}[page]()

def startup():
    o=tk.Frame(root,bg=BG);o.place(relx=0,rely=0,relwidth=1,relheight=1)
    tk.Label(o,text="RUNE",bg=BG,fg=CYAN,font=("Helvetica",38,"bold")).place(relx=.5,rely=.4,anchor="center")
    tk.Label(o,text="MADE BY ALLEN",bg=BG,fg=MUTED,font=("Helvetica",12)).place(relx=.5,rely=.49,anchor="center")
    s=tk.Label(o,text="INITIALIZING...",bg=BG,fg=MUTED);s.place(relx=.5,rely=.56,anchor="center")
    stages=["INITIALIZING...","LOADING CORE...","LOADING MEMORY...","CONNECTING TO OLLAMA...","CHECKING AI...","RUNE ONLINE"]
    def a(i=0):
        if i<len(stages):s.config(text=stages[i]);root.after(250,lambda:a(i+1))
        else:o.destroy();show("Chat");speak("Rune online.")
    a()

def main():
    global root,content
    root=tk.Tk();root.title("Rune v1.1 — Made by Allen");root.geometry("1100x700");root.minsize(850,550);root.configure(bg=BG)
    side=tk.Frame(root,bg=SIDE,width=215);side.pack(side="left",fill="y");side.pack_propagate(False)
    tk.Label(side,text="RUNE",bg=SIDE,fg=CYAN,font=("Helvetica",38,"bold")).pack(anchor="w",padx=22,pady=(28,0))
    tk.Label(side,text="v1.1 • MADE BY ALLEN",bg=SIDE,fg=MUTED).pack(anchor="w",padx=22,pady=(0,20))
    content=tk.Frame(root,bg=BG);content.pack(side="right",fill="both",expand=True)
    for n in ("Chat","Projects","Files","Memory","Code","Settings"):
        tk.Button(side,text=n,bg=SIDE,fg=TEXT,activebackground=PANEL2,relief="flat",bd=0,anchor="w",padx=22,pady=10,command=lambda x=n:show(x)).pack(fill="x",padx=8,pady=2)
    root.after(100,startup);root.mainloop()

if __name__=="__main__":main()