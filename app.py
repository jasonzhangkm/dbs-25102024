from flask import Flask, render_template, request
from pulp import LpProblem, LpMinimize, LpVariable, LpStatus, value

app = Flask(__name__)

def exchange_denominations(T, selected_denominations):
    model = LpProblem("Denomination_Exchange", LpMinimize)

    variables = {f'x{denom}': LpVariable(f'x{denom}', lowBound=0, cat='Integer') for denom in selected_denominations}

    model += sum(variables.values()), "Total_Bills"
    total_value = sum(int(denom) * variables[f'x{denom}'] for denom in selected_denominations)
    model += total_value == T, "Total_Value"

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

    model.solve()

    if LpStatus[model.status] == 'Optimal':
        result = {denom: int(value(variables[f'x{denom}'])) for denom in selected_denominations}
        result['total_bills'] = sum(result[denom] for denom in selected_denominations)
        return result
    else:
        return None

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
        all_results = []
        locations = ['pos51', 'pos52', 'petty_cash', 'safe']
        total_summary = {'10': 0, '5': 0, '2': 0}
        total_amount_exchanged = 0

        # Loop through each location
        for location in locations:
            amount_key = f'{location}_amount'
            denom_key = f'{location}_denom'
            amount = int(request.form[amount_key])
            selected_denoms = request.form.getlist(denom_key)

            # Create the PuLP optimization model
            problem = LpProblem('Denomination_Exchange', LpMinimize)
            # Variables for each denomination type
            ten_bills = LpVariable('ten_bills', lowBound=0, cat='Integer')
            five_bills = LpVariable('five_bills', lowBound=0, cat='Integer')
            two_bills = LpVariable('two_bills', lowBound=0, cat='Integer')

            # Define the objective function (minimize total number of bills)
            problem += ten_bills + five_bills + two_bills, 'Total_Bills'

            # Constraints for selected denominations
            constraints = []
            if '10' in selected_denoms:
                constraints.append(ten_bills * 10)
            if '5' in selected_denoms:
                constraints.append(five_bills * 5)
            if '2' in selected_denoms:
                constraints.append(two_bills * 2)

            if constraints:
                problem += lpSum(constraints) == amount

            # Solve the optimization problem
            problem.solve()

            # Extract results and calculate the total exchanged for each location
            result = {
                'location': location.upper().replace('_', ' '),
                'amount': amount,
                '10': int(value(ten_bills)),
                '5': int(value(five_bills)),
                '2': int(value(two_bills)),
                'total_exchanged': (int(value(ten_bills)) * 10) +
                                   (int(value(five_bills)) * 5) +
                                   (int(value(two_bills)) * 2)
            }
            all_results.append(result)

            # Update the final summary
            total_summary['10'] += result['10']
            total_summary['5'] += result['5']
            total_summary['2'] += result['2']
            total_amount_exchanged += result['total_exchanged']

        # Render the results.html with the calculated values
        return render_template('results.html', 
                               all_results=all_results, 
                               final_summary=total_summary, 
                               total_amount_exchanged=total_amount_exchanged)
    
    # If GET request, show the index form
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
