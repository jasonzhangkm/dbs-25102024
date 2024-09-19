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

# Function to handle two-denomination cases
def add_two_denom_constraints(model, variables, selected_denominations, T):
    denom_set = set(selected_denominations)
    if denom_set == set(['10', '5']):
        model += 10 * variables['x10'] <= 0.80 * T
        model += 10 * variables['x10'] >= 0.70 * T
        model += 5 * variables['x5'] <= 0.30 * T
        model += 5 * variables['x5'] >= 0.20 * T
    elif denom_set == set(['10', '2']):
        model += 10 * variables['x10'] <= 0.90 * T
        model += 10 * variables['x10'] >= 0.80 * T
        model += 2 * variables['x2'] <= 0.20 * T
        model += 2 * variables['x2'] >= 0.10 * T
    elif denom_set == set(['5', '2']):
        model += 5 * variables['x5'] <= 0.75 * T
        model += 5 * variables['x5'] >= 0.65 * T
        model += 2 * variables['x2'] <= 0.35 * T
        model += 2 * variables['x2'] >= 0.25 * T

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            locations = ['POS51', 'POS52', 'Petty_Cash', 'Safe']
            all_results = []
            total_amount_exchanged = 0
            final_summary = {'10': 0, '5': 0, '2': 0}

            # Loop through each location and perform the exchange
            for location in locations:
                amount = float(request.form.get(f'amount_{location}'))
                selected_denom = request.form.getlist(f'denom_{location}')
                
                # Validate amount and denomination selection
                if not amount or not selected_denom:
                    raise ValueError(f"Invalid input for {location}: amount={amount}, selected_denom={selected_denom}")
                
                # Only proceed with the exchange if there is at least one denomination selected
                if len(selected_denom) == 0:
                    raise ValueError(f"No denominations selected for {location}. Please select at least one.")

                # Perform the exchange
                result = exchange_denominations(amount, selected_denom)
                if result:
                    total_exchanged = 0
                    for denom in selected_denom:
                        count = result[f'x{denom}']
                        value = count * int(denom)
                        total_exchanged += value
                        final_summary[denom] += count

                    all_results.append({
                        "location": location,
                        "amount": amount,
                        "result": result,
                        "total_exchanged": total_exchanged
                    })
                    total_amount_exchanged += total_exchanged
                else:
                    raise ValueError(f"No optimal solution found for {location}.")

            return render_template('results.html', all_results=all_results, total_amount_exchanged=total_amount_exchanged, final_summary=final_summary)

        except ValueError as e:
            return f"An error occurred: {e}"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
