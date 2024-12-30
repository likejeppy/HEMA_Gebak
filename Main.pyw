import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter import messagebox, Toplevel
from PIL import Image, ImageTk
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
import json
import logging
import os

# Configure logging
logging.basicConfig(
    filename="app.log",  # Log file name
    level=logging.DEBUG,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    datefmt="%d-%m-%Y %H:%M:%S",  # Date format
)

logging.info("*******************************************************************************************************")
logging.info("Loading application.")

# Dictionary to store article numbers, names, and values
saved_articles = {}
order_articles = {}  # New dictionary to store articles added to the order
total_value = 0

# Get the directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Config file path relative to the script
config_file = os.path.join(base_dir, "config.json")

# Default configuration
logging.info("Setting default config values.")
default_config = {
    "main_file_path": None,
    "main_window_position": (686, 350),
    "order_window_position": (686, 350),
    "add_article_window_position": (686, 350)
}

def load_config():
    logging.info("Performing function 'load_config'.")
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

    if os.path.exists(config_file):
        logging.info("Config file found, loading it.")
        try:
            with open(config_file, "r") as f:
                if os.path.getsize(config_file) == 0:  # Check if the file is empty
                    logging.warning("Config file is empty, returning default configuration.")
                    return {}
                return json.load(f)
        except json.JSONDecodeError:
            logging.error("Config file is invalid JSON, returning default configuration.")
            return {}
    else:
        logging.warning("Config file does not exist, returning default configuration.")
        return {}


def save_config(config):
    logging.info("Performing function 'save_config'.")
    try:
        # Convert absolute path to relative path
        if "main_file_path" in config and config["main_file_path"] is not None:
            config["main_file_path"] = os.path.relpath(config["main_file_path"],
                                                       start=os.path.dirname(os.path.abspath(__file__)))

        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
            logging.info(f"Config file saved successfully at: {config_file}")
    except Exception as e:
        logging.error(f"Error saving config file at {config_file}: {e}")

# Save the dictionary to a JSON file
def save_articles():
    logging.info("Performing function 'save_articles'.")
    # Sort the dictionary by article name (keys) before saving
    sorted_articles = dict(sorted(saved_articles.items()))


    try:
        # Read the existing content
        with open("saved_articles.json", "r") as file:
            existing_data = json.load(file)
            logging.info("Successfully found existing data in 'saved_articles.json'.")
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty, start with an empty dictionary
        existing_data = {}
        logging.debug("Couldn't find existing data, returning empty.")

    # Update the existing data with the new sorted articles
    existing_data.update(sorted_articles)

    # Write the updated data back to the file
    with open("saved_articles.json", "w") as file:
        json.dump(existing_data, file, indent=4)
        logging.info("Successfully saved data to 'saved_articles.json'.")


# Load the dictionary from the JSON file
def load_articles():
    logging.info("Performing function 'load_articles'.")
    global saved_articles
    try:
        with open("saved_articles.json", "r") as file:
            saved_articles = json.load(file)
            logging.info("Successfully loaded content file.")
    except FileNotFoundError:
        saved_articles = {}  # If the file doesn't exist, initialize with an empty dictionary
        logging.debug("Couldn't find existing data, initializing with empty dictionary.")

# Function to populate Listbox with loaded data
def populate_listbox(listbox):
    logging.info("Performing function 'populate_listbox'.")
    # Populate the Listbox with the article names and values (sorted alphabetically, case-insensitive)
    listbox.delete(0, tk.END)  # Clear existing entries in the listbox

    # Sort the articles alphabetically in a case-insensitive manner
    for article_name in sorted(saved_articles, key=lambda x: x.strip().lower()):
        article_value = saved_articles[article_name]["value"]
        listbox.insert(tk.END, f"{article_name} - €{article_value}")


def update_listbox(search_term=""):
    """
    Update the listbox to show items matching the search term, sorted alphabetically.
    """
    saved_listbox.delete(0, tk.END)  # Clear existing entries in the listbox

    # Create a list of articles that match the search term, including their values
    matching_items = [f"{article_name} - €{saved_articles[article_name]['value']}"
                      for article_name in saved_articles
                      if search_term.lower() in article_name.lower()]

    # Sort the matching items alphabetically (case-insensitive)
    matching_items.sort(key=lambda x: x.split(" - ")[0].strip().lower())

    # Insert the sorted items into the listbox
    for item in matching_items:
        saved_listbox.insert(tk.END, item)



def on_search(*args):
    logging.info("Performing function 'on_search'.")
    """
    Callback function for search entry changes.
    """
    search_term = search_var.get()
    update_listbox(search_term)
    logging.info(f"Searching for: {search_term}.")

def generate_barcode(window, entry_number, entry_name, entry_value, barcode_label, value_label):
    logging.info("Performing function 'generate_barcode'.")
    article_number = entry_number.get()
    article_name = entry_name.get()
    article_value = entry_value.get()
    global saved_articles
    if not article_number.isdigit():
        messagebox.showerror("Ongeldige invoer", "Artikelnummer mag alleen nummers bevatten.")
        logging.error("Invalid input for article number in function.")
        return
    if not article_name:
        messagebox.showerror("Ongeldige Invoer", "Artikel moet een naam hebben.")
        logging.error("Invalid input for article name in function.")
        return
    if not article_value.replace('.', '', 1).isdigit():
        messagebox.showerror("Ongeldige Invoer", "Artikelwaarde mag alleen nummers bevatten.")
        logging.error("Invalid input for article value in function'.")
        return

    try:
        logging.info("Trying to generate barcode.")
        # Generate barcode with Code128 format
        barcode = Code128(article_number, writer=ImageWriter())
        buffer = BytesIO()
        barcode.write(buffer)
        buffer.seek(0)

        # Load barcode into Tkinter
        image = Image.open(buffer)
        photo = ImageTk.PhotoImage(image)

        # Display the barcode
        barcode_label.config(image=photo)
        barcode_label.image = photo

        # Save article (store article number and value)
        saved_articles[article_name] = {
            "number": int(article_number),
            "value": float(article_value),
        }

        save_articles()  # Save after generating barcode
        clear_contents()

        # Update the value label at the top
        value_label.config(text=f"Prijs: €{article_value}", fg="green")
        logging.info(f"Successfully generated barcode with article: {article_name} with number: {article_number} and value: {article_value}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate barcode: {e}")
        logging.error(f"Failed to generate barcode: {e}")

def generate_barcode_from_listbox(event, listbox, barcode_label, value_label):
    logging.info("Perofrming function 'generate_barcode_from_listbox'.")
    # Get the selected article name from the listbox
    selected_item_index = listbox.curselection()
    if not selected_item_index:
        messagebox.showerror("Geen Artikel Geselecteerd", "Selecteer eerst een artikel van de lijst.")
        logging.error("Geen artikel geselecteerd.")
        return

    # Get the article name and details
    article_name = listbox.get(selected_item_index).split(' - ')[0]
    article_number = saved_articles[article_name]["number"]
    article_value = saved_articles[article_name]["value"]

    # Generate the barcode
    logging.info(f"Trying to generate barcode for article: {article_name}, with number: {article_number} and value: {article_value}.")
    generate_barcode_directly(article_number, article_value, barcode_label, value_label)


def generate_barcode_directly(article_number, article_value, barcode_label, value_label=None):
    logging.info("Performing function 'generate_barcode_directly'.")
    try:
        # Generate barcode with Code128 format
        barcode = Code128(str(article_number), writer=ImageWriter())
        buffer = BytesIO()
        barcode.write(buffer)
        buffer.seek(0)

        # Load barcode into Tkinter
        image = Image.open(buffer)
        photo = ImageTk.PhotoImage(image)

        # Display the barcode
        barcode_label.config(image=photo)
        barcode_label.image = photo

        # Update the value label at the top
        if value_label:
            value_label.config(text=f"Prijs: €{article_value}", fg="green")
        logging.info(f"Successfully generated barcode for article number: {article_number} with value: {article_value}.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate barcode: {e}")
        logging.error(f"Failed to generate barcode: {e}")


def add_to_order(listbox, order_listbox, total_value_label):
    logging.info("Performing function 'add_to_order'.")
    # Get the selected article name from the listbox
    global total_value, order_articles
    selected_item_index = listbox.curselection()

    if not selected_item_index:
        messagebox.showerror("Geen Artikel Geselecteerd", "Selecteer eerst een artikel van de lijst.")
        logging.error("Geen artikel geselecteerd.")
        return

    # Get the article name from the listbox
    article_name = listbox.get(selected_item_index).split(' - ')[0]

    article_value = saved_articles[article_name]["value"]
    total_value += article_value  # Add the selected article's value to the total
    order_articles[article_name] = saved_articles[article_name]  # Add to order

    try:
        total_value_label.config(text=f"Totale waarde: {total_value}")

        # Populate the order listbox with the updated order (article name and value)
        populate_order_listbox(order_listbox)

        logging.info(f"Trying to add item: {article_name} with value: {article_value} to order.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to update total value: {e}")
        logging.error(f"Failed to update total value: {e}")

def remove_from_order(order_listbox, total_value_label):
    logging.info("Performing function 'remove_from_order'.")
    global total_value, order_articles
    selected_item_index = order_listbox.curselection()

    if not selected_item_index:
        messagebox.showerror("Geen Artikel Geselecteerd", "Selecteer eerst een artikel om te verwijderen van het pakket.")
        logging.error("Geen artikel geselecteerd.")
        return

    # Get the article name from the order listbox
    article_name = order_listbox.get(selected_item_index).split(' - ')[0]

    # Remove the selected item from the order and update the total
    article_value = order_articles[article_name]["value"]
    total_value -= article_value  # Subtract the article's value from the total
    del order_articles[article_name]  # Remove from order

    try:
        total_value_label.config(text=f"Totale waarde: {total_value}")

        # Populate the order listbox with the updated order (article name and value)
        populate_order_listbox(order_listbox)

        logging.info(f"Trying to remove: {article_name} with value: {article_value} from order.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to update total value: {e}")
        logging.error(f"Failed to update total value: {e}")

def populate_order_listbox(order_listbox):
    logging.info("Performing function 'populate_order_listbox'.")
    # Populate the Listbox with the articles in the order and their values
    order_listbox.delete(0, tk.END)  # Clear existing entries in the listbox
    for article_name, article_info in order_articles.items():
        article_value = article_info["value"]
        order_listbox.insert(tk.END, f"{article_name} - {article_value}")

# Declare the Entry widgets as global
def clear_contents():
    logging.info("Performing function 'clear_contents'.")
    entry_name.delete(0, tk.END)
    entry_value.delete(0, tk.END)
    entry_number.delete(0, tk.END)
    entry_name.focus()

# Add New Article Window (Barcode Generation)
def add_article_window():
    logging.info("Performing function and creating window 'add_article_window'.")
    global entry_name, entry_value, entry_number  # Make them global
    add_article_window = Toplevel()
    add_article_window.title("Add New Article")
    add_article_window.resizable(False, False)
    add_article_window.minsize(200,0)

    add_article_window.grab_set()
    add_article_window.lift()

    # Focus force
    add_article_window.focus_force()

    # Retrieve saved window position, default to root coordinates
    add_article_window_position = config.get('add_article_window_position', (root.winfo_x(), root.winfo_y()))
    add_article_window.geometry(f"+{add_article_window_position[0]}+{add_article_window_position[1]}")

    # UI Elements for the Add New Article window
    label_name = tk.Label(add_article_window, text="Naam:")
    label_name.pack(pady=5, padx=5)

    entry_name = tk.Entry(add_article_window, width=30)
    entry_name.pack(pady=5, padx=5)

    label_number = tk.Label(add_article_window, text="Artikelnummer:")
    label_number.pack(pady=5, padx=5)

    entry_number = tk.Entry(add_article_window, width=30)
    entry_number.pack(pady=5, padx=5)

    label_value = tk.Label(add_article_window, text="Prijs:")
    label_value.pack(pady=5, padx=5)

    entry_value = tk.Entry(add_article_window, width=30)
    entry_value.pack(pady=5, padx=5)

    barcode_label = tk.Label(add_article_window)
    barcode_label.pack(pady=10, padx=5)

    value_label = tk.Label(add_article_window, text="Prijs: €0.00", font=("Helvetica", 14), fg="green")
    value_label.pack(pady=5, padx=5)

    button_generate = tk.Button(add_article_window, text="Voeg Artikel Toe",
                                command=lambda: generate_barcode(add_article_window, entry_number, entry_name, entry_value,
                                                                 barcode_label, value_label))
    button_generate.pack(pady=10, padx=5)

    # Bind the Enter key to trigger the button function
    add_article_window.bind('<Return>', lambda event: generate_barcode(add_article_window, entry_number, entry_name, entry_value,
                                                               barcode_label, value_label))


    add_article_window.focus()
    entry_name.focus()

    # Function to capture the position before closing
    def save_window_position(event):
        logging.info("Performing function 'save_window_position'.")
        add_article_window_position = add_article_window.winfo_x(), add_article_window.winfo_y()
        config['add_article_window_position'] = add_article_window_position

    # Bind the close event to save the window position
    logging.info("Closing window 'add_article_window'.")
    add_article_window.protocol("WM_DELETE_WINDOW", lambda: (save_window_position(None), add_article_window.destroy()))

    root.wait_window(add_article_window)
    root.deiconify()


def make_order_window():
    logging.info("Performing function and creating window 'make_order_window'.")
    order_window = tk.Toplevel(root)
    order_window.title("Make Order")
    order_window.resizable(False, False)
    order_window.minsize(200,0)
    order_window.maxsize(999,999)

    order_window.grab_set()
    order_window.lift()

    # Focus force
    order_window.focus_force()

    # Retrieve saved window position, default to root coordinates
    order_window_position = config.get('order_window_position', (root.winfo_x(), root.winfo_y()))
    order_window.geometry(f"+{order_window_position[0]}+{order_window_position[1]}")

    label_saved = tk.Label(order_window, text="Zoeken:", font=("Helvetica", 11))
    label_saved.pack(pady=5, padx=5)

    # Create a frame to hold the search entry and the clear button
    search_frame = tk.Frame(order_window)
    search_frame.pack(pady=5)

    # Search variable and entry
    global search_var
    search_var = tk.StringVar()
    search_var.trace_add("write", on_search)

    search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Helvetica", 14))
    search_entry.pack(side="left", padx=5)

    # Function to clear the search entry and reset the listbox
    def clear_search():
        logging.info("Performing function 'clear_search'.")
        search_var.set("")  # Reset the search box
        update_listbox()  # Reset the listbox to show all items

    # Clear button
    clear_button = tk.Button(search_frame, text="X", command=clear_search, font=("Helvetica", 9, "bold"))
    clear_button.pack(side="left", padx=5)

    barcode_label = tk.Label(order_window)
    barcode_label.pack(pady=10, padx=5)

    # Listbox for saved articles
    global saved_listbox
    saved_listbox = tk.Listbox(order_window, width=40, height=10, font=("Helvetica", 12),
                               bg="#f0f0f0", selectmode=tk.SINGLE, bd=1, relief="sunken", activestyle="none")

    # Create a scrollbar for the Listbox
    scrollbar = tk.Scrollbar(order_window, orient="vertical", command=saved_listbox.yview)
    saved_listbox.config(yscrollcommand=scrollbar.set)

    # Pack scrollbar and listbox
    scrollbar.pack(side="right", fill="y")
    saved_listbox.pack(pady=5, padx=5)

    # Hover effect for listbox items
    def on_listbox_hover(event):
        index = saved_listbox.nearest(event.y)  # Get the nearest index based on mouse position
        saved_listbox.itemconfig(index, {'bg': '#d3d3d3'})  # Change background color on hover

    def on_listbox_leave(event):
        index = saved_listbox.nearest(event.y)
        saved_listbox.itemconfig(index, {'bg': '#f0f0f0'})  # Reset background color when mouse leaves

    saved_listbox.bind("<Motion>", on_listbox_hover)  # Hover effect when moving the mouse
    saved_listbox.bind("<Leave>", on_listbox_leave)  # Reset background when mouse leaves

    # Highlight the selected item
    def highlight_selected(event):
        selected_index = saved_listbox.curselection()  # Get the index of the selected item
        for i in range(len(saved_listbox.get(0, tk.END))):
            if i == selected_index[0]:
                saved_listbox.itemconfig(i, {'bg': '#87CEEB'})  # Highlight selected item
            else:
                saved_listbox.itemconfig(i, {'bg': '#f0f0f0'})  # Reset the background of unselected items

    saved_listbox.bind("<<ListboxSelect>>", highlight_selected)

    # Add tooltips to the listbox items
    def show_tooltip(event):
        index = saved_listbox.nearest(event.y)
        article_name = saved_listbox.get(index).split(" - ")[0]
        tooltip = ttk.Tooltip(saved_listbox, text=f"Details for {article_name}")
        tooltip.place(x=event.x, y=event.y)

    saved_listbox.bind("<Motion>", show_tooltip)

    # Binding the action to the listbox selection
    saved_listbox.bind("<<ListboxSelect>>",
                       lambda event: generate_barcode_from_listbox(event, saved_listbox, barcode_label, value_label))

    generate_barcode_directly("15160043", "0", barcode_label)

    # Greyed out are element that are made for adding items to order, is in development.
    #button_add_to_order = tk.Button(order_window, text="Voeg Toe", state="disabled",
                                    #command=lambda: add_to_order(saved_listbox, order_listbox, total_value_label))
    #button_add_to_order.pack(pady=10, padx=5)

    #button_remove_from_order = tk.Button(order_window, text="Verwijder", state="disabled",
                                         #command=lambda: remove_from_order(order_listbox, total_value_label))
    #button_remove_from_order.pack(pady=10, padx=5)

    value_label = tk.Label(order_window, text="Prijs: €0.00", font=("Helvetica", 14), fg="green")
    value_label.pack(pady=5, padx=5)

    #total_value_label = tk.Label(order_window, text="Totale waarde: €0.00", font=("Helvetica", 14), fg="green")
    #total_value_label.pack(pady=5, padx=5)

    load_articles()
    populate_listbox(saved_listbox)
    update_listbox()

    # Listbox for the current order
    #order_listbox = tk.Listbox(order_window, width=40, height=10, state="disabled")
    #order_listbox.pack(pady=5, padx=5)

    order_window.grab_set()

    # Function to capture the position before closing
    def save_window_position(event):
        logging.info("Performing function 'save_window_position'.")
        order_window_position = order_window.winfo_x(), order_window.winfo_y()
        config['order_window_position'] = order_window_position

    logging.info("Closing window 'make_order_window'.")
    # Bind the close event to save the window position
    order_window.protocol("WM_DELETE_WINDOW", lambda: (save_window_position(None), order_window.destroy()))
    root.wait_window(order_window)
    root.deiconify()

# Main Window for choosing actions
# Create the main window
logging.info("Creating main window")
root = tk.Tk()
root.title("HEMA Gebak - jeffvh")
root.resizable(False, False)
config = load_config()
root.minsize(200, 0)

main_window_position = config.get('main_window_position', (686, 350))  # Default to (100, 100)
root.geometry(f"+{main_window_position[0]}+{main_window_position[1]}")

# Button to open the "Add New Article" window
def open_add_article():
    logging.info("Performing function 'open_add_article'.")
    root.withdraw()
    add_article_window()

# Button to open the "Make Order" window
def open_make_order():
    logging.info("Performing function 'open_make_order'.")
    root.withdraw()
    make_order_window()

button_add_article = tk.Button(root, text="Voeg Nieuwe Taart Toe", width=20, command=open_add_article, state="normal")
button_add_article.pack(pady=5, padx=0)

button_make_order = tk.Button(root, text="Zoek Artikenummer", width=20, command=open_make_order, state="normal")
button_make_order.pack(pady=20, padx=5)

def on_close():
    logging.info("Performing function 'on_close'.")
    main_window_position = (root.winfo_x(), root.winfo_y())
    config['main_window_position'] = main_window_position
    save_config(config)
    logging.info("Successfully performed function 'on_close'.")
    logging.info(
        "Closing application...")  # Last log entry
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# Run the main window
root.mainloop()
    # Populate the listbox with saved articles
