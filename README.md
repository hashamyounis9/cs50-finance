# CS50 Finance: A Stock Portfolio Tracker
![My Finance 2024](screenshot/my_finance_2024.png)



<p>This repository contains the code for CS50's Finance problem set, a web application for managing a simulated stock portfolio. Users can track their holdings, view real-time stock prices, and buy/sell stocks (without real-money transactions).</p>

<h2>Features</h2>

<ul>
<li><strong>Portfolio Management:</strong> Users can register and create a portfolio to track their owned stocks.</li>
<li><strong>Real-Time Stock Prices:</strong> The application retrieves and displays current stock prices using an external API.</li>
<li><strong>Simulated Trading:</strong> Users can buy and sell stocks within their portfolio, updating their holdings and cash balance.</li>
<li><strong>Portfolio Valuation:</strong> The application calculates the total value of a user's portfolio based on current stock prices.</li>
</ul>

<h2>Technologies Used</h2>

<ul>
<li><strong>Backend:</strong> Flask (web framework)</li>
<li><strong>Frontend:</strong> HTML, CSS (optional styling)</li>
<li><strong>Database:</strong> SQLite (data storage for user portfolios)</li>
<li><strong>External API:</strong> IEX Cloud or Yahoo Finance (for stock price data)</li>
</ul>

<h2>Getting Started</h2>

<ol>
<li>Clone this repository:</li>
<pre><code>git clone https://github.com/hashamyounis9/cs50-finance.git</code></pre>
<li>Install dependencies:</li>
<pre><code>python3 -m venv .venv<br>source .venv/bin/activate<br>pip install -r requirements.txt</code></pre>
<li>Configure API Key:
<ul>
<li>Create an account with IEX Cloud or Yahoo Finance (depending on the chosen API).</li>
<li>Obtain your API key.</li>
<li>Create a file named api.py and store your API key securely within it.</li>
</ul>
</li>
<li>Run the application:</li>
<pre><code>export FLASK_APP=application.py<br>flask run</code></pre>
This will launch the application on http://127.0.0.1:5000/ in your web browser.
</ol>

<h2>Usage</h2>

Usage
Register: Create a new account to start tracking your portfolio.
View Portfolio: The homepage displays your owned stocks, number of shares, current price, and total value for each holding.
<p>
It also shows your remaining cash balance and the total portfolio value.
Search Stocks: Enter a stock symbol to look up its current price.
Buy/Sell Stocks: Use the provided form to simulate buying or selling shares of a stock.
Additional Notes
This application is for educational purposes and does not involve real-money transactions.
The code utilizes error handling and user input validation for a robust user experience.
Contributing
Feel free to fork this repository and contribute your improvements!

Happy coding!
* Search Stocks: Enter a stock symbol to look up its current price.
* Buy/Sell Stocks: Use the provided form to simulate buying or selling shares of a stock.
</p>

<h2>Additional Notes</h2>

<ul>
<li>This application is for educational purposes and does not involve real-money transactions.</li>
<li>The code utilizes error handling and user input validation for a robust user experience.</li>
</ul>

<h2>Contributing</h2>
<p>Feel free to fork this repository and contribute your improvements!</p>

<p>Happy coding!</p>
</body>
</html>
