import requests
from bs4 import BeautifulSoup
import time
import csv
import smtplib
import ssl
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import queue

# --- Core Scraping Logic ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1',
}

def check_price(url):
    """
    Scrapes a given product URL to find its title and price.
    This version is more robust and checks for common blocking patterns.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- Check for CAPTCHA ---
        if "api-services-support-pipeline" in response.text or "captcha" in response.text.lower():
            return None, "Request blocked by CAPTCHA. Try again later."

        # --- Find Product Title ---
        # List of possible selectors for the title
        title_selectors = ['#productTitle', 'h1.product-title', 'h1']
        title_element = None
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                break
        
        title = title_element.get_text().strip() if title_element else "Title not found"

        # --- Find Product Price ---
        # List of possible selectors for the price
        price_selectors = [
            '.a-price-whole',
            'span.a-price-whole',
            'span.price-tag',
            '.priceToPay',
            '#price'
        ]
        price_span = None
        for selector in price_selectors:
            price_span = soup.select_one(selector)
            if price_span:
                break
        
        # Extract price text
        if price_span:
             price_str = price_span.get_text().strip()
             # Some sites might include the fraction in the same element
             price_fraction = soup.select_one('.a-price-fraction')
             if price_fraction:
                 price_str += price_fraction.get_text().strip()
        else:
            return title, "Price element not found on page."
        
        # Clean and convert price
        cleaned_price = ''.join(filter(lambda char: char.isdigit() or char == '.', price_str))
        price = float(cleaned_price) if cleaned_price else None
        
        if price is None:
            return title, "Could not parse price from text."

        return title, price
        
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP Error {e.response.status_code}. The page may not exist."
    except Exception as e:
        return None, f"Error: {e}"

def send_deal_alert_email(product_title, current_price, product_url, email_config, log_queue):
    """Sends an email alert when a deal is found."""
    sender_email = email_config['sender']
    receiver_email = email_config['receiver']
    password = email_config['password']

    if not all([sender_email, receiver_email, password]):
        log_queue.put(("  - Email not sent: Please configure email settings.", "error"))
        return

    subject = f"Price Drop Alert: {product_title}"
    body = f"The price for '{product_title}' has dropped to ${current_price:.2f}!\n\nBuy it now at:\n{product_url}"
    message = f"Subject: {subject}\n\n{body}"

    try:
        log_queue.put(("  - Logging into email server...", None))
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            log_queue.put(("  - Sending email alert...", None))
            server.sendmail(sender_email, receiver_email, message)
            log_queue.put(("  - Email sent successfully!", "deal"))
    except Exception as e:
        log_queue.put((f"  - Failed to send email: {e}", "error"))


# --- GUI Application Class ---
class DealHunterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Deal-Hunter Pro")
        self.root.geometry("850x700")

        self.products_file = "products.csv"
        self.products = self.load_tracking_list()
        self.scraper_thread = None
        self.is_running = False
        self.log_queue = queue.Queue()

        self.create_widgets()
        self.populate_product_list()
        self.process_log_queue()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # --- Top Controls Frame ---
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        
        # --- Product Controls ---
        product_controls = ttk.Frame(top_frame)
        product_controls.pack(side=tk.LEFT)
        self.add_button = ttk.Button(product_controls, text="Add Product", command=self.add_product)
        self.add_button.pack(side=tk.LEFT, padx=5)
        self.remove_button = ttk.Button(product_controls, text="Remove Selected", command=self.remove_product)
        self.remove_button.pack(side=tk.LEFT, padx=5)

        # --- Scraper Control ---
        self.start_stop_button = ttk.Button(top_frame, text="Start Scraper", command=self.toggle_scraper)
        self.start_stop_button.pack(side=tk.RIGHT, padx=5)

        # --- Product List ---
        list_frame = ttk.LabelFrame(main_frame, text="Tracked Products", padding="10")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        self.tree = ttk.Treeview(list_frame, columns=("URL", "Target Price"), show="headings")
        self.tree.heading("URL", text="Product URL")
        self.tree.heading("Target Price", text="Target Price")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # --- Right Panel (Email Config & Logs) ---
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=1, column=1, sticky="ns", padx=(5, 0))
        right_panel.rowconfigure(1, weight=1)

        # --- Email Config ---
        email_frame = ttk.LabelFrame(right_panel, text="Email Alert Settings", padding="10")
        email_frame.grid(row=0, column=0, sticky="ew")
        
        ttk.Label(email_frame, text="Your Email (Sender):").grid(row=0, column=0, sticky="w", pady=2)
        self.sender_email_entry = ttk.Entry(email_frame, width=35)
        self.sender_email_entry.grid(row=1, column=0, sticky="ew")

        ttk.Label(email_frame, text="Recipient Email:").grid(row=2, column=0, sticky="w", pady=2)
        self.receiver_email_entry = ttk.Entry(email_frame, width=35)
        self.receiver_email_entry.grid(row=3, column=0, sticky="ew")

        ttk.Label(email_frame, text="Your App Password:").grid(row=4, column=0, sticky="w", pady=2)
        self.password_entry = ttk.Entry(email_frame, show="*", width=35)
        self.password_entry.grid(row=5, column=0, sticky="ew")

        # --- Log Area ---
        log_frame = ttk.LabelFrame(right_panel, text="Logs", padding="10")
        log_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, state="disabled", wrap="word", height=10)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Add tag for coloring deal alerts
        self.log_text.tag_configure("deal", foreground="green", font=("TkDefaultFont", 9, "bold"))
        self.log_text.tag_configure("error", foreground="red")

    def populate_product_list(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for i, product in enumerate(self.products):
            self.tree.insert("", tk.END, iid=i, values=(product['url'], f"${product['target_price']:.2f}"))

    def add_product(self):
        url = simpledialog.askstring("Add Product", "Enter the product URL:", parent=self.root)
        if not url: return
        try:
            target_price = simpledialog.askfloat("Add Product", "Enter the target price:", parent=self.root, minvalue=0.0)
            if target_price is None: return
            self.products.append({'url': url, 'target_price': target_price})
            self.save_tracking_list()
            self.populate_product_list()
            self.log("Product added successfully.")
        except (ValueError, TypeError):
            messagebox.showerror("Invalid Input", "Please enter a valid number for the price.")

    def remove_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a product to remove.")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to remove the selected product?"):
            item_index = self.tree.index(selected_item[0])
            del self.products[item_index]
            self.save_tracking_list()
            self.populate_product_list()
            self.log("Product removed.")

    def toggle_scraper(self):
        if self.is_running:
            self.is_running = False
            self.start_stop_button.config(text="Start Scraper")
            self.log("Scraper stopping... it will finish the current cycle.")
        else:
            if not self.products:
                messagebox.showwarning("No Products", "Please add at least one product to track.")
                return
            self.is_running = True
            self.start_stop_button.config(text="Stop Scraper")
            self.scraper_thread = threading.Thread(target=self.run_scraper_loop, daemon=True)
            self.scraper_thread.start()

    def run_scraper_loop(self):
        self.log("--- Scraper Started ---")
        email_config = {
            'sender': self.sender_email_entry.get(),
            'receiver': self.receiver_email_entry.get(),
            'password': self.password_entry.get()
        }
        while self.is_running:
            for product in list(self.products):
                if not self.is_running: break
                self.log(f"Checking: {product['url'][:50]}...")
                title, result = check_price(product['url'])
                if isinstance(result, float):
                    current_price = result
                    self.log(f"  - Price: ${current_price:.2f} | Target: ${product['target_price']:.2f}")
                    if current_price <= product['target_price']:
                        self.log(f"DEAL ALERT! Price for '{title}' is ${current_price:.2f}!", "deal")
                        send_deal_alert_email(title, current_price, product['url'], email_config, self.log_queue)
                else: # 'result' is now a descriptive error string
                    self.log(f"  - {result}", "error")
                time.sleep(5)
            if self.is_running:
                self.log("--- Cycle complete. Waiting 1 minute. ---")
                time.sleep(60)
        self.log("--- Scraper Stopped ---")

    def log(self, message, tag=None):
        self.log_queue.put((message, tag))

    def process_log_queue(self):
        try:
            while not self.log_queue.empty():
                message, tag = self.log_queue.get_nowait()
                self.log_text.config(state="normal")
                start_index = self.log_text.index(tk.END)
                self.log_text.insert(tk.END, message + "\n")
                if tag:
                    end_index = self.log_text.index(tk.END)
                    self.log_text.tag_add(tag, f"{start_index} - 1c", f"{end_index} - 1c")
                self.log_text.config(state="disabled")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_log_queue)

    def load_tracking_list(self):
        tracking_list = []
        try:
            with open(self.products_file, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if row:
                        tracking_list.append({'url': row[0], 'target_price': float(row[1])})
        except FileNotFoundError:
            pass
        return tracking_list

    def save_tracking_list(self):
        with open(self.products_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["URL", "TargetPrice"])
            for product in self.products:
                writer.writerow([product['url'], product['target_price']])
    
    def on_closing(self):
        if self.is_running:
            if messagebox.askyesno("Quit", "Scraper is running. Are you sure you want to quit?"):
                self.is_running = False
                self.root.destroy()
        else:
            self.root.destroy()

# --- Main execution block ---
if __name__ == "__main__":
    root = tk.Tk()
    app = DealHunterApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
