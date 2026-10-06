import tkinter as tk
from tkinter import messagebox
from database import admins, books, students, issued_books

def require_db():
    if admins is None:
        messagebox.showerror("MongoDB Error", "MongoDB is not running.\nStart MongoDB and restart the application.")
        return False
    return True

def clear(root):
    for w in root.winfo_children():
        w.destroy()

def login():
    if not require_db(): return
    root = tk.Tk()
    root.title("Library Management System - Login")
    root.geometry("420x300")
    root.resizable(False, False)

    tk.Label(root, text="LIBRARY MANAGEMENT SYSTEM", font=("Arial", 18, "bold")).pack(pady=25)
    form = tk.Frame(root); form.pack(pady=10)
    tk.Label(form, text="Username", width=12, anchor="w").grid(row=0,column=0,pady=8)
    user = tk.Entry(form, width=25); user.grid(row=0,column=1)
    tk.Label(form, text="Password", width=12, anchor="w").grid(row=1,column=0,pady=8)
    pwd = tk.Entry(form, width=25, show="*"); pwd.grid(row=1,column=1)

    def check():
        if admins.find_one({"username": user.get().strip(), "password": pwd.get()}):
            dashboard(root)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    tk.Button(root, text="Login", width=18, command=check).pack(pady=18)
    tk.Label(root, text="Default: admin / admin123", fg="gray").pack()
    root.mainloop()

def dashboard(root):
    clear(root)
    root.title("Library Management System")
    root.geometry("850x560")

    tk.Label(root, text="LIBRARY MANAGEMENT SYSTEM", font=("Arial", 22, "bold")).pack(pady=20)

    cards = tk.Frame(root); cards.pack(pady=15)
    values = [
        ("Total Books", books.count_documents({})),
        ("Students", students.count_documents({})),
        ("Issued", issued_books.count_documents({"status":"Issued"})),
        ("Available", sum(x.get("available",0) for x in books.find({}, {"available":1})))
    ]
    for i,(name,val) in enumerate(values):
        f=tk.Frame(cards, bd=1, relief="solid", padx=30, pady=18)
        f.grid(row=0,column=i,padx=8)
        tk.Label(f,text=str(val),font=("Arial",22,"bold")).pack()
        tk.Label(f,text=name).pack()

    btns = tk.Frame(root); btns.pack(pady=30)
    buttons=[
        ("Books", books_window),
        ("Students", students_window),
        ("Issue / Return", issue_window),
        ("Refresh", dashboard),
        ("Logout", login)
    ]
    for i,(txt,cmd) in enumerate(buttons):
        tk.Button(btns,text=txt,width=18,height=2,command=lambda c=cmd: c(root)).grid(row=i//3,column=i%3,padx=12,pady=10)

def books_window(root):
    clear(root)
    tk.Label(root,text="BOOK MANAGEMENT",font=("Arial",20,"bold")).pack(pady=12)
    form=tk.Frame(root); form.pack()
    labels=["Book ID","Title","Author","Category","Quantity"]
    entries=[]
    for i,l in enumerate(labels):
        tk.Label(form,text=l).grid(row=i,column=0,pady=5,sticky="w")
        e=tk.Entry(form,width=35); e.grid(row=i,column=1,pady=5); entries.append(e)

    listbox=tk.Listbox(root,width=115,height=13); listbox.pack(pady=15)
    def refresh():
        listbox.delete(0,tk.END)
        for b in books.find():
            listbox.insert(tk.END,f'{b["book_id"]} | {b["title"]} | {b["author"]} | {b["category"]} | Qty:{b["quantity"]} | Available:{b["available"]}')
    def add():
        try:
            bid,title,author,cat,qty=[e.get().strip() for e in entries]
            qty=int(qty)
            if not all([bid,title,author,cat]) or qty<1: raise ValueError
            if books.find_one({"book_id":bid}):
                messagebox.showerror("Error","Book ID already exists."); return
            books.insert_one({"book_id":bid,"title":title,"author":author,"category":cat,"quantity":qty,"available":qty})
            refresh()
            for e in entries:e.delete(0,tk.END)
        except ValueError:
            messagebox.showerror("Error","Enter valid book details and quantity.")
    def delete():
        s=listbox.curselection()
        if not s:return
        bid=listbox.get(s[0]).split(" | ")[0]
        if issued_books.count_documents({"book_id":bid,"status":"Issued"}):
            messagebox.showerror("Error","Cannot delete a book currently issued."); return
        books.delete_one({"book_id":bid}); refresh()
    tk.Button(form,text="Add Book",command=add,width=14).grid(row=5,column=0,pady=10)
    tk.Button(form,text="Delete Selected",command=delete,width=14).grid(row=5,column=1,pady=10,sticky="w")
    tk.Button(root,text="Back",command=lambda:dashboard(root)).pack()
    refresh()

def students_window(root):
    clear(root)
    tk.Label(root,text="STUDENT MANAGEMENT",font=("Arial",20,"bold")).pack(pady=12)
    form=tk.Frame(root); form.pack()
    labels=["Student ID","Name","Course","Phone"]
    entries=[]
    for i,l in enumerate(labels):
        tk.Label(form,text=l).grid(row=i,column=0,pady=5,sticky="w")
        e=tk.Entry(form,width=35); e.grid(row=i,column=1,pady=5); entries.append(e)
    listbox=tk.Listbox(root,width=105,height=15); listbox.pack(pady=15)
    def refresh():
        listbox.delete(0,tk.END)
        for s in students.find():
            listbox.insert(tk.END,f'{s["student_id"]} | {s["name"]} | {s["course"]} | {s["phone"]}')
    def add():
        sid,name,course,phone=[e.get().strip() for e in entries]
        if not all([sid,name,course,phone]):
            messagebox.showerror("Error","All fields are required."); return
        if students.find_one({"student_id":sid}):
            messagebox.showerror("Error","Student ID already exists."); return
        students.insert_one({"student_id":sid,"name":name,"course":course,"phone":phone})
        refresh()
        for e in entries:e.delete(0,tk.END)
    def delete():
        s=listbox.curselection()
        if not s:return
        sid=listbox.get(s[0]).split(" | ")[0]
        if issued_books.count_documents({"student_id":sid,"status":"Issued"}):
            messagebox.showerror("Error","Student has an issued book."); return
        students.delete_one({"student_id":sid}); refresh()
    tk.Button(form,text="Add Student",command=add,width=14).grid(row=4,column=0,pady=10)
    tk.Button(form,text="Delete Selected",command=delete,width=14).grid(row=4,column=1,pady=10,sticky="w")
    tk.Button(root,text="Back",command=lambda:dashboard(root)).pack()
    refresh()

def issue_window(root):
    clear(root)
    tk.Label(root,text="ISSUE / RETURN BOOK",font=("Arial",20,"bold")).pack(pady=15)
    form=tk.Frame(root); form.pack()
    tk.Label(form,text="Book ID").grid(row=0,column=0,pady=8)
    bookid=tk.Entry(form,width=30); bookid.grid(row=0,column=1)
    tk.Label(form,text="Student ID").grid(row=1,column=0,pady=8)
    sid=tk.Entry(form,width=30); sid.grid(row=1,column=1)
    listbox=tk.Listbox(root,width=110,height=15); listbox.pack(pady=15)

    def refresh():
        listbox.delete(0,tk.END)
        for x in issued_books.find():
            listbox.insert(tk.END,f'{x["_id"]} | Book:{x["book_id"]} | Student:{x["student_id"]} | Issue:{x["issue_date"]} | Due:{x["due_date"]} | Status:{x["status"]} | Fine:{x.get("fine",0)}')
    def issue():
        import datetime
        b=books.find_one({"book_id":bookid.get().strip()})
        s=students.find_one({"student_id":sid.get().strip()})
        if not b or not s: messagebox.showerror("Error","Book or student not found."); return
        if b["available"]<=0: messagebox.showerror("Error","Book is not available."); return
        if issued_books.find_one({"book_id":b["book_id"],"student_id":s["student_id"],"status":"Issued"}):
            messagebox.showerror("Error","This student already has this book."); return
        today=datetime.date.today()
        due=today+datetime.timedelta(days=14)
        issued_books.insert_one({"book_id":b["book_id"],"student_id":s["student_id"],"issue_date":str(today),"due_date":str(due),"return_date":None,"status":"Issued","fine":0})
        books.update_one({"book_id":b["book_id"]},{"$inc":{"available":-1}})
        refresh()
    def ret():
        import datetime
        sel=listbox.curselection()
        if not sel:return
        doc_id=int(listbox.get(sel[0]).split(" | ")[0])
        rec=issued_books.find_one({"_id":doc_id,"status":"Issued"})
        if not rec: return
        today=datetime.date.today()
        due=datetime.date.fromisoformat(rec["due_date"])
        fine=max(0,(today-due).days)*5
        issued_books.update_one({"_id":doc_id},{"$set":{"return_date":str(today),"status":"Returned","fine":fine}})
        books.update_one({"book_id":rec["book_id"]},{"$inc":{"available":1}})
        refresh()
        messagebox.showinfo("Returned",f"Book returned.\nFine: ₹{fine}")
    tk.Button(form,text="Issue Book",command=issue,width=15).grid(row=2,column=0,pady=10)
    tk.Button(form,text="Return Selected",command=ret,width=15).grid(row=2,column=1,pady=10,sticky="w")
    tk.Button(root,text="Back",command=lambda:dashboard(root)).pack()
    refresh()

if __name__=="__main__":
    login()
