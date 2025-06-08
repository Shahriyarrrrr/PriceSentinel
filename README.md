# PriceSentinel: Automated E-commerce Deal Tracker

PriceSentinel is a powerful desktop application built with Python that automates the process of tracking product prices on e-commerce websites. It features a clean graphical user interface (GUI) built with Tkinter, allowing users to manage a list of products, set target prices, and receive real-time email notifications when a desired price drop is detected.

The application leverages multi-threading to run the web scraping process in the background, ensuring the UI remains responsive at all times. All tracked products and user settings are saved locally to a CSV file for data persistence across sessions. PriceSentinel is designed to be a practical, set-and-forget tool for savvy online shoppers who want to catch the best deals without constant manual checking. It's an ideal example of using Python for practical automation and web interaction.

---

### Features at a Glance

| Feature | Description |
| :--- | :--- |
| **Graphical Interface** | A clean and intuitive GUI built with Tkinter for easy product management. |
| **Background Processing** | Multi-threaded architecture ensures the app never freezes while scraping. |
| **Email Notifications**| Get instant email alerts via SMTP when a product hits your target price. |
| **Data Persistence** | Your product tracking list is saved to `products.csv` and reloaded on launch. |
| **Dynamic Management** | Add or remove products to track on the fly directly through the interface. |
| **Robust Scraping** | Uses custom headers and error handling to improve success rate against anti-bot measures. |

### How It Works

1.  **Product Management**: The user adds product URLs and target prices through the GUI. This list is saved to `products.csv`.
2.  **Scraping Thread**: When the "Start" button is clicked, a separate background thread is initiated. This thread is responsible for all network activity.
3.  **Scraping Cycle**: The thread iterates through the product list, sending an HTTP request to each URL using the `requests` library.
4.  **HTML Parsing**: The returned HTML content is parsed using `BeautifulSoup4` to find the product's title and current price.
5.  **Price Comparison**: The scraped price is compared against the user's target price.
6.  **Alerting**: If the price is at or below the target, the application triggers the `smtplib` module to send a deal alert email to the configured recipient.
7.  **Logging**: All actions, successes, and errors are reported back to the main GUI thread via a thread-safe queue and displayed in the log window.

### Technology Stack

* **Language:** Python 3
* **GUI:** Tkinter
* **Web Scraping:** `requests` & `BeautifulSoup4`
* **Concurrency:** `threading` & `queue`
* **Email:** `smtplib` & `ssl`

### Setup & Installation

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

### Usage

1.  Run the main script from your terminal:
    ```bash
    python your_main_script_name.py
    ```
2.  Use the **"Add Product"** button to add product URLs and your desired target prices.
3.  Fill in your email details in the **"Email Alert Settings"** panel. **Note:** For Gmail, you must generate and use an **App Password**.
4.  Click **"Start Scraper"** to begin tracking. Logs will appear in the text box in real time.

### License

This project is licensed under the MIT License. See the `LICENSE` file for details.
