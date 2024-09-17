from flask import Flask, render_template, request
from pulp import LpProblem, LpMinimize, LpVariable, LpStatus, value

app = Flask(__name__)

# Exchange logic (using your existing functions)
# Same as before: exchange_denominations, add_constraints, add_two_denom_constraints

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perform_exchange', methods=['POST'])
def perform_exchange():
    locations = ['POS51', 'POS52', 'Petty Cash', 'Safe']
    all_results = []
    total_amount_exchanged = 0

    for location in locations:
        # Check if the amount is provided for the location
        amount_input = request.form.get(f'amount_{location}')
        if not amount_input:
            continue  # Skip this location if no amount is entered

        amount = float(amount_input)
        selected_denominations = request.form.getlist(f'denominations_{location}')
        
        # Check if any denomination was selected
        if not selected_denominations:
            continue  # Skip this location if no denominations are selected

        result = exchange_denominations(amount, selected_denominations)
        if result:
            total_exchanged = sum(result[f'x{denom}'] * int(denom) for denom in selected_denominations)
            all_results.append({
                'location': location,
                'result': result,
                'total_exchanged': total_exchanged
            })
            total_amount_exchanged += total_exchanged

    # Generate a summary after all locations have been processed
    if all_results:
        return render_template('result.html', all_results=all_results, total_amount_exchanged=total_amount_exchanged)
    else:
        # If no results, display an error page
        return render_template('error.html', message="No valid exchanges were processed.")

if __name__ == "__main__":
    app.run(debug=True)
