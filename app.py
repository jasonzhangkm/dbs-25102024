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
        pos51_amount = float(request.form['pos51_amount'])
        pos51_denom = request.form.getlist('pos51_denom')

        pos52_amount = float(request.form['pos52_amount'])
        pos52_denom = request.form.getlist('pos52_denom')

        petty_cash_amount = float(request.form['petty_cash_amount'])
        petty_cash_denom = request.form.getlist('petty_cash_denom')

        safe_amount = float(request.form['safe_amount'])
        safe_denom = request.form.getlist('safe_denom')

        # Perform the exchange for each location
        results = {
            "POS51": exchange_denominations(pos51_amount, pos51_denom),
            "POS52": exchange_denominations(pos52_amount, pos52_denom),
            "Petty Cash": exchange_denominations(petty_cash_amount, petty_cash_denom),
            "Safe": exchange_denominations(safe_amount, safe_denom)
        }

        # Calculate final summary and total exchanged
        total_amount_exchanged = 0
        final_summary = {'10': 0, '5': 0, '2': 0}
        for location, result in results.items():
            if result:
                total_amount_exchanged += sum([int(denom) * result[denom] for denom in result.keys()])
                for denom in result.keys():
                    final_summary[denom] += result[denom]

        return render_template('result.html', all_results=results, total_amount_exchanged=total_amount_exchanged, final_summary=final_summary)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
