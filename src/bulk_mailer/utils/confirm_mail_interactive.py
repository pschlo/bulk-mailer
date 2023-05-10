import tkinter as tk


class ConfirmMailWindow(tk.Tk):
    is_confirmed: bool | None = None

    def __init__(self, text: str, accept:str, reject:str):
        super().__init__()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.6)
        window_height = int(screen_height * 0.85)

        # # calculate the x and y positions to center the window
        # x_position = int(screen_width / 2 - window_width / 2)
        # y_position = int(screen_height / 2 - window_height / 2)

        # set the window position and size
        self.geometry(f"{window_width}x{window_height}+0+0")

        # create a text widget to display the long text
        text_widget = tk.Text(self)
        text_widget.insert(tk.END, text)
        text_widget.pack(fill="both", expand=True)

        # create a frame to hold the buttons
        button_frame = tk.Frame(self)
        button_frame.pack(fill="both", padx=30, pady=10)

        # create the accept button
        accept_button = tk.Button(button_frame, text=f"✓ {accept}", command=self.accept, padx=10)
        accept_button.pack(side="left")

        # # add space between the buttons
        # tk.Label(button_frame, text="").pack(side="left", padx=20)

        # create the reject button
        reject_button = tk.Button(button_frame, text=f"✗ {reject}", command=self.reject, padx=10)
        reject_button.pack(side="right")


    def accept(self):
        # function to execute when the accept button is clicked
        self.is_confirmed = True
        self.destroy()

    def reject(self):
        # function to execute when the reject button is clicked
        self.is_confirmed = False
        self.destroy()



def ask_send_confirmation(text: str, accept:str, reject:str) -> bool:
    root = ConfirmMailWindow(text, accept, reject)
    root.mainloop()

    if root.is_confirmed is None:
        return False
    else:
        return root.is_confirmed