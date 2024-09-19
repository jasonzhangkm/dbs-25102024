from flask import Flask, render_template, request
from pulp import LpProblem, LpMinimize, LpVariable, LpStatus, value

app = Flask(__name__)

# Function to perform denomination exchange for a single location
def exchange_denominations(T, selected_denominations):
    model = LpProblem("Denomination_Exchange", LpMinimize)
    variables = {f'x{denom}': LpVariable(f'x{denom}', lowBound=0, cat='Integer') for denom in selected_denominations}
    model += sum(variables.values()), "Total_Bills"
    total_value = sum(int(denom) * variables[f'x{denom}'] for denom in selected_denominations)
    model += total_value == T, "Total_Value"
    add_constraints(model, variables, selected_denominations, T)
    model.solve()

    if LpStatus[model.status] == 'Optimal':
        result = {f'x{denom}': int(value(variables[f'x{denom}'])) for denom in selected_denominations}
        result['total_bills'] = sum(result[f'x{denom}'] for denom in selected_denominations)
        return result
    else:
        return None

# Add constraints
def add_constraints(model, variables, selected_denominations, T):
    if set(selected_denominations) == set(['10', '5', '2']):
        model += 10 * variables['x10'] <= 0.70 * T
        model += 10 * variables['x10'] >= 0.60 * T
        model += 5 * variables['x5'] <= 0.32 * T
        model += 5 * variables['x5'] >= 0.22 * T
        model += 2 * variables['x2'] <= 0.18 * T
        model += 2 * variables['x2'] >= 0.08 * T
    # other constraints based on the denominations...

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/exchange', methods=['POST'])
def exchange():
    # Get data from form
    location = request.form['location']
    amount = float(request.form['amount'])
    selected_denominations = request.form.getlist('denominations')
    
    # Perform denomination exchange
    result = exchange_denominations(amount, selected_denominations)

    if result:
        total_exchanged = sum(int(denom) * result[f'x{denom}'] for denom in selected_denominations)
        return render_template('result.html', location=location, amount=amount, result=result, total_exchanged=total_exchanged)
    else:
        return "No optimal solution found."

if __name__ == '__main__':
    app.run(debug=True)
