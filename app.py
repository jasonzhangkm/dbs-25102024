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
        amount = float(request.form[f'amount_{location}'])
        selected_denominations = request.form.getlist(f'denominations_{location}')
        
        if selected_denominations:
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
    return render_template('result.html', all_results=all_results, total_amount_exchanged=total_amount_exchanged)

if __name__ == "__main__":
    app.run(debug=True)
