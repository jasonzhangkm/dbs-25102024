from flask import Flask, render_template, request
from pulp import LpProblem, LpMinimize, LpVariable, LpStatus, value

app = Flask(__name__)

# Function to perform the optimized denomination exchange for each location
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
    if set(selected_denominations) == {'10', '5', '2'}:
        model += 10 * variables['x10'] <= 0.70 * T
        model += 10 * variables['x10'] >= 0.60 * T
        model += 5 * variables['x5'] <= 0.32 * T
        model += 5 * variables['x5'] >= 0.22 * T
        model += 2 * variables['x2'] <= 0.18 * T
        model += 2 * variables['x2'] >= 0.08 * T
    elif len(selected_denominations) == 1:
        denom_value = int(selected_denominations[0])
        model += denom_value * variables[f'x{denom_value}'] == T
    elif len(selected_denominations) == 2:
        add_two_denom_constraints(model, variables, selected_denominations, T)

    # Solve the model
    model.solve()

    # Check if the solution is optimal
    if LpStatus[model.status] == 'Optimal':
        result = {f'x{denom}': int(value(variables[f'x{denom}'])) for denom in selected_denominations}
        return result
    else:
        return None

# Helper function for two-denomination cases
def add_two_denom_constraints(model, variables, selected_denominations, T):
    denom_set = set(selected_denominations)
    if denom_set == {'10', '5'}:
        model += 10 * variables['x10'] <= 0.80 * T
        model += 10 * variables['x10'] >= 0.70 * T
        model += 5 * variables['x5'] <= 0.30 * T
        model += 5 * variables['x5'] >= 0.20 * T
    elif denom_set == {'10', '2'}:
        model += 10 * variables['x10'] <= 0.90 * T
        model += 10 * variables['x10'] >= 0.80 * T
        model += 2 * variables['x2'] <= 0.20 * T
        model += 2 * variables['x2'] >= 0.10 * T
    elif denom_set == {'5', '2'}:
        model += 5 * variables['x5'] <= 0.75 * T
        model += 5 * variables['x5'] >= 0.65 * T
        model += 2 * variables['x2'] <= 0.35 * T
        model += 2 * variables['x2'] >= 0.25 * T

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Input amounts for each location
            pos51_amount = float(request.form['pos51_amount'])
            pos52_amount = float(request.form['pos52_amount'])
            petty_cash_amount = float(request.form['petty_cash_amount'])
            safe_amount = float(request.form['safe_amount'])

            # Input selected denominations for each location
            pos51_denom = request.form.getlist('pos51_denom')
            pos52_denom = request.form.getlist('pos52_denom')
            petty_cash_denom = request.form.getlist('petty_cash_denom')
            safe_denom = request.form.getlist('safe_denom')

            all_results = []
            total_amount_exchanged = 0
            final_summary = {"10": 0, "5": 0, "2": 0}

            # Perform the denomination exchange for each location
            for location, amount, denom in [
                ("POS51", pos51_amount, pos51_denom),
                ("POS52", pos52_amount, pos52_denom),
                ("Petty Cash", petty_cash_amount, petty_cash_denom),
                ("Safe", safe_amount, safe_denom)
            ]:
                result = exchange_denominations(amount, denom)
                if result:
                    total_exchanged = sum(result[f'x{d}'] * int(d) for d in denom)
                    all_results.append({"location": location, **result, "total_exchanged": total_exchanged})
                    total_amount_exchanged += total_exchanged
                    for d in denom:
                        final_summary[d] += result[f'x{d}']
                else:
                    raise ValueError(f"No optimal solution found for {location} with amount {amount}.")

            return render_template('results.html', all_results=all_results, total_amount_exchanged=total_amount_exchanged, final_summary=final_summary)

        except Exception as e:
            return f"An error occurred: {e}"

    return render_template('index.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
