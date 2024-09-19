from flask import Flask, render_template, request, redirect, url_for
from pulp import LpProblem, LpMinimize, LpVariable, LpStatus, value

app = Flask(__name__)

# Function to perform denomination exchange
def exchange_denominations(T, selected_denominations):
    model = LpProblem("Denomination_Exchange", LpMinimize)
    variables = {f'x{denom}': LpVariable(f'x{denom}', lowBound=0, cat='Integer') for denom in selected_denominations}
    
    # Objective: Minimize total bills
    model += sum(variables.values()), "Total_Bills"
    
    total_value = sum(int(denom) * variables[f'x{denom}'] for denom in selected_denominations)
    model += total_value == T, "Total_Value"
    
    if '10' in selected_denominations and '5' in selected_denominations:
        model += 10 * variables['x10'] <= 0.70 * T
        model += 5 * variables['x5'] <= 0.30 * T
    
    model.solve()
    
    if LpStatus[model.status] == 'Optimal':
        return {denom: int(value(variables[f'x{denom}'])) for denom in selected_denominations}
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        locations = ['POS51', 'POS52', 'Petty Cash', 'Safe']
        denominations = ['10', '5', '2']
        all_exchanges = []
        
        for location in locations:
            amount = float(request.form.get(f'amount_{location}'))
            selected_denom = request.form.getlist(f'denom_{location}')
            result = exchange_denominations(amount, selected_denom)
            
            if result:
                all_exchanges.append({
                    'location': location,
                    'amount': amount,
                    'result': result,
                    'total_exchanged': sum(int(denom) * count for denom, count in result.items())
                })

        total_denominations = {'10': 0, '5': 0, '2': 0}
        for exchange in all_exchanges:
            for denom in total_denominations.keys():
                total_denominations[denom] += exchange['result'].get(denom, 0)
        
        total_amount_exchanged = sum(ex['total_exchanged'] for ex in all_exchanges)
        return render_template('results.html', exchanges=all_exchanges, total_amount=total_amount_exchanged, total_denominations=total_denominations)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
