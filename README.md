\# PriceSentinel: Automated E-commerce Deal Tracker

![PriceSentinel Screenshot](screenshot_01.png)

PriceSentinel is a powerful desktop application built with Python that automates the process of tracking product prices on e-commerce websites. It features a clean graphical user interface (GUI) built with Tkinter, allowing users to manage a list of products, set target prices, and receive real-time email notifications when a desired price drop is detected.

The application leverages multi-threading to run the web scraping process in the background, ensuring the UI remains responsive at all times. All tracked products and user settings are saved locally to a CSV file for data persistence across sessions.PriceSentinel is designed to be a practical, set-and-forget tool for savvy online shoppers who want to catch the best deals without constant manual checking. It's an ideal example of using Python for practical automation and web interaction.

---

### **Key Features**

* **Graphical User Interface (GUI):** A user-friendly interface built with Python's native Tkinter library to easily manage your tracking list.
* **Background Scraping:** Uses a separate thread for web scraping, so the application never freezes or becomes unresponsive while it's working.
* **Automated Email Alerts:** Configure your Gmail credentials to receive instant email notifications the moment a product's price drops to or below your target.
* **Persistent Data:** Your list of tracked products is automatically saved to a `products.csv` file, so your list is always there when you restart the application.
* **Robust Scraping:** The scraper uses custom headers and error handling to mimic a real web browser, making it more resilient to anti-bot measures.
* **Dynamic Product Management:** Easily add new product URLs and target prices, or remove items you no longer wish to track, directly from the GUI.

### **Technology Stack**

* **Language:** Python 3
* **GUI:** Tkinter
* **Web Scraping:** `requests` & `BeautifulSoup4`
* **Concurrency:** `threading` & `queue`

### **Setup & Installation**

To run this project, you'll need Python 3 installed.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Shahriyarrrrr/PriceSentinel.git](https://github.com/Shahriyarrrrr/PriceSentinel.git)
    cd PriceSentinel
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv env
    .\env\Scripts\activate
    ```

3.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

### **Usage**

1.  Run the main script:
    ```bash
    python your_main_script_name.py
    ```
2.  Use the "Add Product" button to add product URLs and your desired target prices.
3.  Fill in your email details in the "Email Alert Settings" panel. **Note:** For Gmail, you must generate and use an **App Password**.
4.  Click "Start Scraper" to begin tracking. Logs will appear in the text box in real time.

