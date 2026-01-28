import datetime
import sqlite3
from tkcalendar import DateEntry
from tkinter import *
import tkinter.messagebox as mb
import tkinter.ttk as ttk

# -------------------- DATABASE --------------------
connector = sqlite3.connect("ExpenseTracker.db")
cursor = connector.cursor()

connector.execute("""
CREATE TABLE IF NOT EXISTS ExpenseTracker (
    ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    Date DATETIME,
    Payee TEXT,
    Description TEXT,
    Amount FLOAT,
    ModeOfPayment TEXT
)
""")
connector.commit()

# -------------------- FUNCTIONS --------------------
def list_all_expenses():
    global table
    table.delete(*table.get_children())
    all_data = connector.execute("SELECT * FROM ExpenseTracker")
    for values in all_data.fetchall():
        table.insert("", END, values=values)

def view_expense_details():
    global table, date, payee, desc, amnt, MoP
    if not table.selection():
        mb.showerror("No expense selected", "Please select an expense to view details")
        return

    current = table.item(table.focus())
    values = current["values"]

    expense_date = datetime.date(
        int(values[1][:4]),
        int(values[1][5:7]),
        int(values[1][8:])
    )

    date.set_date(expense_date)
    payee.set(values[2])
    desc.set(values[3])
    amnt.set(values[4])
    MoP.set(values[5])

def clear_fields():
    global desc, payee, amnt, MoP, date, table
    today = datetime.datetime.now().date()
    desc.set("")
    payee.set("")
    amnt.set(0.0)
    MoP.set("Cash")
    date.set_date(today)
    table.selection_remove(*table.selection())

def remove_expense():
    if not table.selection():
        mb.showerror("No record selected", "Please select a record to delete")
        return

    current = table.item(table.focus())
    values = current["values"]

    sure = mb.askyesno(
        "Are you sure?",
        f"Are you sure you want to delete the record of {values[2]}?"
    )

    if sure:
        connector.execute(
            "DELETE FROM ExpenseTracker WHERE ID = ?", (values[0],)
        )
        connector.commit()
        list_all_expenses()
        mb.showinfo("Deleted", "Record deleted successfully")

def remove_all_expenses():
    sure = mb.askyesno(
        "Are you sure?",
        "Are you sure you want to delete all expenses?",
        icon="warning"
    )

    if sure:
        table.delete(*table.get_children())
        connector.execute("DELETE FROM ExpenseTracker")
        connector.commit()
        clear_fields()
        list_all_expenses()
        mb.showinfo("Deleted", "All expenses deleted")
    else:
        mb.showinfo("Aborted", "No expense was deleted")

def add_another_expense():
    global date, payee, desc, amnt, MoP

    if not date.get() or not payee.get() or not desc.get() or not amnt.get():
        mb.showerror("Fields empty", "Please fill all fields")
        return

    connector.execute(
        """
        INSERT INTO ExpenseTracker
        (Date, Payee, Description, Amount, ModeOfPayment)
        VALUES (?, ?, ?, ?, ?)
        """,
        (date.get_date(), payee.get(), desc.get(), amnt.get(), MoP.get())
    )
    connector.commit()

    clear_fields()
    list_all_expenses()
    mb.showinfo("Added", "Expense added successfully")

def edit_expense():
    global table

    if not table.selection():
        mb.showerror("No expense selected", "Please select an expense to edit")
        return

    view_expense_details()

    def edit_existing():
        current = table.item(table.focus())
        values = current["values"]

        connector.execute(
            """
            UPDATE ExpenseTracker
            SET Date=?, Payee=?, Description=?, Amount=?, ModeOfPayment=?
            WHERE ID=?
            """,
            (date.get_date(), payee.get(), desc.get(), amnt.get(), MoP.get(), values[0])
        )
        connector.commit()

        clear_fields()
        list_all_expenses()
        mb.showinfo("Updated", "Expense updated successfully")
        edit_btn.destroy()

    edit_btn = Button(
        data_entry_frame,
        text="Edit expense",
        font=btn_font,
        width=30,
        bg=hlb_btn_bg,
        command=edit_existing
    )
    edit_btn.place(x=10, y=395)

def selected_expense_to_words():
    if not table.selection():
        mb.showerror("No expense selected", "Please select an expense")
        return

    values = table.item(table.focus())["values"]
    message = (
        f"You paid {values[4]} to {values[2]} "
        f"for {values[3]} on {values[1]} via {values[5]}"
    )

    mb.showinfo("Expense in words", message)

# -------------------- GUI --------------------
root = Tk()
root.title("Expense Tracker")
root.geometry("1200x550")
root.resizable(0, 0)

# Colors & Fonts

dataentry_frame_bg = "#07726D"     # very light teal
buttons_frame_bg = "#B6B468"       # deep muted teal
hlb_btn_bg = "#E75094"             # soft red (Bootstrap style)

lbl_font = ("Segoe UI", 12)
entry_font = ("Segoe UI", 11)
btn_font = ("Segoe UI Semibold", 11)


Label(
    root,
    text="EXPENSE TRACKER",
    font=("Noto Sans CJK TC", 15, "bold"),
    bg=hlb_btn_bg
).pack(side=TOP, fill=X)

# Variables
desc = StringVar()
amnt = DoubleVar()
payee = StringVar()
MoP = StringVar(value="Cash")

# Frames
data_entry_frame = Frame(root, bg=dataentry_frame_bg)
data_entry_frame.place(x=0, y=30, relheight=0.95, relwidth=0.25)

buttons_frame = Frame(root, bg=buttons_frame_bg)
buttons_frame.place(relx=0.25, rely=0.05, relwidth=0.75, relheight=0.21)

tree_frame = Frame(root)
tree_frame.place(relx=0.25, rely=0.26, relwidth=0.75, relheight=0.74)

# Data Entry Widgets
Label(data_entry_frame, text="Date (M/DD/YY):", font=lbl_font, bg=dataentry_frame_bg).place(x=10, y=50)
date = DateEntry(data_entry_frame, font=entry_font)
date.place(x=160, y=50)

Label(data_entry_frame, text="Description:", font=lbl_font, bg=dataentry_frame_bg).place(x=10, y=100)
Entry(data_entry_frame, font=entry_font, width=31, textvariable=desc).place(x=10, y=130)

Label(data_entry_frame, text="Amount:", font=lbl_font, bg=dataentry_frame_bg).place(x=10, y=180)
Entry(data_entry_frame, font=entry_font, width=14, textvariable=amnt).place(x=160, y=180)

Label(data_entry_frame, text="Payee:", font=lbl_font, bg=dataentry_frame_bg).place(x=10, y=230)
Entry(data_entry_frame, font=entry_font, width=31, textvariable=payee).place(x=10, y=260)

Label(data_entry_frame, text="Mode of Payment:", font=lbl_font, bg=dataentry_frame_bg).place(x=10, y=310)
OptionMenu(
    data_entry_frame,
    MoP,
    *["Cash", "Cheque", "Credit Card", "Debit Card", "Paytm", "Google Pay", "Razorpay"]
).place(x=160, y=305)

Button(data_entry_frame, text="Add expense", font=btn_font, width=30, bg=hlb_btn_bg, command=add_another_expense).place(x=10, y=395)

# Buttons
Button(buttons_frame, text="Delete Expense", font=btn_font, width=25, bg=hlb_btn_bg, command=remove_expense).place(x=30, y=5)
Button(buttons_frame, text="Clear Fields", font=btn_font, width=25, bg=hlb_btn_bg, command=clear_fields).place(x=335, y=5)
Button(buttons_frame, text="Delete All Expenses", font=btn_font, width=25, bg=hlb_btn_bg, command=remove_all_expenses).place(x=640, y=5)
Button(buttons_frame, text="View Selected Expense", font=btn_font, width=25, bg=hlb_btn_bg, command=view_expense_details).place(x=30, y=65)
Button(buttons_frame, text="Edit Selected Expense", font=btn_font, width=25, bg=hlb_btn_bg, command=edit_expense).place(x=335, y=65)
Button(buttons_frame, text="Convert Expense to Sentence", font=btn_font, width=25, bg=hlb_btn_bg, command=selected_expense_to_words).place(x=640, y=65)

# Treeview
table = ttk.Treeview(
    tree_frame,
    columns=("ID", "Date", "Payee", "Description", "Amount", "Mode"),
    show="headings"
)

for col in ("ID", "Date", "Payee", "Description", "Amount", "Mode"):
    table.heading(col, text=col)

table.pack(fill=BOTH, expand=True)

list_all_expenses()
root.mainloop()
