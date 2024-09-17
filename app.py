from flask import Flask, render_template, request
from pulp import LpProblem, LpMinimize, LpVariable, LpStatus, value

app = Flask(__name__)

# Function to perform denomination exchange for a single location
def exchange_denominations(T, selected_denominations):
    model = LpProblem("Denomination_Exchange", LpMinimize)
    
    # Define decision variables only for selected denominations
    variables = {f'x{denom}': LpVariable(f'x{denom}', lowBound=0, cat='Integer') for denom in selected_denominations}
    
    # Objective: Minimize the total number of bills
    model += sum(variables.values()), "Total_Bills"
    
    # Constraints: Ensure the total value equals T
    total_value = sum(int(denom) * variables[f'x{denom}'] for denom in selected_denominations)
    model += total_value == T, "Total_Value"
    
    # Add constraints based on selected denominations
    add_constraints(model, variables, selected_denominations, T)
    
    # Solve the model
    model.solve()

    # Check if the solution is optimal
    if LpStatus[model.status] == 'Optimal':
        result = {f'x{denom}': int(value(variables[f'x{denom}'])) for denom in selected_denominations}
        result['total_bills'] = sum(result[f'x{denom}'] for denom in selected_denominations)
        return result
    else:
        return None

# Function to add constraints based on selected denominations
def add_constraints(model, variables, selected_denominations, T):
    if set(selected_denominations) == set(['10', '5', '2']):
        model += 10 * variables['x10'] <= 0.75 * T
        model += 10 * variables['x10'] >= 0.55 * T
        model += 5 * variables['x5'] <= 0.25 * T
        model += 5 * variables['x5'] >= 0.10 * T
        model += 2 * variables['x2'] <= 0.15 * T
        model += 2 * variables['x2'] >= 0.05 * T
    elif len(selected_denominations) == 1:
        denom_value = int(selected_denominations[0])
        model += denom_value * variables[f'x{denom_value}'] == T
    elif len(selected_denominations) == 2:
        add_two_denom_constraints(model, variables, selected_denominations, T)

# Function to handle two-denomination cases
def add_two_denom_constraints(model, variables, selected_denominations, T):
    denom_set = set(selected_denominations)
    if denom_set == set(['10', '5']):
        model += 10 * variables['x10'] <= 0.90 * T
        model += 10 * variables['x10'] >= 0.70 * T
        model += 5 * variables['x5'] <= 0.35 * T
        model += 5 * variables['x5'] >= 0.25 * T
    elif denom_set == set(['10', '2']):
        model += 10 * variables['x10'] <= 0.95 * T
        model += 10 * variables['x10'] >= 0.75 * T
        model += 2 * variables['x2'] <= 0.20 * T
        model += 2 * variables['x2'] >= 0.10 * T
    elif denom_set == set(['5', '2']):
        model += 5 * variables['x5'] <= 0.75 * T
        model += 5 * variables['x5'] >= 0.25 * T
        model += 2 * variables['x2'] <= 0.25 * T
        model += 2 * variables['x2'] >= 0.15 * T

# Home route: Input form
@app.route('/')
def index():
    return render_template('index.html')

# Route for processing the exchange
@app.route('/exchange', methods=['POST'])
def perform_exchange():
    location = request.form['location']
    amount = float(request.form['amount'])
    denominations = request.form.getlist('denominations')
    
    # Perform exchange using the existing logic
    result = exchange_denominations(amount, denominations)
    
    if result:
        total_exchanged = sum(result[f'x{denom}'] * int(denom) for denom in denominations)
        return render_template('result.html', result=result, total_exchanged=total_exchanged, location=location)
    else:
        return render_template('error.html', message="No optimal solution found")

if __name__ == "__main__":
    app.run(debug=True)
