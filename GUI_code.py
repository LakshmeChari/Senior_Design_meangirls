"""
Spyder Editor

This is an attempt to make a GUI.
"""

import tkinter as tk
from tkinter import ttk

# ================= ROOT =================
root = tk.Tk()
root.title("DC House Thermostat")
root.geometry("1200x650")
root.configure(bg="#0b0f14")
root.resizable(False, False)

# ================= COLORS =================
BG = "#0b0f14"
CARD = "#121821"
CARD_DARK = "#0f141c"
ACCENT = "#21d19f"
BLUE = "#3b82f6"
TEXT = "#e5e7eb"
MUTED = "#9ca3af"
INACTIVE = "#1f2937"
WARNING = "#facc15"

# ================= STATE =================
current_temp = tk.DoubleVar(value=22.0)
target_temp = tk.DoubleVar(value=22.0)
mode = tk.StringVar(value="Auto")
fan_state = tk.StringVar(value="OFF")
unit = tk.StringVar(value="C")
system_state = tk.StringVar(value="Idle")

# ================= CONVERSIONS =================
def c_to_f(c):
    return c * 9/5 + 32

def f_to_c(f):
    return (f - 32) * 5/9

# ================= DIAL =================
def draw_dial(temp):
    dial.delete("all")
    center, radius = 150, 110
    start, span = -210, 240

    dial.create_arc(center-radius, center-radius, center+radius, center+radius,
                    start=start, extent=span, style="arc", width=12, outline="#1f2937")

    progress = (temp-15)/15 * span
    dial.create_arc(center-radius, center-radius, center+radius, center+radius,
                    start=start, extent=progress, style="arc", width=12, outline=ACCENT)

    display_temp = temp
    symbol = "°C"
    if unit.get() == "F":
        display_temp = c_to_f(temp)
        symbol = "°F"

    dial.create_text(center, center-5,
                     text=f"{display_temp:.1f}{symbol}",
                     fill=TEXT, font=("Helvetica", 28, "bold"))

    dial.create_text(center, center+22,
                     text="CURRENT TEMPERATURE",
                     fill=MUTED, font=("Helvetica", 9))

    if abs(temp - target_temp.get()) < 0.05:
        dial.create_rectangle(center-45, center+42, center+45, center+62,
                              fill=ACCENT, outline="")
        dial.create_text(center, center+52,
                         text="AT TARGET",
                         fill="black", font=("Helvetica", 9, "bold"))

# ================= FUNCTIONS =================
def update_target_display():
    temp = target_temp.get()
    display_temp = temp
    symbol = "°C"
    if unit.get() == "F":
        display_temp = c_to_f(temp)
        symbol = "°F"
    target_label.config(text=f"{display_temp:.1f}{symbol}")

def update_target(val=None):
    target_temp.set(float(val))
    update_target_display()

def change_temp(delta):
    new = min(max(target_temp.get() + delta, 15), 30)
    target_temp.set(new)
    slider.set(new)
    update_target_display()

def set_mode(selected):
    mode.set(selected)
    auto_btn.config(bg=ACCENT if selected == "Auto" else INACTIVE,
                    fg="black" if selected == "Auto" else TEXT)
    manual_btn.config(bg=ACCENT if selected == "Manual" else INACTIVE,
                      fg="black" if selected == "Manual" else TEXT)

def toggle_fan():
    if fan_state.get() == "OFF":
        fan_state.set("ON")
        fan_button.config(bg=ACCENT, fg="black", text="ON")
    else:
        fan_state.set("OFF")
        fan_button.config(bg=INACTIVE, fg=TEXT, text="OFF")

def update_inputs(new_state):
    system_state.set(new_state)
    status_label.config(text=new_state)
    draw_dial(current_temp.get())
    root.after(100, lambda: update_inputs(system_state.get()))

# ================= LEFT CARD =================
left_card = tk.Frame(root, bg=CARD, width=380, height=520)
left_card.place(x=100, y=60)

tk.Label(left_card, text="DC House Thermostat",
         fg=MUTED, bg=CARD, font=("Helvetica", 10)).pack(pady=15)

dial = tk.Canvas(left_card, width=300, height=300,
                 bg=CARD, highlightthickness=0)
dial.pack()
draw_dial(current_temp.get())

# ---------- UNIT (NOW INSIDE LEFT CARD) ----------
tk.Label(left_card, text="TEMPERATURE UNIT",
         fg=MUTED, bg=CARD,
         font=("Helvetica", 9)).pack(pady=(15, 5))

unit_frame = tk.Frame(left_card, bg=CARD)
unit_frame.pack()

c_btn = tk.Button(unit_frame, text="°C", width=6,
                  bg=ACCENT, fg="black",
                  relief="flat",
                  command=lambda: set_unit("C"))
c_btn.pack(side="left", padx=5)

f_btn = tk.Button(unit_frame, text="°F", width=6,
                  bg=INACTIVE, fg=TEXT,
                  relief="flat",
                  command=lambda: set_unit("F"))
f_btn.pack(side="left", padx=5)

def set_unit(selected):
    unit.set(selected)
    c_btn.config(bg=ACCENT if selected == "C" else INACTIVE,
                 fg="black" if selected == "C" else TEXT)
    f_btn.config(bg=ACCENT if selected == "F" else INACTIVE,
                 fg="black" if selected == "F" else TEXT)
    update_target_display()
    draw_dial(current_temp.get())

# ================= RIGHT COLUMN =================
right_x = 480

# ---------- TARGET TEMP ----------
target_card = tk.Frame(root, bg=CARD, width=600, height=140)
target_card.place(x=right_x, y=60)

tk.Label(target_card, text="TARGET TEMPERATURE",
         fg=MUTED, bg=CARD, font=("Helvetica", 10)).place(x=20, y=15)

target_label = tk.Label(target_card,
                        fg=TEXT, bg=CARD,
                        font=("Helvetica", 28, "bold"))
target_label.place(x=250, y=40)

tk.Button(target_card, text="−", width=4, relief="flat",
          bg=INACTIVE, fg=TEXT,
          command=lambda: change_temp(-0.5)).place(x=160, y=50)

tk.Button(target_card, text="+", width=4, relief="flat",
          bg=INACTIVE, fg=TEXT,
          command=lambda: change_temp(0.5)).place(x=420, y=50)

slider = ttk.Scale(target_card, from_=15, to=30,
                   orient="horizontal", length=460,
                   command=update_target)
slider.set(22.0)
slider.place(x=70, y=100)

update_target_display()

# ---------- OPERATING MODE ----------
mode_card = tk.Frame(root, bg=CARD, width=600, height=100)
mode_card.place(x=right_x, y=220)

tk.Label(mode_card, text="OPERATING MODE",
         fg=MUTED, bg=CARD, font=("Helvetica", 10)).place(x=20, y=15)

auto_btn = tk.Button(mode_card, text="⚡ Auto", width=18, relief="flat",
                     bg=ACCENT, fg="black",
                     command=lambda: set_mode("Auto"))
auto_btn.place(x=40, y=50)

manual_btn = tk.Button(mode_card, text="⏱ Manual", width=18, relief="flat",
                       bg=INACTIVE, fg=TEXT,
                       command=lambda: set_mode("Manual"))
manual_btn.place(x=260, y=50)

# ---------- SYSTEM MODE CARD ----------
system_mode_card = tk.Frame(root, bg=CARD, width=600, height=100)
system_mode_card.place(x=480, y=340)

tk.Label(system_mode_card, text="SYSTEM MODE",
         fg=MUTED, bg=CARD, font=("Helvetica", 10)).place(x=20, y=15)

mode_buttons = []
current_system_mode = tk.StringVar(value="Heating")

for i, (label, name) in enumerate([("❄ Cooling", "Cooling"), ("☀ Heating", "Heating")]):
    def on_click(n=name):
        current_system_mode.set(n)
        for b, bname in mode_buttons:
            if bname == n:
                b.config(bg=ACCENT, fg="black")
            else:
                b.config(bg=INACTIVE, fg=TEXT)

    btn = tk.Button(system_mode_card, text=label, width=20,
                    bg=ACCENT if name == "Heating" else INACTIVE,
                    fg="black" if name == "Heating" else TEXT,
                    relief="flat",
                    command=on_click)
    btn.place(x=40 + i*220, y=50)
    mode_buttons.append((btn, name))

# ---------- FAN CARD ----------
status_y = 520

fan_card = tk.Frame(root, bg=CARD, width=250, height=90)
fan_card.place(x=540, y=status_y - 40)

tk.Label(fan_card, text="Fan",
         fg=MUTED, bg=CARD,
         font=("Helvetica", 9)).place(x=20, y=20)

fan_button = tk.Button(fan_card,
                       text="OFF",
                       width=8,
                       relief="flat",
                       bg=INACTIVE,
                       fg=TEXT,
                       command=toggle_fan)
fan_button.place(x=20, y=45)

# ---------- STATUS CARD ----------
status_card = tk.Frame(root, bg=CARD, width=250, height=90)
status_card.place(x=840, y=status_y - 40)

tk.Label(status_card, text="Status",
         fg=MUTED, bg=CARD,
         font=("Helvetica", 9)).place(x=20, y=20)

status_label = tk.Label(status_card,
                        text=system_state.get(),
                        fg=TEXT, bg=CARD,
                        font=("Helvetica", 16, "bold"))
status_label.place(x=20, y=45)

# ================= START =================
update_inputs("Idle")
root.mainloop()